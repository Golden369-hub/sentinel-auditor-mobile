#!/usr/bin/env python3
import argparse
import signal
import sys
import time

from audit_guard import evaluate_sla
from grd_mobile_audit import audit_network

RUNNING = True


def handle_shutdown(signum, frame):
    global RUNNING
    print(f"\n[INFO] Caught signal {signum}. Terminating daemon...")
    RUNNING = False


def run_daemon(interval_seconds=300):
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    print("--------------------------------------------------")
    print("GRD SENTINEL // BACKGROUND AUDIT DAEMON ONLINE")
    print(f"Interval: {interval_seconds} seconds")
    print("Zero-Bloat // NIST SP 800-171 Immutability Guard")
    print("--------------------------------------------------")

    cycle = 1
    while RUNNING:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print(f"\n[CYCLE #{cycle}] Auditing network at {ts} UTC...")

        try:
            report = audit_network()
            compliant = evaluate_sla(report)
            status_tag = "SLA_PASS" if compliant else "SLA_BREACH"
            nonce = report.get("sha256_hash", "")[:16]
            print(f"[STATUS] Cycle #{cycle}: {status_tag} | Head: {nonce}...")
        except Exception as e:
            print(f"[ERROR] Cycle #{cycle} encountered fault: {e}")

        cycle += 1
        elapsed = 0
        while RUNNING and elapsed < interval_seconds:
            time.sleep(1)
            elapsed += 1

    print("[SHUTDOWN] Sentinel daemon safely halted. Ledger intact.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GRD Sentinel Daemon - Headless Periodic Telemetry Auditor"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Audit interval in seconds (default: 300)"
    )
    args = parser.parse_args()

    run_daemon(interval_seconds=args.interval)
    sys.exit(0)
