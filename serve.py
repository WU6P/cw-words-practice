#!/usr/bin/env python3
"""Local dev server for CW Words Practice.

Adds Cache-Control: max-age headers so iOS Safari caches the app and can
serve it offline after the server is stopped.  Use instead of:
  python3 -m http.server 8000
"""
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CacheHandler(SimpleHTTPRequestHandler):
    # Resources that should never be stale-cached (always re-fetch when online)
    NO_CACHE = {'/sw.js', '/manifest.json'}
    # Everything else gets a one-year cache so iOS serves it offline
    MAX_AGE = 365 * 24 * 3600

    def end_headers(self):
        path = self.path.split('?')[0]
        if path in self.NO_CACHE:
            self.send_header('Cache-Control', 'no-cache')
        else:
            self.send_header('Cache-Control', f'public, max-age={self.MAX_AGE}')
        super().end_headers()

    def log_message(self, fmt, *args):
        super().log_message(fmt, *args)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(('', port), CacheHandler)
    print(f'Serving at http://0.0.0.0:{port}  (Ctrl-C to stop)')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
