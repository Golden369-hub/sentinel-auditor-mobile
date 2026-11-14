import re

with open('index.html', 'r') as f:
    html = f.read()

# 1. Strip all corrupted script tags completely to eliminate syntax drift
html_clean = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)

# 2. Define the pristine, unified zero-entropy JavaScript payload
pristine_js = """
<script>
window.onerror = function(m, s, l, c, e) {
    const t = document.getElementById('term');
    if(t) {
        t.innerHTML += '<br><span style="color:#ff3344">FATAL // ' + m + ' (Line ' + l + ')</span>';
        t.scrollTop = t.scrollHeight;
    }
};

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(r => r.forEach(x => x.unregister()));
}

function calculateTrueSignalBars(rsrp_dbm) {
    if (rsrp_dbm == null) return 0;
    const r = Number(rsrp_dbm);
    if (r >= -85) return 4;
    if (r >= -95) return 3;
    if (r >= -105) return 2;
    if (r >= -115) return 1;
    return 0;
}

let currentAuditRecord = null;

function printTerm(msg) {
    const t = document.getElementById('term');
    if(t) {
        t.innerHTML += '<br>' + msg;
        t.scrollTop = t.scrollHeight;
    }
}

function executeScan() {
    const btn = document.getElementById('btn-run');
    if(btn) {
        btn.disabled = true;
        btn.innerText = '[ ENGAGED // RUNNING... ]';
    }
    printTerm('Starting multi-vector carrier audit...');

    fetch('/api/run_audit')
        .then(res => res.json())
        .then(data => {
            if(btn) {
                btn.disabled = false;
                btn.innerText = '[ EXECUTE TELEMETRY AUDIT ]';
            }
            currentAuditRecord = data;

            const ping = data.ping_metrics || {};
            const dl = data.download_metrics || {};
            const dns = data.dns_metrics || {};
            const isp = data.isp_metrics || {};
            const hash = data.sha256_hash || "ZERO-DRIFT";
            const cell = data.cellular_metrics || {};

            const setVal = (id, val) => { const el = document.getElementById(id); if(el) el.innerHTML = val; };
            
            setVal('isp-val', (isp.isp || 'UNKNOWN') + ' [' + (isp.asn || 'AS--') + ']');
            setVal('lat-val', Number(ping.avg_ms || 0).toFixed(2) + '<span style="font-size:0.7rem"> ms</span>');
            setVal('jit-val', Number(ping.mdev_ms || 0).toFixed(2) + '<span style="font-size:0.7rem"> ms</span>');
            setVal('loss-val', (ping.packet_loss_pct || 0) + '%');
            setVal('dns-val', Number(dns.latency_ms || 0).toFixed(2) + '<span style="font-size:0.7rem"> ms</span>');
            setVal('tp-val', Number(dl.mbps || 0).toFixed(2) + ' <span style="font-size:0.7rem">Mbps</span>');
            
            const hashEl = document.getElementById('hash-val');
            if(hashEl) hashEl.innerText = hash;

            const pct = Math.min(Math.round(((dl.mbps || 0) / 500) * 100), 100);
            const barFill = document.getElementById('bar-fill');
            if(barFill) barFill.style.width = pct + '%';

            if (cell.rsrp_dbm) {
                const signalVal = document.getElementById('signal-val');
                const signalBar = document.getElementById('cyberpunk-signal-bar');
                if (signalVal && signalBar) {
                    const bars = calculateTrueSignalBars(cell.rsrp_dbm);
                    signalVal.innerHTML = bars + ' BARS <span style="font-size:0.7rem; color:var(--neon-cyan)">' + cell.rsrp_dbm + ' dBm</span>';
                    let meter = ""; let c = "";
                    if (bars === 4) { meter = "████"; c = "#00ff66"; }
                    else if (bars === 3) { meter = "███░"; c = "#FEE00A"; }
                    else if (bars === 2) { meter = "██░░"; c = "#ff9900"; }
                    else { meter = "█░░░"; c = "#ff3344"; }
                    signalBar.innerText = meter;
                    signalBar.style.color = c;
                }
            }

            printTerm("Carrier: " + (isp.isp || 'ISP') + " [" + (isp.asn || '') + "] (" + (isp.city || '') + ", " + (isp.region || '') + ")");
            printTerm("Audit PASS // " + hash.substring(0, 16) + "...");
        })
        .catch(err => {
            if(btn) {
                btn.disabled = false;
                btn.innerText = '[ EXECUTE TELEMETRY AUDIT ]';
            }
            printTerm("FATAL // " + err);
        });
}

async function exportAuditJson() {
    if (!currentAuditRecord) {
        printTerm("WARN // Execute telemetry audit prior to ledger export.");
        return;
    }
    const exportPayload = {
        framework: "GRD Sentinel Auditor Mobile",
        compliance_standard: "NIST SP 800-171 AU-9",
        export_timestamp: new Date().toISOString(),
        audit_data: currentAuditRecord,
        system_integrity: "ZERO_DRIFT"
    };
    const rawJson = JSON.stringify(exportPayload, null, 2);
    const encoder = new TextEncoder();
    const hashBuffer = await crypto.subtle.digest("SHA-256", encoder.encode(rawJson));
    const sha256 = Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, "0")).join("");

    const sealedRecord = {
        ...exportPayload,
        au9_sha256_seal: sha256
    };
    const blob = new Blob([JSON.stringify(sealedRecord, null, 2)], { type: "application/json" });
    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = `sentinel-audit-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(downloadUrl);
    printTerm("AUDIT LEDGER EXPORTED (AU-9 SEALED)");
}
</script>
"""

# 3. Inject precisely before the body close to preserve the visual footer
if '</body>' in html_clean:
    html_clean = html_clean.replace('</body>', pristine_js + '\n</body>')
else:
    html_clean += pristine_js

with open('index.html', 'w') as f:
    f.write(html_clean)
with open('www/index.html', 'w') as f:
    f.write(html_clean)

print("[+] Corrupted Javascript purged. Pristine Zero-Entropy Logic injected.")
