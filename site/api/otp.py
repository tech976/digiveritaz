"""
DigiVeritaz OTP — Vercel Serverless Function (POST /api/otp) backed by MSG91.

Why server-side: the MSG91 auth key is a SECRET and must never ship in browser
JS. The frontend calls this same-origin endpoint; this function talks to MSG91.

The lead's phone number is saved to the sheet BEFORE this is ever called, so a
number is captured even if the person never completes (or never starts) OTP.

Actions (JSON body):
  {"action":"send",   "phone":"9XXXXXXXXX"}            -> MSG91 sends an SMS OTP
  {"action":"verify", "phone":"9XXXXXXXXX","otp":"123456"} -> MSG91 verifies it
  {"action":"resend", "phone":"9XXXXXXXXX"}            -> MSG91 resends

Env vars (set in Vercel -> Project -> Settings -> Environment Variables):
  MSG91_AUTHKEY      (required)  your MSG91 Auth Key
  MSG91_TEMPLATE_ID  (required)  DLT-approved OTP template id from MSG91
  MSG91_OTP_EXPIRY   (optional)  minutes, default 5
  MSG91_OTP_LENGTH   (optional)  digits, default 6
  MSG91_COUNTRY      (optional)  country code, default 91 (India)

Stdlib only (urllib) so Vercel builds it as a single function with no deps.
"""
import os, re, json, urllib.request, urllib.parse
from http.server import BaseHTTPRequestHandler

MSG91_BASE = "https://control.msg91.com/api/v5"


def _load_env():
    if os.environ.get("MSG91_AUTHKEY"):
        return
    here = os.path.dirname(os.path.abspath(__file__))
    for base in (os.getcwd(), here, os.path.dirname(here), os.path.dirname(os.path.dirname(here))):
        p = os.path.join(base, ".env")
        if os.path.isfile(p):
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            return


_load_env()


def _cfg():
    return {
        "authkey":  os.environ.get("MSG91_AUTHKEY", "").strip(),
        "template": os.environ.get("MSG91_TEMPLATE_ID", "").strip(),
        "expiry":   os.environ.get("MSG91_OTP_EXPIRY", "5").strip() or "5",
        "length":   os.environ.get("MSG91_OTP_LENGTH", "6").strip() or "6",
        "cc":       os.environ.get("MSG91_COUNTRY", "91").strip() or "91",
    }


def _mobile(phone, cc):
    digits = re.sub(r"\D", "", str(phone or ""))
    if digits.startswith(cc) and len(digits) > 10:
        return digits
    return cc + digits[-10:]


def _http(method, url, authkey, body=None):
    headers = {"authkey": authkey, "Content-Type": "application/json", "Accept": "application/json"}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
    except Exception as e:
        return {"type": "error", "message": "network: %s" % e}
    try:
        return json.loads(raw)
    except Exception:
        return {"type": "error", "message": raw[:300]}


def handle_otp(payload):
    cfg = _cfg()
    action = (payload.get("action") or "").lower()
    phone = payload.get("phone") or ""

    if not cfg["authkey"] or not cfg["template"]:
        # Misconfigured: tell the frontend so it can let the lead continue
        # (the number is already captured) instead of dead-ending.
        return {"ok": False, "error": "otp_not_configured"}

    digits = re.sub(r"\D", "", str(phone))
    if len(digits) < 10:
        return {"ok": False, "error": "bad_phone"}
    mobile = _mobile(phone, cfg["cc"])

    if action == "send":
        q = urllib.parse.urlencode({
            "template_id": cfg["template"],
            "mobile": mobile,
            "otp_expiry": cfg["expiry"],
            "otp_length": cfg["length"],
        })
        res = _http("POST", "%s/otp?%s" % (MSG91_BASE, q), cfg["authkey"], body={})
        ok = str(res.get("type", "")).lower() == "success"
        return {"ok": ok, "request_id": res.get("message") if ok else None,
                "error": None if ok else (res.get("message") or "send_failed")}

    if action == "resend":
        q = urllib.parse.urlencode({"mobile": mobile, "retrytype": "text"})
        res = _http("GET", "%s/otp/retry?%s" % (MSG91_BASE, q), cfg["authkey"])
        ok = str(res.get("type", "")).lower() == "success"
        return {"ok": ok, "error": None if ok else (res.get("message") or "resend_failed")}

    if action == "verify":
        otp = re.sub(r"\D", "", str(payload.get("otp") or ""))
        if len(otp) < 4:
            return {"ok": False, "error": "bad_otp"}
        q = urllib.parse.urlencode({"mobile": mobile, "otp": otp})
        res = _http("GET", "%s/otp/verify?%s" % (MSG91_BASE, q), cfg["authkey"])
        msg = str(res.get("message", "")).lower()
        ok = (str(res.get("type", "")).lower() == "success") or ("verified" in msg)
        return {"ok": ok, "verified": ok,
                "error": None if ok else (res.get("message") or "otp_mismatch")}

    return {"ok": False, "error": "unknown_action"}


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
        cfg = _cfg()
        self._send(200, {"ok": True, "service": "digiveritaz-otp",
                         "configured": bool(cfg["authkey"] and cfg["template"])})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
            self._send(200, handle_otp(payload))
        except Exception as e:
            self._send(200, {"ok": False, "error": "server_error", "detail": str(e)})

    def log_message(self, *a):
        return
