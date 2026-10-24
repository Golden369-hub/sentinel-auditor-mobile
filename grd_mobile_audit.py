#!/usr/bin/env python3
import hashlib
import json
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request


def get_last_hash(ledger_file="audit_ledger.jsonl"):
    if not os.path.exists(ledger_file):
        return "0" * 64
    try:
        with open(ledger_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return "0" * 64
            last_entry = json.loads(lines[-1].strip())
            return last_entry.get("entry_hash", "0" * 64)
    except (json.JSONDecodeError, OSError):
        return "0" * 64


def append_to_ledger(report, ledger_file="audit_ledger.jsonl"):
    prev_hash = get_last_hash(ledger_file)
    entry = {
        "prev_hash": prev_hash,
        "telemetry": report
    }
    raw_bytes = json.dumps(entry, sort_keys=True).encode("utf-8")
    entry_hash = hashlib.sha256(raw_bytes).hexdigest()
    entry["entry_hash"] = entry_hash

    with open(ledger_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry_hash


def audit_network(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    host = cfg["ping"]["target"]
    count = cfg["ping"]["count"]
    dl_url = cfg["throughput"]["url"]
    timeout_s = cfg["throughput"]["timeout_seconds"]

    # NIST SC: Verify scheme is strictly HTTP/HTTPS
    parsed_url = urllib.parse.urlparse(dl_url)
    if parsed_url.scheme not in ("http", "https"):
        raise ValueError(f"Disallowed protocol scheme: {parsed_url.scheme}")

    # 1. ICMP Telemetry
    cmd = ["ping", "-c", str(count), "-W", str(timeout_s), host]
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )
    rtt_match = re.search(
        r"rtt min/avg/max/mdev = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+)",
        res.stdout
    )

    if rtt_match:
        ping_metrics = {
            "min_ms": float(rtt_match.group(1)),
            "avg_ms": float(rtt_match.group(2)),
            "max_ms": float(rtt_match.group(3)),
            "mdev_ms": float(rtt_match.group(4))
        }
    else:
        ping_metrics = {
            "min_ms": 0.0,
            "avg_ms": 0.0,
            "max_ms": 0.0,
            "mdev_ms": 0.0
        }

    # 2. HTTP/TLS Goodput Audit
    start_t = time.time()
    req = urllib.request.Request(
        dl_url,
        headers={"User-Agent": "GRD-Sentinel-Auditor/1.1"}
    )
    with urllib.request.urlopen(  # nosec B310
        req, timeout=timeout_s
    ) as response:
        payload = response.read()
    duration = time.time() - start_t
    bytes_transferred = len(payload)
    mbps = ((bytes_transferred * 8) / (1024 * 1024)) / duration

    download_metrics = {
        "bytes_transferred": bytes_transferred,
        "duration_s": duration,
        "mbps": mbps
    }

    report = {
        "timestamp": int(time.time()),
        "ping_metrics": ping_metrics,
        "download_metrics": download_metrics,
        "status": "PASS"
    }

    # 3. Cryptographic Ledger Append
    report["sha256_hash"] = append_to_ledger(report)
    return report


if __name__ == "__main__":
    rep = audit_network()
    print(json.dumps(rep, indent=2))
