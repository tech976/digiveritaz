#!/usr/bin/env python3
"""Local dev server for the SEO dashboard.

Unlike site/serve.py (static only), this one dispatches /api/* to the same
Python functions Vercel will run, so the dashboard is fully working locally.

Usage:
    python3 serve.py            # http://localhost:3002
    python3 serve.py 4000
"""
import json, os, sys, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "api"))
import analyze as analyze_fn
import inventory as inventory_fn


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    # ---- api ----------------------------------------------------------
    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _route(self, params):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")
        if path == "/api/analyze":
            return analyze_fn.run(params)
        if path == "/api/inventory":
            return inventory_fn.run()
        return 404, {"error": "no such endpoint"}

    def do_GET(self):
        if urllib.parse.urlparse(self.path).path.startswith("/api/"):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                self._json(*self._route({k: v[0] for k, v in q.items()}))
            except Exception as e:
                self._json(500, {"error": str(e)})
            return
        super().do_GET()

    def do_POST(self):
        if not urllib.parse.urlparse(self.path).path.startswith("/api/"):
            self.send_error(405)
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            self._json(*self._route(json.loads(self.rfile.read(n) or b"{}")))
        except Exception as e:
            self._json(500, {"error": str(e)})

    # ---- static (mirrors vercel cleanUrls) -----------------------------
    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0]
        fs = super().translate_path(clean)
        if os.path.isfile(fs):
            return fs
        if os.path.isdir(fs):
            idx = os.path.join(fs, "index.html")
            if os.path.isfile(idx):
                return idx
        cand = fs.rstrip(os.sep) + ".html"
        return cand if os.path.isfile(cand) else fs

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3002
    print(f"DigiVeritaz SEO dashboard  ->  http://localhost:{port}/")
    print(f"  api: /api/inventory  /api/analyze?url=...&keyphrase=...")
    try:
        ThreadingHTTPServer(("localhost", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
