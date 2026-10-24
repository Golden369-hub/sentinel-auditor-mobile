#!/usr/bin/env python3
import json
import os
import sys

from grd_mobile_audit import audit_network


def evaluate_sla(report, cfg_path="config.json"):
    if not os.path.exists(cfg_path):
        print(f"[FAIL] Configuration not found: {cfg_path}")
        return False

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    sla = cfg.get("sla_thresholds", {})
    ping = report.get("ping_metrics", {})
    dns = report.get("dns_metrics", {})
    dl = report.get("download_metrics", {})

    max_lat = sla.get("max_avg_latency_ms", 60.0)
    max_jit = sla.get("max_jitter_ms", 15.0)
    max_loss = sla.get("max_packet_loss_pct", 0.0)
    max_dns = sla.get("max_dns_latency_ms", 25.0)
    min_mbps = sla.get("min_throughput_mbps", 50.0)

    violations = []

    if ping.get("avg_ms", 0.0) > max_lat:
        violations.append(
            f"Latency breach: {ping.get('avg_ms')} ms > {max_lat} ms"
        )

    if ping.get("mdev_ms", 0.0) > max_jit:
        violations.append(
            f"Jitter breach: {ping.get('mdev_ms')} ms > {max_jit} ms"
        )

    if ping.get("packet_loss_pct", 0.0) > max_loss:
        violations.append(
            f"Packet loss breach: {ping.get('packet_loss_pct')}% > {max_loss}%"
        )

    if dns.get("latency_ms", 0.0) > max_dns:
        violations.append(
            f"DNS latency breach: {dns.get('latency_ms')} ms > {max_dns} ms"
        )

    if dl.get("mbps", 0.0) < min_mbps:
        violations.append(
            f"Throughput breach: {round(dl.get('mbps', 0.0), 2)} Mbps < "
            f"{min_mbps} Mbps"
        )

    print("--------------------------------------------------")
    print("GRD SENTINEL // SLA COMPLIANCE EVALUATION")
    print("--------------------------------------------------")
    print(f"Carrier Node: {report.get('isp_metrics', {}).get('isp', 'N/A')}")
    print(f"Block Nonce : {report.get('sha256_hash', 'N/A')}")

    if violations:
        print("[FAIL] Network SLA requirements breached:")
        for v in violations:
            print(f"       ! {v}")
        print("--------------------------------------------------")
        return False

    print("[PASS] All network parameters within SLA specifications.")
    print("--------------------------------------------------")
    return True


if __name__ == "__main__":
    audit_report = audit_network()
    compliant = evaluate_sla(audit_report)
    sys.exit(0 if compliant else 2)
