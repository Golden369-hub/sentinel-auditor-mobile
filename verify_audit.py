import hashlib
import json
from pathlib import Path
import sys


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
    computed_seal = hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

    print(f"[*] Framework  : {data.get('framework')}")
    print(f"[*] Timestamp  : {data.get('export_timestamp')}")
    print(f"[*] Computed   : {computed_seal}")
    print(f"[*] Recorded   : {recorded_seal}")

    if computed_seal == recorded_seal:
        print("[+] VERIFICATION SUCCESS: NIST SP 800-171 AU-9 SEAL INTACT")
        return True
    else:
        print("[-] VERIFICATION FAILED: INTEGRITY COMPROMISED")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        dl_path = Path.home() / "storage/downloads"
        target = str(list(dl_path.glob("sentinel-audit*.json"))[-1])
    verify_ledger(target)
