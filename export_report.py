#!/usr/bin/env python3
import csv
import json
import os
import sys
import time


def generate_reports(ledger_path="audit_ledger.jsonl"):
    if not os.path.exists(ledger_path):
        print(f"[FAIL] Ledger not found: {ledger_path}")
        return False

    records = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not records:
        print("[WARN] Ledger contains no parseable entries.")
        return False

    csv_filename = "sentinel_compliance_export.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "Block_Index",
            "Timestamp_UTC",
            "Carrier_ISP",
            "ASN",
            "Gateway_City",
            "Latency_Avg_ms",
            "Jitter_mdev_ms",
            "Packet_Loss_pct",
            "DNS_Latency_ms",
            "Throughput_Mbps",
            "Status",
            "Entry_SHA256"
        ])

        total_loss = 0.0
        total_mbps = 0.0
        total_lat = 0.0
        pass_count = 0

        for idx, entry in enumerate(records, start=1):
            t = entry.get("telemetry", {})
            isp = t.get("isp_metrics", {})
            ping = t.get("ping_metrics", {})
            dns = t.get("dns_metrics", {})
            dl = t.get("download_metrics", {})

            loss = ping.get("packet_loss_pct", 0.0)
            mbps = dl.get("mbps", 0.0)
            avg_ms = ping.get("avg_ms", 0.0)
            status = t.get("status", "UNKNOWN")

            if status == "PASS":
                pass_count += 1
            total_loss += loss
            total_mbps += mbps
            total_lat += avg_ms

            ts = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.gmtime(t.get("timestamp", 0))
            )

            writer.writerow([
                idx,
                ts,
                isp.get("isp", "N/A"),
                isp.get("asn", "N/A"),
                isp.get("city", "N/A"),
                avg_ms,
                ping.get("mdev_ms", 0.0),
                loss,
                dns.get("latency_ms", 0.0),
                round(mbps, 2),
                status,
                entry.get("entry_hash", "")
            ])

    n = len(records)
    print(f"[PASS] Exported {n} blocks to {csv_filename}")
    print("--------------------------------------------------")
    print("NIST SP 800-171 AU-6 TELEMETRY EXECUTIVE SUMMARY")
    print("--------------------------------------------------")
    print(f"Total Audits Logged      : {n}")
    print(f"Pass Rate                : {round((pass_count / n) * 100, 2)}%")
    print(f"Average Latency (RTT)    : {round(total_lat / n, 2)} ms")
    print(f"Mean Packet Loss Rate    : {round(total_loss / n, 2)}%")
    print(f"Average Single-Stream    : {round(total_mbps / n, 2)} Mbps")
    print(f"Latest Chained Root Nonce: {records[-1].get('entry_hash', '')}")
    print("--------------------------------------------------")
    return True


if __name__ == "__main__":
    success = generate_reports()
    sys.exit(0 if success else 1)
