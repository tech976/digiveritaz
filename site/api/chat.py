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

def _extract_contact(msgs):
    """Pull name/email/phone out of the whole conversation so a tool call that omits
    one (e.g. user sends the phone in a later message) still has the full set."""
    users = [m.get("content", "") for m in (msgs or []) if m.get("role") == "user"]
    text = "\n".join(users)
    out = {}
    em = re.search(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)
    if em:
        out["email"] = em.group(0)
    for cand in re.findall(r"\+?\d[\d \-]{8,}\d", text):
        if 10 <= len(re.sub(r"\D", "", cand)) <= 13:
            out["phone"] = re.sub(r"[ \-]", "", cand)
            break
    name = ""
    nm = re.search(r"(?:i am|i'm|this is|my name is|name is)\s+([A-Za-z][A-Za-z.'\- ]{1,38})", text, re.I)
    if nm:
        name = re.split(r"(?i)\b(?:and|from|here|need|want|looking|for|the|my|we)\b", nm.group(1), 1)[0].strip()
    if not name and em:
        line = next((u for u in users if out["email"] in u), "")
        before = line.split(out["email"])[0].strip(" ,-:")
        toks = [w for w in re.split(r"\s+", before) if re.fullmatch(r"[A-Za-z][A-Za-z.'\-]*", w)]
        if toks:
            name = " ".join(toks[-3:])
    if name.strip():
        out["name"] = name.strip()[:60]
    return out

_PLACEHOLDER_NAMES = {"visitor", "user", "customer", "name", "your name", "client", "there", "test", "example", "someone"}

def _clean_name(n):
    n = (n or "").strip().strip(".")
    if not n or n.lower() in _PLACEHOLDER_NAMES:
        return ""
    if not re.fullmatch(r"[A-Za-z][A-Za-z.'\- ]{1,59}", n):
        return ""
    return n

def _last_otp(msgs):
    for mm in reversed(msgs or []):
        if mm.get("role") == "user":
            hit = re.search(r"\b(\d{6})\b", mm.get("content", "") or "")
            if hit:
                return hit.group(1)
    return ""

def _loadargs(tc):
    try:
        return json.loads((tc.get("function") or {}).get("arguments") or "{}")
    except Exception:
        return {}

def _parse_inline_tools(text):
    """Some models emit a tool call as text (<function=name>{json}</function>) instead of a
    native tool_call. Parse + strip them so the raw block never leaks to the visitor."""
    calls = []
    for hit in re.finditer(r"<function\s*=\s*([A-Za-z_]+)\s*>\s*(\{.*?\})", text or "", re.S):
        try:
            calls.append((hit.group(1), json.loads(hit.group(2))))
        except Exception:
            calls.append((hit.group(1), {}))
    cleaned = re.sub(r"<function\b.*", "", text or "", flags=re.S).strip()
    return cleaned, calls

def _otp_reply(state, known):
    wa, email = WHATSAPP, known.get("email", "")
    if state == "verified":
        return ("You're all set — thank you! Your details are verified and saved, and our team will reach out "
                "within one business day. Want to talk sooner? WhatsApp +%s or book a call: %s" % (wa, BOOKING_URL))
    if state in ("sent", "rate"):
        to = (" to " + email) if email else ""
        spam = " and spam (you may already have one from a moment ago)" if state == "rate" else ""
        return "I've emailed a 6-digit verification code%s. Please check your inbox%s and type the code here to confirm." % (to, spam)
    if state == "need_email":
        return "Happy to set that up! Could you share your name, email and phone? I'll email a quick 6-digit code to verify and get the team on it."
    if state == "need_phone":
        return "Almost there — what's the best phone number to reach you on? I'll email a 6-digit code to confirm. (Prefer WhatsApp? +%s)" % wa
    if state == "need_name":
        return "Thanks! And your name? Then I'll email you a 6-digit verification code to confirm."
    if state == "bad_code":
        return ("That code didn't match or has expired. Please re-enter the 6-digit code from your email, or say "
                "'resend' for a new one. You can also reach us on WhatsApp at +%s." % wa)
    return "I couldn't send the code just now — let's continue on WhatsApp at +%s and the team will help right away." % wa

