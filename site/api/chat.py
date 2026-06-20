"""
DigiVeritaz chatbot — Vercel Serverless Function (POST /api/chat).

Self-contained (stdlib only) so Vercel builds it cleanly as one function:
- Retrieval: lexical TF-IDF over api/kb_index.json (no DB, no embeddings cost).
- LLM: Groq primary -> Groq secondary -> Gemini fallback (never dead-ends).
- Lead capture: capture_lead tool -> forwarded to LEAD_WEBHOOK_URL (your Sheet).
- Analytics: structured JSON to stdout (Vercel function logs).
Secrets are read from environment variables only.

The pure logic lives in handle_chat(); the Vercel `handler` class and the local
dev server both call it.
"""
import os, re, json, math, time, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler

# ---------------------------------------------------------------- env loading
def _load_env():
    if os.environ.get("GROQ_API_KEY") or os.environ.get("GEMINI_API_KEY"):
        return
    here = os.path.dirname(os.path.abspath(__file__))
    for base in (os.getcwd(), here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))):
        d = base
        for _ in range(5):
            p = os.path.join(d, ".env")
            if os.path.isfile(p):
                for line in open(p, encoding="utf-8"):
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
                return
            nd = os.path.dirname(d)
            if nd == d:
                break
            d = nd

_load_env()

GROQ_KEYS    = [k for k in (os.environ.get("GROQ_API_KEY"), os.environ.get("GROQ_API_KEY_2")) if k]
GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "")
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
LEAD_WEBHOOK = os.environ.get("LEAD_WEBHOOK_URL", "")
WHATSAPP     = os.environ.get("WHATSAPP_NUMBER", "919956655662")
BOOKING_URL  = os.environ.get("BOOKING_URL", "/contact-us/")
HTTP_TIMEOUT = 8  # keep under Vercel Hobby's 10s function limit
UA = "Mozilla/5.0 (compatible; DigiVeritazBot/1.0; +https://www.digiveritaz.com)"  # Cloudflare blocks default urllib UA

# ---------------------------------------------------------------- knowledge base
_KB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kb_index.json")
_STOP = set("a an the of to for and or in on at is are be by with your you our we it this that as from will can".split())
_KB = None

def _tok(s):
    return [w for w in re.split(r"[^a-z0-9]+", s.lower()) if len(w) > 1 and w not in _STOP]

def _kb():
    global _KB
    if _KB is not None:
        return _KB
    try:
        chunks = json.load(open(_KB_PATH, encoding="utf-8")).get("chunks", [])
    except Exception:
        chunks = []
    toks, df = [], {}
    for c in chunks:
        t = _tok(c["title"] + " " + c["text"]); toks.append(t)
        for w in set(t):
            df[w] = df.get(w, 0) + 1
    n = max(1, len(chunks))
    idf = {w: math.log(1 + n / (1 + c)) for w, c in df.items()}
    _KB = {"chunks": chunks, "tokens": toks, "idf": idf}
    return _KB

def retrieve(query, k=5):
    kb = _kb()
    if not kb["chunks"]:
        return []
    q = [w for w in _tok(query) if w in kb["idf"]]
    if not q:
        return []
    scored = []
    for i, toks in enumerate(kb["tokens"]):
        if not toks:
            continue
        tf = {}
        for w in toks:
            tf[w] = tf.get(w, 0) + 1
        s = sum(tf.get(w, 0) * kb["idf"][w] for w in q)
        if s > 0:
            scored.append((s / (1 + math.log(len(toks))), i))
    scored.sort(reverse=True)
    return [kb["chunks"][i] for _, i in scored[:k]]

