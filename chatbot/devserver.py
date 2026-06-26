#!/usr/bin/env python3
"""
Local dev server for the chatbot — serves the static site (with Vercel-style
cleanUrls/trailingSlash) AND the /api/chat endpoint, so you can test the whole
widget end-to-end without the Vercel CLI.

    python chatbot/devserver.py            # http://localhost:3000
    python chatbot/devserver.py 8090       # custom port

Reads keys from the repo-root .env (git-ignored).
"""
import os, sys, json
from http.server import HTTPServer, SimpleHTTPRequestHandler
# Serve XSLT/XML with content types the browser will apply (for sitemap stylesheet preview)
SimpleHTTPRequestHandler.extensions_map.setdefault(".xsl", "text/xsl")
SimpleHTTPRequestHandler.extensions_map[".xml"] = "application/xml"

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
SITE = os.path.join(REPO, "site")
sys.path.insert(0, os.path.join(SITE, "api"))
import chat as chatmod  # site/api/chat.py
import otp as otpmod    # site/api/otp.py

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        if path in ("/api/chat", "/api/otp"):
            n = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(n) or b"{}")
            except Exception:
                payload = {}
            try:
                if path == "/api/otp":
                    self._json(200, otpmod.handle_otp(payload))
                else:
                    self._json(200, chatmod.handle_chat(payload))
            except Exception as e:
                self._json(200, {"ok": False, "reply": "Server error: " + str(e), "endState": "error"})
        else:
            self._json(404, {"error": "not found"})

    def _exists(self, rel):
        return os.path.isfile(os.path.join(SITE, rel.lstrip("/")))

    def do_GET(self):
        p = self.path.split("?")[0]
        if p.rstrip("/") == "/api/chat":
            return self._json(200, {"ok": True, "service": "digiveritaz-chat"})
        if p.rstrip("/") == "/api/otp":
            return self._json(200, {"ok": True, "service": "digiveritaz-otp"})
        # Vercel-style clean URL resolution
        if p != "/" and p.endswith("/"):
            if self._exists(p + "index.html"):
                self.path = p + "index.html"
            elif self._exists(p.rstrip("/") + ".html"):
                self.path = p.rstrip("/") + ".html"
        elif p != "/" and "." not in os.path.basename(p):
            if self._exists(p + ".html"):
                self.path = p + ".html"
            elif self._exists(p + "/index.html"):
                self.path = p + "/index.html"
        return super().do_GET()

    def log_message(self, *a):
        return


if __name__ == "__main__":
    print("DigiVeritaz site + chatbot on http://localhost:%d  (Ctrl+C to stop)" % PORT)
    keys = len(chatmod.GROQ_KEYS) + (1 if chatmod.GEMINI_KEY else 0)
    print("LLM keys loaded: %d  | KB chunks: %d" % (keys, len(chatmod._kb()["chunks"])))
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
