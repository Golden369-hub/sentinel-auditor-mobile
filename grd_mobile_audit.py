import subprocess
import re
import time
import urllib.request
import ssl

def audit_ping(host="1.1.1.1", count=4):
    cmd = ["ping", "-c", str(count), host]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    latencies = [float(x) for x in re.findall(r"time=([\d\.]+)\s*ms", res.stdout)]
    if not latencies:
        return {"avg_ms": 0.0, "jitter_ms": 0.0}
    avg_lat = round(sum(latencies) / len(latencies), 2)
    jitter = round(max(latencies) - min(latencies), 2)
    return {"avg_ms": avg_lat, "jitter_ms": jitter}

def audit_download():
    url = "https://speed.cloudflare.com/__down?bytes=25000000"
    headers = {"User-Agent": "Mozilla/5.0"}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    total_bytes = 0
    try:
        req = urllib.request.Request(url, headers=headers)
        start_time = time.time()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if time.time() - start_time > 8:
                    break
        duration = time.time() - start_time
        if duration <= 0 or total_bytes == 0:
            return 0.0
        mbps = round((total_bytes * 8) / (duration * 1024 * 1024), 2)
        return mbps
    except Exception as e:
        print(f"    [DEBUG] Stream Error: {e}")
        return 0.0

def main():
    print("=============================================")
    print("  GRD SENTINEL™ // MOBILE WI-FI AUDIT")
    print("  Zero Telemetry | Pure Standard Library")
    print("=============================================")
    print("[*] Auditing Ping & Jitter to 1.1.1.1...")
    ping_data = audit_ping()
    print(f"    Avg Latency: {ping_data['avg_ms']} ms")
    print(f"    Jitter     : {ping_data['jitter_ms']} ms")
    print("[*] Auditing Wi-Fi Goodput (Cloudflare CDN)...")
    speed = audit_download()
    print(f"    Throughput : {speed} Mbps")
    print("=============================================")
    print("[+] Audit Complete.")

if __name__ == "__main__":
    main()
