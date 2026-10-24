import json
import os
import sys

CONFIG_PATH = os.path.expanduser("~/grd_mobile/config.json")

def test_config_integrity():
    assert os.path.exists(CONFIG_PATH), "FAIL: config.json missing"
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    assert "ping" in data and "target" in data["ping"], "FAIL: ping configuration invalid"
    assert "throughput" in data and "url" in data["throughput"], "FAIL: throughput configuration invalid"
    print("[PASS] Configuration schema verified.")

def main():
    try:
        test_config_integrity()
        print("[PASS] Pre-flight pipeline check successful.")
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
