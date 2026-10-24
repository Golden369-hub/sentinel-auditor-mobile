import json
import hashlib
import sys
from pathlib import Path

def verify_ledger(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"[-] Error: File not found: {filepath}")
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    recorded_seal = data.get("au9_sha256_seal")
    if not recorded_seal:
        print("[-] Error: Missing 'au9_sha256_seal' in ledger.")
        return False

    del data["au9_sha256_seal"]
    canonical_json = json.dumps(data, indent=2)
    computed_seal = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    print(f"[*] Framework  : {data.get('framework')}")
    print(f"[*] Timestamp  : {data.get('export_timestamp')}")
    print(f"[*] Computed   : {computed_seal}")
    print(f"[*] Recorded   : {recorded_seal}")

    if computed_seal == recorded_seal:
        print("[+] VERIFICATION SUCCESS: NIST SP 800-171 AU-9 SEAL INTACT (ZERO DRIFT)")
        return True
    else:
        print("[-] VERIFICATION FAILED: INTEGRITY COMPROMISED / HASH MISMATCH")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(list(Path.home().glob("storage/downloads/sentinel-audit*.json"))[-1])
    verify_ledger(target)
