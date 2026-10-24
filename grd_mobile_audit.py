#!/usr/bin/env python3
import hashlib
import json
import os
import re
import socket
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


def audit_dns(query_host):
    start_t = time.time()
    try:
        addr_info = socket.getaddrinfo(
            query_host, None, socket.AF_INET, socket.SOCK_STREAM
        )
        latency_ms = (time.time() - start_t) * 1000.0
        resolved_ips = sorted(list({item[4][0] for item in addr_info}))
        return {
            "query_host": query_host,
            "resolved_ips": resolved_ips,
            "latency_ms": round(latency_ms, 2),
            "status": "PASS"
        }
    except socket.gaierror:
        return {
            "query_host": query_host,
            "resolved_ips": [],
            "latency_ms": 0.0,
            "status": "FAIL"
        }


def audit_network(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    host = cfg["ping"]["target"]
    count = cfg["ping"]["count"]
    dl_url = cfg["throughput"]["url"]
    timeout_s = cfg["throughput"]["timeout_seconds"]
    query_host = cfg.get("dns", {}).get("query_host", "cloudflare.com")

    parsed_url = urllib.parse.urlparse(dl_url)
    if parsed_url.scheme not in ("http", "https"):
        raise ValueError(f"Disallowed protocol scheme: {parsed_url.scheme}")

    # 1. ICMP Burst & Packet Loss Telemetry
    cmd = ["ping", "-c", str(count), "-W", str(timeout_s), host]
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False
    )

    loss_match = re.search(r"(\d+)% packet loss", res.stdout)
    packet_loss_pct = float(loss_match.group(1)) if loss_match else 0.0

    rtt_match = re.search(
        r"rtt min/avg/max/mdev = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+)",
        res.stdout
    )

    if rtt_match:
        ping_metrics = {
            "min_ms": float(rtt_match.group(1)),
            "avg_ms": float(rtt_match.group(2)),
            "max_ms": float(rtt_match.group(3)),
            "mdev_ms": float(rtt_match.group(4)),
            "packet_loss_pct": packet_loss_pct
        }
    else:
        ping_metrics = {
            "min_ms": 0.0,
            "avg_ms": 0.0,
            "max_ms": 0.0,
            "mdev_ms": 0.0,
            "packet_loss_pct": 100.0
        }

    # 2. DNS Telemetry
    dns_metrics = audit_dns(query_host)

    # 3. HTTP/TLS Goodput Audit
    start_t = time.time()
    req = urllib.request.Request(
        dl_url,
        headers={"User-Agent": "GRD-Sentinel-Auditor/1.3"}
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

    status = (
        "PASS"
        if (packet_loss_pct == 0.0 and dns_metrics["status"] == "PASS")
        else "DEGRADED"
    )

    report = {
        "timestamp": int(time.time()),
        "ping_metrics": ping_metrics,
        "dns_metrics": dns_metrics,
        "download_metrics": download_metrics,
        "status": status
    }

    # 4. Cryptographic Ledger Append
    report["sha256_hash"] = append_to_ledger(report)
    return report


if __name__ == "__main__":
    rep = audit_network()
    print(json.dumps(rep, indent=2))
