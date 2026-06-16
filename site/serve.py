#!/usr/bin/env python3
"""Local dev server that mimics Vercel's cleanUrls + trailingSlash routing.

Production (Vercel) serves clean URLs like /contact-us/ from the flat file
contact-us.html. A plain `python -m http.server` does not, so every page except
index.html 404s locally. This server replicates the Vercel mapping so local
previews match production.

Usage:
    python3 serve.py            # serves ./ on http://localhost:3000
    python3 serve.py 8080       # custom port
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))


class CleanURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        # Resolve the on-disk file for a clean URL request.
        # Drop query string / fragment before routing.
        clean = path.split("?", 1)[0].split("#", 1)[0]
        fs = super().translate_path(clean)

        # Real file (asset, css, js, .html) -> serve as-is.
        if os.path.isfile(fs):
            return fs

        # Directory with an index.html (e.g. /case-study/, /uk/) -> serve it.
        if os.path.isdir(fs):
            index = os.path.join(fs, "index.html")
            if os.path.isfile(index):
                return index

        # Clean URL: /contact-us/ or /contact-us -> contact-us.html
        # Also handles nested: /blog/post/ -> blog/post.html
        candidate = fs.rstrip(os.sep) + ".html"
        if os.path.isfile(candidate):
            return candidate

        return fs

    def end_headers(self):
        # Avoid stale-cache confusion during local dev.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    httpd = HTTPServer(("localhost", port), CleanURLHandler)
    print(f"DigiVeritaz dev server  ->  http://localhost:{port}/")
    print("(clean URLs + trailing slashes, mirroring vercel.json)")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