# Service buttons surfaced under a reply when a service is mentioned/asked about.
SERVICES_MENU = [
    ("SEO", "/seo/", [r"\bseo\b", r"search engine optim"]),
    ("PPC / Google Ads", "/pay-per-click/", [r"\bppc\b", r"pay[- ]per[- ]click", r"google ads", r"search ads"]),
    ("Performance Marketing", "/performance-marketing-agency/", [r"performance marketing"]),
    ("Social Media Management", "/social-media-management/", [r"social media management", r"social media marketing"]),
    ("Paid Social Ads", "/paid-social-media-advertising/", [r"paid social", r"meta ads", r"facebook ads", r"instagram ads", r"social media advertising"]),
    ("E-Commerce Marketing", "/ecommerce-marketing/", [r"e-?commerce marketing", r"ecommerce marketing", r"online store marketing"]),
    ("Amazon Marketing", "/amazon-marketing/", [r"amazon"]),
    ("Native Advertising", "/native-advertising/", [r"native ad"]),
    ("WhatsApp Marketing", "/whatsapp-marketing-services/", [r"whatsapp"]),
    ("Influencer Marketing", "/influencer-marketing/", [r"influencer"]),
    ("Digital PR", "/digital-pr/", [r"digital pr"]),
    ("Online Reputation", "/online-reputation-management/", [r"reputation", r"\borm\b"]),
    ("Content Marketing", "/organic-marketing-services/", [r"content marketing", r"organic marketing", r"content writing", r"copywriting"]),
    ("Branding & Design", "/branding-and-design/", [r"branding", r"brand identity", r"\blogo\b"]),
    ("UI/UX Design", "/ui-ux-design/", [r"ui/?ux", r"ux design", r"ui design"]),
    ("Website Development", "/website-development/", [r"website development", r"web development", r"web design"]),
    ("Custom Software", "/custom-software-development/", [r"custom software", r"software development"]),
    ("E-Commerce Development", "/ecommerce-development/", [r"e-?commerce development", r"shopify", r"woocommerce", r"online store"]),
    ("Mobile App Development", "/mobile-app-development/", [r"mobile app", r"app development"]),
    ("Lead Generation", "/lead-generation/", [r"lead generation", r"lead gen"]),
    ("Generative Engine Optimisation", "/generative-search-optimisation/", [r"generative engine", r"\bgeo\b", r"\bgso\b"]),
    ("Conversion Rate Optimisation", "/conversion-rate-optimisation/", [r"conversion rate", r"\bcro\b", r"landing page"]),
    ("Data Strategy", "/data-strategy-consulting-services/", [r"data strategy", r"\bga4\b"]),
]

def _service_buttons(text, limit=6):
    t = " " + (text or "").lower() + " "
    out = []
    for label, url, pats in SERVICES_MENU:
        if any(re.search(p, t) for p in pats):
            out.append({"label": label, "url": url})
        if len(out) >= limit:
            break
    return out

def _services_for(reply, user_last):
    s = _service_buttons(reply) or _service_buttons(user_last)
    # General "what services do you offer?" — surface the top services even if the
    # reply text didn't enumerate them.
    if not s and re.search(r"\bservices?\b|what (do|all do) you (do|offer|provide)|offerings?", (user_last or ""), re.I):
        s = [{"label": l, "url": u} for (l, u, _) in SERVICES_MENU[:6]]
    return s

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
    otp_state = None
    known = _extract_contact(msgs_in)

    for key in GROQ_KEYS:
        try:
            m = _groq(messages, key, tools=TOOLS)
            content = m.get("content") or ""
            calls = [((tc.get("function") or {}).get("name"), _loadargs(tc)) for tc in (m.get("tool_calls") or [])]
            if not calls and "<function" in content:
                content, calls = _parse_inline_tools(content)
            for fn, args in calls:
                args = args if isinstance(args, dict) else {}
                if fn == "send_verification":
                    # Build the lead ONLY from what the visitor actually typed (never the model's guesses).
                    email = known.get("email", "")
                    phone = known.get("phone", "")
                    name = known.get("name", "") or _clean_name(args.get("name"))
                    if not email:
                        otp_state = "need_email"
                    elif len(_digits(phone)) < 10:
                        otp_state = "need_phone"
                    elif not name:
                        otp_state = "need_name"
                    else:
                        sv = send_verification({"name": name, "email": email, "phone": phone})
                        otp_state = "sent" if sv.get("ok") else ("rate" if sv.get("error") == "otp_rate_limited" else "send_fail")
                elif fn == "verify_and_capture":
                    otp = str(args.get("otp") or "").strip() or _last_otp(msgs_in)
                    email = known.get("email", "") or args.get("email", "")
                    if re.fullmatch(r"\d{6}", otp or "") and email:
                        vr = verify_and_capture({"name": known.get("name", ""), "email": email,
                                                 "phone": known.get("phone", ""), "business": args.get("business", ""),
                                                 "budget": args.get("budget", ""), "service": args.get("service", ""),
                                                 "industry": args.get("industry", ""), "timeline": args.get("timeline", ""),
                                                 "notes": args.get("notes", ""), "otp": otp})
                        captured = captured or bool(vr.get("ok"))
                        otp_state = "verified" if vr.get("ok") else "bad_code"
                    else:
                        otp_state = "bad_code"
            if calls:
                reply = _otp_reply(otp_state, known)
            else:
                reply = re.sub(r"<function\b.*", "", content, flags=re.S).strip()
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

    # Guard: if the model claimed a code was sent as plain text (no tool call), correct it.
    if otp_state is None and re.search(r"(sent|emailed)[^.]{0,40}code|code[^.]{0,40}(sent|emailed)", reply or "", re.I):
        reply = ("Happy to help! To email your 6-digit verification code I just need your name, email and phone "
                 "— could you share those? (Prefer WhatsApp? +%s)" % WHATSAPP)
    if captured:
        otp_state = "verified"

    log_event(event="chat", provider=used, captured=captured, page=page, q=user_last[:120])
    return {
        "reply": reply,
        "captured": captured,
        "endState": "captured" if captured else "active",
        "provider": used,
        "services": _services_for(reply, user_last),
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
