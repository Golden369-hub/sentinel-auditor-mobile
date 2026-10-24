#!/usr/bin/env python3
import hashlib
import json
import os
import sys


def verify_chain(ledger_path="audit_ledger.jsonl"):
    if not os.path.exists(ledger_path):
        print(f"[FAIL] Ledger file not found: {ledger_path}")
        return False

    with open(ledger_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("[WARN] Ledger is empty. No records to verify.")
        return True

    expected_prev = "0" * 64
    for idx, raw_line in enumerate(lines, start=1):
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError as e:
            print(f"[FAIL] Malformed JSON on line {idx}: {e}")
            return False

        stored_prev = entry.get("prev_hash")
        stored_hash = entry.get("entry_hash")
        telemetry = entry.get("telemetry")

        if stored_prev != expected_prev:
            print(f"[FAIL] Broken link at block #{idx}:")
            print(f"       Expected prev_hash: {expected_prev}")
            print(f"       Found prev_hash:    {stored_prev}")
            return False

        # Recalculate canonical hash
        recalc_payload = {
            "prev_hash": stored_prev,
            "telemetry": telemetry
        }
        recalc_bytes = json.dumps(
            recalc_payload, sort_keys=True
        ).encode("utf-8")
        computed_hash = hashlib.sha256(recalc_bytes).hexdigest()

        if computed_hash != stored_hash:
            print(f"[FAIL] Hash mismatch at block #{idx}:")
            print(f"       Recorded: {stored_hash}")
            print(f"       Computed: {computed_hash}")
            return False

        expected_prev = stored_hash

    print("[PASS] Audit integrity verified.")
    print(f"[INFO] Total verified blocks: {len(lines)}")
    print(f"[ROOT] Current head hash: {expected_prev}")
    return True


if __name__ == "__main__":
    success = verify_chain()
    sys.exit(0 if success else 1)
