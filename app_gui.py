#!/usr/bin/env python3
import http.server
import json
import os
import socketserver

PORT = 8080


class AuditHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            index_path = os.path.join(
                os.path.dirname(__file__), "index.html"
            )
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        elif self.path == "/api/run_audit":
            from grd_mobile_audit import audit_network
            report = audit_network("config.json")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(report).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    addr = ("127.0.0.1", PORT)
    with socketserver.TCPServer(addr, AuditHandler) as httpd:
        print(f"[+] Sentinel HUD active on http://127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    run_server()
