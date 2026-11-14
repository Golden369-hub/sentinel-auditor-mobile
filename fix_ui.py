import re
with open('index.html', 'r') as f:
    html = f.read()

# 1. Fix CSS Layout Squish (Force Vertical Column Stack)
html = re.sub(
    r'display:\s*flex;\s*justify-content:\s*center;',
    r'display: flex; flex-direction: column; align-items: center; justify-content: flex-start; overflow-x: hidden;',
    html
)

# 2. Inject True Signal Math directly to prevent JS 404 errors on the browser
js_func = """
function calculateTrueSignalBars(rsrp_dbm) {
    if (rsrp_dbm == null) return 0;
    const r = Number(rsrp_dbm);
    if (r >= -85) return 4;
    if (r >= -95) return 3;
    if (r >= -105) return 2;
    if (r >= -115) return 1;
    return 0;
}
"""
if 'function calculateTrueSignalBars' not in html:
    html = html.replace('let currentAuditRecord = null;', js_func + '\nlet currentAuditRecord = null;')

with open('index.html', 'w') as f:
    f.write(html)
print("[+] UI and JS Logic patched for zero-drift.")
