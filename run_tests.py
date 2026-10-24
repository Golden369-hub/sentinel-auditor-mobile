#!/usr/bin/env python3
import json
import os
import subprocess  # nosec B404
import sys

from verify_ledger import verify_chain


def check_config(path="config.json"):
    print("[TEST 1/4] Validating config.json schema...")
    if not os.path.exists(path):
        print(f"  [FAIL] Missing configuration: {path}")
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        required = ["ping", "dns", "throughput", "sla_thresholds"]
        for key in required:
            if key not in cfg:
                print(f"  [FAIL] Missing required section: {key}")
                return False
        print("  [PASS] Config schema intact.")
        return True
    except Exception as e:
        print(f"  [FAIL] JSON parsing error: {e}")
        return False


def check_ledger():
    print("[TEST 2/4] Verifying cryptographic SHA-256 ledger...")
    valid = verify_chain()
    if valid:
        print("  [PASS] Ledger cryptographically verified.")
        return True
    print("  [FAIL] Ledger verification failed.")
    return False


def run_bandit():
    print("[TEST 3/4] Running Bandit SAST scan...")
    cmd = ["bandit", "-r", ".", "-ll", "-q"]
    proc = subprocess.run(  # nosec B603
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if proc.returncode == 0:
        print("  [PASS] SAST passed. 0 Medium / 0 High vulnerabilities.")
        return True
    print("  [FAIL] Bandit detected security issues.")
    return False


def run_flake8():
    print("[TEST 4/4] Running Flake8 style audit...")
    cmd = ["flake8", "."]
    proc = subprocess.run(  # nosec B603
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if proc.returncode == 0 and not proc.stdout.strip():
        print("  [PASS] Flake8 passed. 0 style violations.")
        return True
    print(f"  [FAIL] Flake8 violations detected:\n{proc.stdout}")
    return False


def main():
    print("=" * 50)
    print("GRD SENTINEL AUDITOR // UNIFIED TEST HARNESS")
    print("=" * 50)

    checks = [
        check_config(),
        check_ledger(),
        run_bandit(),
        run_flake8()
    ]

    print("=" * 50)
    if all(checks):
        print("[SUCCESS] All 4 verification stages passed.")
        print("=" * 50)
        sys.exit(0)
    else:
        print("[FAILURE] One or more test stages tripped.")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
