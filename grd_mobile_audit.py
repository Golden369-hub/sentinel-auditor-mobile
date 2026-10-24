#!/usr/bin/env python3
import json
import os
import ssl
import subprocess
import time
import urllib.request


def run_ping_test(host, count=4):
    cmd = ["ping", "-c", str(count), host]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = res.stdout.strip().split("\n")
        stats_line = [
            line for line in lines
            if "rtt min/avg/max/mdev" in line or "round-trip" in line
        ]
        if stats_line:
            parts = stats_line[0].split("=")[1].strip().split("/")
            return {
                "min_ms": float(parts[0]),
                "avg_ms": float(parts[1]),
                "max_ms": float(parts[2]),
                "mdev_ms": float(parts[3].split()[0]),
            }
    except Exception:
        pass
    return None


def run_download_test(url, timeout=10, chunk_size=65536):
    if not url.lower().startswith(("https://", "http://")):
        raise ValueError(f"Disallowed URL scheme: {url}")

    ctx = ssl.create_default_context()
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    headers = {"User-Agent": "GRD-Sentinel-Auditor/1.0"}
    total_bytes = 0
    start_time = time.time()

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(
            req, context=ctx, timeout=timeout
        ) as response:  # nosec B310
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if time.time() - start_time > timeout:
                    break
        duration = time.time() - start_time
        mbps = (total_bytes * 8) / (duration * 1_000_000)
        return {
            "bytes_transferred": total_bytes,
            "duration_s": duration,
            "mbps": mbps,
        }
    except Exception as e:
        return {"error": str(e)}


def audit_network(config_file="config.json"):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file missing: {config_file}")

    with open(config_file, "r") as f:
        cfg = json.load(f)

    ping_cfg = cfg.get("ping", {})
    tp_cfg = cfg.get("throughput", {})

    target_host = ping_cfg.get("target", "1.1.1.1")
    ping_count = ping_cfg.get("count", 4)
    download_url = tp_cfg.get(
        "url",
        "https://speed.cloudflare.com/__down?bytes=25000000"
    )
    timeout = tp_cfg.get("timeout_seconds", 8)
    chunk_size = tp_cfg.get("chunk_size", 65536)

    ping_result = run_ping_test(target_host, count=ping_count)
    dl_result = run_download_test(
        download_url, timeout=timeout, chunk_size=chunk_size
    )

    status = "PASS" if ping_result and "error" not in dl_result else "FAIL"
    return {
        "timestamp": int(time.time()),
        "ping_metrics": ping_result,
        "download_metrics": dl_result,
        "status": status,
    }


if __name__ == "__main__":
    report = audit_network()
    print(json.dumps(report, indent=2))