# ---------------------------------------------------------------- prompt + tool
SYSTEM = """You are "Veri", the AI assistant for DigiVeritaz — a Mumbai-based performance digital marketing agency (SEO, PPC, performance marketing, paid social, e-commerce, WhatsApp marketing, branding, data strategy) serving India, UAE and the UK.

YOUR JOB IS LEAD QUALIFICATION, not generic support. Behave like a sharp, friendly junior sales rep. Every conversation should move toward ONE of: (1) the visitor books a call, (2) you capture their contact details, or (3) you hand off to WhatsApp. If a chat ends without one of these, you failed.

HOW TO BEHAVE:
- Greet contextually and steer toward the visitor's goal. Ask one focused question at a time.
- Qualify conversationally — try to learn: desired service/outcome, industry (Real Estate, Automotive, Healthcare/Wellness, Education/Finance, Lifestyle/Services), rough budget or current monthly ad spend, timeline, and contact details (name, business, email, phone/WhatsApp).
- Recommend the right service and share its page link with a one-line reason, using only the CONTEXT below.
- When an industry is mentioned, cite a RELEVANT real result from CONTEXT (e.g. Zedex 200X ROAS, Shape-U 1,556 leads/month, SIWS low cost-per-lead). Never invent numbers.
- Always offer a clear next step: book a call, leave details, or WhatsApp.

HARD RULES:
- Only discuss DigiVeritaz, its services and case studies. Politely decline anything else and pivot back.
- NEVER quote or estimate specific prices — say pricing depends on scope and route them to a quick call.
- NEVER invent prices, guarantees, statistics or case-study numbers. Ground every specific claim in CONTEXT. If unsure, say so and offer a callback.
- LEAD CAPTURE WITH EMAIL VERIFICATION (two steps): collect the visitor's name, email AND phone number — all three are required before verification. Then call the send_verification tool. ONLY after the tool result confirms code_sent=true may you tell them a 6-digit code was emailed and ask them to type it here. If the tool says it failed or needs a phone, ask for the missing/valid detail and do NOT claim a code was sent. When they reply with the code, call verify_and_capture with the code plus all their details. Treat the lead as captured ONLY after verify_and_capture returns verified=true. If it fails, ask them to re-check the code, offer to resend, or hand off to WhatsApp.
- Keep replies short, confident and helpful (2-4 sentences). Use the visitor's words.
- If asked for a human, or after hours, or unsure: capture details and offer WhatsApp at +%(wa)s — never dead-end.

CONTACT: WhatsApp/phone +%(wa)s. Book a call: %(book)s
"""

_LEAD_PROPS = {
    "name": {"type": "string"}, "business": {"type": "string"},
    "email": {"type": "string"}, "phone": {"type": "string"},
    "service": {"type": "string"}, "industry": {"type": "string"},
    "budget": {"type": "string"}, "timeline": {"type": "string"},
    "notes": {"type": "string"},
}
TOOLS = [
    {"type": "function", "function": {
        "name": "send_verification",
        "description": "Email a 6-digit verification code to the visitor. REQUIRES name, email AND a valid phone number — the system rejects it without a phone. Must happen before a lead can be saved.",
        "parameters": {"type": "object",
            "properties": {"name": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"}},
            "required": ["name", "email", "phone"]},
    }},
    {"type": "function", "function": {
        "name": "verify_and_capture",
        "description": "Verify the 6-digit code the visitor typed and, if valid, save the lead. Call only after send_verification and after the visitor provides the code.",
        "parameters": {"type": "object",
            "properties": dict(_LEAD_PROPS, otp={"type": "string", "description": "the 6-digit code the visitor typed"}),
            "required": ["email", "otp"]},
    }},
]

def _wa_link():
    return "https://wa.me/" + re.sub(r"[^0-9]", "", WHATSAPP)

# ---------------------------------------------------------------- LLM transport
def _post_json(url, payload, headers):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": UA, **headers})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))

def _groq(messages, key, tools=None):
    payload = {"model": GROQ_MODEL, "messages": messages, "temperature": 0.4, "max_tokens": 700}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    data = _post_json("https://api.groq.com/openai/v1/chat/completions", payload,
                      {"Authorization": "Bearer " + key})
    return data["choices"][0]["message"]

def _gemini(messages):
    contents, sys_i = [], None
    for m in messages:
        if m["role"] == "system":
            sys_i = m["content"]; continue
        if m["role"] == "tool":
            continue
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.get("content") or ""}]})
    payload = {"contents": contents}
    if sys_i:
        payload["systemInstruction"] = {"parts": [{"text": sys_i}]}
    url = ("https://generativelanguage.googleapis.com/v1beta/models/" + GEMINI_MODEL
           + ":generateContent?key=" + urllib.parse.quote(GEMINI_KEY))
    data = _post_json(url, payload, {})
    return data["candidates"][0]["content"]["parts"][0]["text"]

