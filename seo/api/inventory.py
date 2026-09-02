"""GET /api/inventory — the page list plus the keyword clusters.

Served from the committed JSON that build_inventory.py / build_keywords.py
produce, so the dashboard has something to render before any crawling starts.
"""
import json, os
from http.server import BaseHTTPRequestHandler

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def run():
    def load(name):
        p = os.path.join(DATA, name)
        return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else {}
    inv, kw = load("inventory.json"), load("keywords.json")
    return 200, {"origin": inv.get("origin"), "count": inv.get("count", 0),
                 "pages": inv.get("pages", []),
                 "clusters": kw.get("clusters", {}), "unmapped": kw.get("unmapped", [])}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        code, obj = run()
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        return
