import re
with open('grd_mobile_audit.py', 'r') as f:
    code = f.read()

func = '''
def audit_cellular():
    try:
        import subprocess, json
        res = subprocess.run(["termux-telephony-cellinfo"], capture_output=True, text=True)
        cells = json.loads(res.stdout)
        for cell in cells:
            if cell.get("registered", False):
                rsrp = cell.get("ss_rsrp") or cell.get("rsrp", 0)
                rsrq = cell.get("ss_rsrq") or cell.get("rsrq", 0)
                band = cell.get("bands", ["UNKNOWN"])[0] if cell.get("bands") else "UNKNOWN"
                return {
                    "network_type": cell.get("type", "UNKNOWN").upper(),
                    "rsrp_dbm": rsrp,
                    "rsrq_db": rsrq,
                    "band": band,
                    "status": "PASS"
                }
        return {"status": "FAIL", "error": "No registered cell"}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}
'''

if "def audit_cellular" not in code:
    code = code.replace("def audit_network", func.strip() + "\n\ndef audit_network")
    code = code.replace('"download_metrics": download_metrics,', '"download_metrics": download_metrics,\n        "cellular_metrics": audit_cellular(),')
    with open('grd_mobile_audit.py', 'w') as f:
        f.write(code)
    print("Successfully injected cellular telemetry into grd_mobile_audit.py")
else:
    print("Module already patched.")