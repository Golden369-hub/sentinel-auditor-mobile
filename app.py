#!/usr/bin/env python3
import http.server
import json
import socketserver
from grd_mobile_audit import audit_network

PORT = 8080


class SentinelHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/run_audit":
            try:
                report = audit_network()
                payload = json.dumps(report).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:
                err_payload = json.dumps({
                    "status": "FAIL",
                    "error": str(e)
                }).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_payload)))
                self.end_headers()
                self.wfile.write(err_payload)
        else:
            super().do_GET()


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SentinelHandler) as httpd:
        print(f"GRD Sentinel API online at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
