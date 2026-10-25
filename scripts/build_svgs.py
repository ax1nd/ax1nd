import sys
sys.path.insert(0, "scripts")
from generate_contributions import crt

GLYPHS = {
 "A": ["01110","10001","10001","11111","10001","10001","10001"],
 "R": ["11110","10001","10001","11110","10100","10010","10001"],
 "V": ["10001","10001","10001","10001","10001","01010","00100"],
 "I": ["11111","00100","00100","00100","00100","00100","11111"],
 "N": ["10001","11001","10101","10011","10001","10001","10001"],
 "D": ["11110","10001","10001","10001","10001","10001","11110"],
}
INVADER = ["00100000100","00010001000","00111111100","01101110110",
           "11111111111","10111111101","10100000101","00011011000"]

def pixels(rows, x0, y0, px, cls="t", delay0=0.0, per_col=0.0, extra=""):
    out = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "1":
                d = round(delay0 + c * per_col, 3)
                st = f' style="opacity:0;animation:p .15s {d}s forwards"' if per_col else ""
                out.append(f'<rect class="{cls}" x="{x0+c*px}" y="{y0+r*px}" width="{px-1}" height="{px-1}"{st}/>')
    return "".join(out)

# ---------- whoami ----------
W, H = 820, 430
b = ['<style>@keyframes p{to{opacity:1}} '
     '@keyframes ty{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}} '
     '@keyframes bob{50%{transform:translateY(6px)}} .inv{animation:bob 1.2s steps(2) infinite}</style>']
b.append('<text x="34" y="82" class="d" font-size="11">ARVIND-OS (R) v1.0   MEMORY CHECK: 640K OK   DISK: READY</text>')
x = 44
for i, ch in enumerate("ARVIND"):
    b.append(pixels(GLYPHS[ch], x, 100, 9, delay0=0.2 + i*0.25, per_col=0.04))
    x += 54
b.append(f'<g class="inv">{pixels(INVADER, 664, 104, 8)}</g>')
b.append('<text x="44" y="190" class="d" font-size="13" style="animation:ty 1.2s steps(30) 1.9s backwards">&gt; FULL-STACK DEVELOPER // BUILDER // NEVER SETTLING</text>')
rows = [("NAME", "ARVIND"), ("LOCATION", "CHENNAI, INDIA"), ("ROLE", "DEVELOPER &amp; BUILDER"),
        ("STATUS", "ONLINE - SHIPPING CODE"), ("MOTTO", "NEVER SETTLE.")]
y, t = 232, 3.2
for k, v in rows:
    dots = "." * (12 - len(k))
    b.append(f'<text x="44" y="{y}" font-size="15" style="animation:ty 1s steps(28) {t}s backwards">'
             f'<tspan class="d">{k} {dots} </tspan><tspan class="t">{v}</tspan></text>')
    y += 28; t += 1.0
b.append(f'<text x="44" y="{y+22}" font-size="15" class="t">C:\\ARVIND&gt;<tspan class="blink"> █</tspan></text>')
open("assets/whoami.svg", "w").write(crt(W, H, "ARVIND-OS ▸ WHOAMI.EXE", "\n".join(b)))

# ---------- stack ----------
cats = [("FRONTEND", ["REACT", "TYPESCRIPT", "TAILWIND", "VITE"]),
        ("BACKEND", ["NODE.JS", "EXPRESS", "MYSQL", "FASTAPI"]),
        ("ML/DATA", ["PYTHON", "SCIKIT-LEARN", "PYTORCH", "PANDAS"])]
b = ['<style>@keyframes p{to{opacity:1}}</style>', '<text x="34" y="86" class="t" font-size="14">C:\\ARVIND&gt; STACK --LIST</text>']
y, d = 120, 0.3
for name, tags in cats:
    b.append(f'<text x="44" y="{y+16}" class="d" font-size="12">{name}</text>')
    x = 160
    for tg in tags:
        wd = int(len(tg) * 8.4 + 24)
        b.append(f'<g style="opacity:0;animation:p .2s {d}s forwards"><rect x="{x}" y="{y}" width="{wd}" height="24" fill="none" stroke="{"#33ff66"}" stroke-width="1.5"/>'
                 f'<text x="{x+wd/2}" y="{y+16}" text-anchor="middle" class="t" font-size="12">{tg}</text></g>')
        x += wd + 12; d += 0.15
    y += 44
b.append(f'<text x="34" y="{y+22}" font-size="13"><tspan class="t">&gt; 12 MODULES LOADED. READY</tspan><tspan class="t blink"> █</tspan></text>')
open("assets/stack.svg", "w").write(crt(W, 320, "ARVIND-OS ▸ STACK.EXE", "\n".join(b)))
