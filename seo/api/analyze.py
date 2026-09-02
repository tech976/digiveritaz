"""GET/POST /api/analyze — Yoast-style report for one URL.

One URL per request on purpose: a single page takes ~1-3s, so fanning 293 of
them out from the browser (a few at a time) keeps every request well under
Vercel's 10s function ceiling and lets the dashboard fill in progressively.
"""
import json, os, sys, urllib.parse
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _engine as engine

ALLOWED_HOSTS = {"digiveritaz.com", "www.digiveritaz.com", "localhost", "127.0.0.1"}


def run(params):
    url = (params.get("url") or "").strip()
    if not url:
        return 400, {"error": "missing url"}
    if not url.startswith(("http://", "https://")):
        url = "https://" + url.lstrip("/")

    host = urllib.parse.urlparse(url).hostname or ""
    if host.split(":")[0] not in ALLOWED_HOSTS:
        return 403, {"error": f"host not allowed: {host}",
                     "hint": "This dashboard audits digiveritaz.com only."}

    kp = (params.get("keyphrase") or "").strip() or None
    src = (params.get("keyphrase_source") or "derived").strip()
    return 200, engine.analyze_url(url, kp, src)


class handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        params = {k: v[0] for k, v in q.items()}
        try:
            self._send(*run(params))
        except Exception as e:
            self._send(500, {"error": str(e)})

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            self._send(*run(json.loads(self.rfile.read(n) or b"{}")))
        except Exception as e:
            self._send(500, {"error": str(e)})

    def log_message(self, *a):
        return