# ---------------------------------------------------------------- lead + logs
def _apps_post(fields):
    """POST form-encoded fields to the Apps Script; return parsed JSON ({} on failure)."""
    if not LEAD_WEBHOOK:
        return {}
    try:
        body = urllib.parse.urlencode(fields).encode()
        req = urllib.request.Request(LEAD_WEBHOOK, data=body, method="POST", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            txt = r.read().decode("utf-8", "replace")
        try:
            return json.loads(txt)
        except Exception:
            return {"raw": txt}
    except Exception as e:
        print("APPS_POST_ERROR " + str(e))
        return {}

def _jsok():
    import random, string
    return "dv-" + "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

def _digits(s):
    return re.sub(r"[^0-9]", "", s or "")

def send_verification(args):
    """Step 1 — email a 6-digit OTP via the contact Apps Script (action=request_otp).
    The script needs a valid phone + JS token, so guard for those before calling."""
    if len(_digits(args.get("phone"))) < 10:
        print("OTP_SEND " + json.dumps({"email": args.get("email"), "ok": False, "err": "need_phone"}, ensure_ascii=False))
        return {"ok": False, "error": "need_phone"}
    res = _apps_post({"action": "request_otp", "fullname": args.get("name", ""),
                      "email": args.get("email", ""), "phone": args.get("phone", ""),
                      "_jsok": _jsok(), "_ts": str(int(time.time() * 1000) - 9000)})
    ok = bool(res.get("ok"))
    print("OTP_SEND " + json.dumps({"email": args.get("email"), "ok": ok, "err": res.get("error")}, ensure_ascii=False))
    return {"ok": ok, "error": res.get("error")}

def verify_and_capture(args):
    """Step 2 — verify the OTP and save the lead via the existing flow (action=submit_form + otp)."""
    print("LEAD " + json.dumps(dict({k: v for k, v in args.items() if v and k != "otp"}, source="website-chatbot"), ensure_ascii=False))
    extra = " | ".join(filter(None, [
        "service: " + args["service"] if args.get("service") else "",
        "industry: " + args["industry"] if args.get("industry") else "",
        "timeline: " + args["timeline"] if args.get("timeline") else "",
        "notes: " + args["notes"] if args.get("notes") else ""]))
    res = _apps_post({"action": "submit_form", "otp": args.get("otp", ""),
                      "fullname": args.get("name", ""), "email": args.get("email", ""),
                      "phone": args.get("phone", ""), "company": args.get("business", ""),
                      "budget": args.get("budget", ""),
                      "message": ("[chatbot lead] " + extra).strip(),
                      "source": "website-chatbot", "_jsok": _jsok(),
                      "_ts": str(int(time.time() * 1000) - 9000)})
    ok = bool(res.get("ok"))
    print("LEAD_VERIFY " + json.dumps({"email": args.get("email"), "ok": ok, "err": res.get("error")}, ensure_ascii=False))
    return {"ok": ok, "error": res.get("error")}

def log_event(**kw):
    print("ANALYTICS " + json.dumps(kw, ensure_ascii=False))

# ---------------------------------------------------------------- main entry
def handle_chat(payload):
    msgs_in = (payload.get("messages") or [])[-12:]
    page = payload.get("page", "")
    user_last = next((m.get("content", "") for m in reversed(msgs_in) if m.get("role") == "user"), "")

    ctx = retrieve((user_last + " " + page).strip(), k=5)
    ctx_text = "\n\n".join("[%s — %s]\n%s" % (c["title"], c["url"], c["text"]) for c in ctx) or "(no specific match)"
    system = (SYSTEM % {"wa": WHATSAPP, "book": BOOKING_URL}) + "\n\nCONTEXT (use only this for facts):\n" + ctx_text

    messages = [{"role": "system", "content": system}]
    for m in msgs_in:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            messages.append({"role": m["role"], "content": m["content"]})

    reply, used, captured = None, None, False
    otp_sent_ok, otp_fail = False, None

    for key in GROQ_KEYS:
        try:
            m = _groq(messages, key, tools=TOOLS)
            tcs = m.get("tool_calls") or []
            if tcs:
                messages.append(m)
                for tc in tcs:
                    fn = tc.get("function", {}).get("name")
                    try:
                        args = json.loads(tc["function"].get("arguments") or "{}")
                    except Exception:
                        args = {}
                    if fn == "send_verification":
                        sv = send_verification(args)
                        if sv.get("ok"):
                            otp_sent_ok = True
                            result = {"code_sent": True, "instruction": "A code was emailed. Tell the visitor to check their inbox and type the 6-digit code here."}
                        elif sv.get("error") in ("need_phone", "bad_phone"):
                            otp_fail = "phone"
                            result = {"code_sent": False, "instruction": "A valid phone number is required before sending the code. Ask the visitor for their phone number. Do NOT say a code was sent."}
                        else:
                            otp_fail = "other"
                            result = {"code_sent": False, "instruction": "The code could not be sent. Apologise briefly and offer to continue on WhatsApp at +" + WHATSAPP + ". Do NOT say a code was sent."}
                    elif fn == "verify_and_capture":
                        vr = verify_and_capture(args)
                        ok = bool(vr.get("ok"))
                        captured = captured or ok
                        if ok:
                            result = {"verified": True, "saved": True, "instruction": "Thank them — their details are saved and the team will follow up within one business day. Offer a call or WhatsApp."}
                        else:
                            result = {"verified": False, "instruction": "The code was wrong or expired. Ask them to re-check and re-enter it, offer to resend, or hand off to WhatsApp. Do NOT say the lead was saved."}
                    else:
                        result = {"error": "unknown_tool"}
                    messages.append({"role": "tool", "tool_call_id": tc.get("id", ""),
                                     "content": json.dumps(result)})
                reply = _groq(messages, key).get("content")
            else:
                reply = m.get("content")
            used = "groq"
            break
        except Exception as e:
            print("GROQ_ERROR " + str(e)); continue

    if reply is None and GEMINI_KEY:
        try:
            reply = _gemini(messages); used = "gemini"
        except Exception as e:
            print("GEMINI_ERROR " + str(e))

    if not reply:
        reply = ("I'm having a brief technical hiccup. Please WhatsApp us at +%s, or drop "
                 "your name and email here and the team will get back to you today." % WHATSAPP)
        used = "fallback"

    # Deterministic guard: never let the model claim a code was sent when it wasn't
    # (covers both a failed send AND the model hallucinating "sent" without calling the tool).
    claims_sent = bool(re.search(r"(sent|emailed)[^.]{0,40}code|code[^.]{0,40}(sent|emailed)", reply or "", re.I))
    if not otp_sent_ok:
        if otp_fail == "other":
            reply = ("I couldn't send the verification code just now. Let's continue on WhatsApp at +%s and the "
                     "team will help you right away." % WHATSAPP)
        elif otp_fail == "phone" or claims_sent:
            reply = ("Almost there! Before I email your 6-digit verification code, I just need a phone number too "
                     "— what's the best number to reach you on? (Prefer to skip it? Message us on WhatsApp at +%s.)" % WHATSAPP)

    log_event(event="chat", provider=used, captured=captured, page=page, q=user_last[:120])
    return {
        "reply": reply,
        "captured": captured,
        "endState": "captured" if captured else "active",
        "provider": used,
        "sources": [{"title": c["title"], "url": c["url"]} for c in ctx[:3]],
        "actions": {"whatsapp": _wa_link(), "booking": BOOKING_URL},
    }

# ---------------------------------------------------------------- Vercel handler
class handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        self._send(200, {"ok": True, "service": "digiveritaz-chat"})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
            self._send(200, handle_chat(payload))
        except Exception as e:
            self._send(200, {"reply": "Sorry, something went wrong. Please WhatsApp us at +%s." % WHATSAPP,
                             "error": str(e), "endState": "error",
                             "actions": {"whatsapp": _wa_link(), "booking": BOOKING_URL}})

    def log_message(self, *a):
        return
