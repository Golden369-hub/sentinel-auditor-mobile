#!/usr/bin/env python3
import http.server
import json
import os
import socketserver
import sys

PORT = 8080
LEDGER_PATH = os.path.expanduser("~/grd_mobile/audit_ledger.jsonl")
WEB_DIR = os.path.dirname(os.path.abspath(__file__))


class SentinelRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            payload = {
                "status": "NO_DATA",
                "blocks_logged": 0,
                "latest_record": None
            }

            if os.path.exists(LEDGER_PATH):
                try:
                    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                        lines = [line.strip() for line in f if line.strip()]
                    if lines:
                        latest = json.loads(lines[-1])
                        payload = {
                            "status": "PASS",
                            "blocks_logged": len(lines),
                            "latest_record": latest
                        }
                except Exception as e:
                    payload = {"status": "ERROR", "message": str(e)}

            self.wfile.write(json.dumps(payload).encode("utf-8"))
        else:
            super().do_GET()


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SentinelRequestHandler) as httpd:
        print("-" * 50)
        print(f"GRD SENTINEL // TELEMETRY BRIDGE ONLINE: PORT {PORT}")
        print(f"API Endpoint : http://localhost:{PORT}/api/telemetry")
        print("Static Portal: http://localhost:8080")
        print("-" * 50)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down Telemetry Bridge cleanly.")
            httpd.server_close()
            sys.exit(0)


if __name__ == "__main__":
    run_server()
