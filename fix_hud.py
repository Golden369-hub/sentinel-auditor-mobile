import re
with open('index.html', 'r') as f:
    html = f.read()

# 1. Recalibrate HUD clipping for responsive mobile width
html = re.sub(
    r'clip-path:[^;]+;',
    r'clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 0 100%);',
    html
)

# 2. Elevate Buttons above scanline overlays
html = re.sub(r'(\.btn-run\s*\{)', r'\1 position: relative; z-index: 1000; ', html)
html = re.sub(r'(\.btn-export\s*\{)', r'\1 position: relative; z-index: 1000; ', html)

# 3. Aggressively kill the Service Worker and bypass cache
html = html.replace("navigator.serviceWorker.register('/sw.js')", "console.log('SW Purged');")
sw_killer = """
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(r => r.forEach(x => x.unregister()));
}
"""
if 'getRegistrations' not in html:
    html = html.replace('<script>', '<script>\n' + sw_killer)

# 4. Inject JS Error Trap directly to the HUD Terminal
js_trap = """
window.onerror = function(m, s, l, c, e) {
    const t = document.getElementById('term');
    if(t) {
        t.innerHTML += '<br><span style="color:#ff3344">FATAL // ' + m + ' (Line ' + l + ')</span>';
        t.scrollTop = t.scrollHeight;
    }
};
"""
if 'window.onerror' not in html:
    html = html.replace('<script>', '<script>\n' + js_trap)

with open('index.html', 'w') as f:
    f.write(html)
with open('www/index.html', 'w') as f:
    f.write(html)
print("[+] HUD Graphics and Interaction Links Hardened.")
