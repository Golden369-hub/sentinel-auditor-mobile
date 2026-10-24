#!/usr/bin/env python3
import http.server
import json
import os
import re
import socketserver
import subprocess  # nosec B404
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

        elif self.path == "/api/trace":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            hops = []
            cmd = ["traceroute", "-n", "-m", "10", "-w", "1", "1.1.1.1"]
            try:
                proc = subprocess.run(  # nosec B603
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=15
                )
                for line in proc.stdout.strip().split("\n")[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    m = re.match(
                        r"^(\d+)\s+([0-9\.\*]+)\s+([0-9\.]+|\*)\s*ms?",
                        line
                    )
                    if m:
                        hops.append({
                            "hop": int(m.group(1)),
                            "ip": m.group(2),
                            "rtt_ms": m.group(3)
                        })
                    elif "*" in line:
                        p = line.split()
                        num = int(p[0]) if p[0].isdigit() else len(hops) + 1
                        hops.append({"hop": num, "ip": "*", "rtt_ms": "*"})
            except Exception as e:
                hops = [{"error": str(e)}]

            self.wfile.write(json.dumps({"hops": hops}).encode("utf-8"))
        else:
            super().do_GET()


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SentinelRequestHandler) as httpd:
        print("-" * 50)
        print(f"GRD SENTINEL // TELEMETRY BRIDGE ONLINE: PORT {PORT}")
        print(f"API Endpoints: /api/telemetry | /api/trace")
        print(f"Static Portal: http://localhost:{PORT}")
        print("-" * 50)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down Telemetry Bridge cleanly.")
            httpd.server_close()
            sys.exit(0)


if __name__ == "__main__":
    run_server()
