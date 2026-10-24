#!/usr/bin/env python3
import json
import os
import sys


def test_config_integrity():
    if not os.path.exists("config.json"):
        print("[FAIL] config.json missing.")
        sys.exit(1)
    with open("config.json", "r") as f:
        cfg = json.load(f)
    assert "ping" in cfg and "target" in cfg["ping"], (
        "FAIL: ping configuration invalid"
    )
    assert "throughput" in cfg and "url" in cfg["throughput"], (
        "FAIL: throughput configuration invalid"
    )
    print("[PASS] Configuration schema verified.")


def main():
    test_config_integrity()
    print("[PASS] Pre-flight pipeline check successful.")


if __name__ == "__main__":
    main()
