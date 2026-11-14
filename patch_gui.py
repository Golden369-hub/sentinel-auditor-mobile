import re

with open('index.html', 'r') as f:
    html = f.read()

# 1. Inject True Signal Cyberpunk Card into the Grid
signal_card = """
        <div class="card card-wide">
            <div class="card-lbl">True Signal RSRP // Bars</div>
            <div class="card-val" id="signal-val">STANDBY <span style="font-size:0.7rem; color:var(--neon-cyan)">-- dBm</span></div>
            <div id="cyberpunk-signal-bar" style="font-size: 1.2rem; margin-top: 4px; letter-spacing: 2px;"></div>
        </div>
"""
if 'True Signal RSRP' not in html:
    html = html.replace('<!-- SIGNAL_INJECT -->', signal_card)
    # If the placeholder isn't there, inject before Throughput
    if '<!-- SIGNAL_INJECT -->' not in html:
        html = html.replace('<div class="card card-wide">\n            <div class="card-lbl">Throughput Goodput</div>', signal_card + '\n        <div class="card card-wide">\n            <div class="card-lbl">Throughput Goodput</div>')

# 2. Update Fetch Logic to map cellular_metrics
fetch_logic = """
            const dl = data.download_metrics || {};
            const cell = data.cellular_metrics || {};
"""
html = re.sub(r'const dl = data\.download_metrics \|\| \{\};', fetch_logic, html)

# 3. Update DOM rendering for the new signal card
dom_update = """
            document.getElementById('tp-val').innerHTML = Number(dl.mbps || 0).toFixed(2) + ' <span style="font-size:0.7rem">Mbps</span>';
            
            // True Signal UI Update
            if(cell.rsrp_dbm) {
                const signalVal = document.getElementById('signal-val');
                const signalBar = document.getElementById('cyberpunk-signal-bar');
                const bars = calculateTrueSignalBars(cell.rsrp_dbm);
                
                signalVal.innerHTML = bars + ' BARS <span style="font-size:0.7rem; color:var(--neon-cyan)">' + cell.rsrp_dbm + ' dBm</span>';
                
                let meter = "";
                let color = "";
                if(bars === 4) { meter = "████"; color = "#00ff66"; } // Optimal (Neon Cyan/Green)
                else if(bars === 3) { meter = "███░"; color = "#FEE00A"; } // Good (Neon Yellow)
                else if(bars === 2) { meter = "██░░"; color = "#ff9900"; } // Marginal (Orange)
                else { meter = "█░░░"; color = "#ff3344"; } // Critical (Neon Red)
                
                signalBar.innerText = meter;
                signalBar.style.color = color;
            }
"""
html = re.sub(r'document\.getElementById\(\'tp-val\'\)\.innerHTML = Number\(dl\.mbps \|\| 0\)\.toFixed\(2\) \+ \' <span style="font-size:0\.7rem">Mbps</span>\';', dom_update, html)

with open('index.html', 'w') as f:
    f.write(html)

print("GUI patched successfully.")
