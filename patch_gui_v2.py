import re

with open('index.html', 'r') as f:
    html = f.read()

# 1. Inject UI Element safely before the Ledger card
html = re.sub(
    r'(<div class="card-lbl"[^>]*>Telemetry SHA-256 Ledger</div>)',
    r'<div class="card card-wide">\n<div class="card-lbl">True Signal RSRP // Bars</div>\n<div class="card-val" id="signal-val">STANDBY <span style="font-size:0.7rem; color:var(--neon-cyan)">-- dBm</span></div>\n<div id="cyberpunk-signal-bar" style="font-size: 1.2rem; margin-top: 4px; letter-spacing: 2px;"></div>\n</div>\n\1',
    html
)

# 2. Add cellular metrics array to fetch logic
html = re.sub(
    r'(const dl = data\.download_metrics \|\| \{\};)',
    r'\1\nconst cell = data.cellular_metrics || {};',
    html
)

# 3. Add DOM update logic safely after the progress bar calculation
dom_logic = r"""\1
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
"""
html = re.sub(r'(document\.getElementById\(\'bar-fill\'\)\.style\.width = pct \+ \'%\';)', dom_logic, html)

with open('index.html', 'w') as f:
    f.write(html)
