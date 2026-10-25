#!/usr/bin/env python3
"""Generate assets/contributions.svg: a retro-CRT contribution grid.

Usage:
  GH_TOKEN=... GH_USER=you python scripts/generate_contributions.py
  python scripts/generate_contributions.py --demo      # fake data, no token
"""
import datetime, json, os, random, sys, urllib.request

USER = os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "arvind"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = "assets/contributions.svg"

GREEN, DIM = "#33ff66", "#1fa84a"
COLORS = ["#0b2413", "#0f5c25", "#14a037", "#2fe05b", "#9dffb4"]
FONT = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,'Courier New',monospace"


def crt(w, h, title, body):
    """Wrap SVG body markup in a retro CRT monitor (bezel, glow, scanlines, vignette, flicker)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}" font-weight="700">
<defs>
  <filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="2" fill="#000" opacity=".3"/></pattern>
  <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".8"/></radialGradient>
  <linearGradient id="band" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".07"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
  <clipPath id="scr"><rect x="14" y="14" width="{w-28}" height="{h-28}" rx="22"/></clipPath>
</defs>
<style>
  .t{{fill:{GREEN}}} .d{{fill:{DIM}}}
  .flick{{animation:flick 4s infinite}}
  @keyframes flick{{0%,100%{{opacity:1}}48%{{opacity:1}}50%{{opacity:.93}}52%{{opacity:1}}54%{{opacity:.96}}}}
  .band{{animation:roll 6s linear infinite}}
  @keyframes roll{{from{{transform:translateY(-90px)}}to{{transform:translateY({h}px)}}}}
  .blink{{animation:blink 1s steps(1) infinite}}
  @keyframes blink{{50%{{opacity:0}}}}
</style>
<rect width="{w}" height="{h}" rx="28" fill="#161616"/>
<rect x="2" y="2" width="{w-4}" height="{h-4}" rx="26" fill="none" stroke="#2c2c2c" stroke-width="2"/>
<rect x="14" y="14" width="{w-28}" height="{h-28}" rx="22" fill="#010b04"/>
<g clip-path="url(#scr)" class="flick">
  <g filter="url(#glow)">
    <text x="34" y="46" class="t" font-size="13" letter-spacing="1.5">{title}</text>
    <text x="{w-34}" y="46" class="d" font-size="12" text-anchor="end">● REC  60Hz</text>
    <rect x="34" y="56" width="{w-68}" height="2" fill="{DIM}" opacity=".7"/>
    {body}
  </g>
  <rect x="14" y="14" width="{w-28}" height="{h-28}" fill="url(#scan)"/>
  <rect class="band" x="14" y="14" width="{w-28}" height="90" fill="url(#band)"/>
  <rect x="14" y="14" width="{w-28}" height="{h-28}" fill="url(#vig)"/>
</g>
<rect x="14" y="14" width="{w-28}" height="{h-28}" rx="22" fill="none" stroke="#0c3a1a" stroke-width="2"/>
</svg>'''


QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [[(d["date"], d["contributionCount"]) for d in w["contributionDays"]] for w in cal["weeks"]]
    return weeks, cal["totalContributions"]


def demo():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=364 + (today.weekday() + 1) % 7)
    weeks, total, d = [], 0, start
    while d <= today:
        week = []
        for _ in range(7):
            n = 0 if d > today else random.choice([0, 0, 0, 1, 2, 3, 5, 8, 12])
            total += n
            week.append((d.isoformat(), n))
            d += datetime.timedelta(days=1)
        weeks.append(week)
    return weeks, total


def streaks(weeks):
    days = [c for w in weeks for (dt, c) in w if dt <= datetime.date.today().isoformat()]
    longest = run = 0
    for c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, rev = 0, list(reversed(days))
    if rev and rev[0] == 0:
        rev = rev[1:]
    for c in rev:
        if not c:
            break
        cur += 1
    return cur, longest


def level(n, mx):
    if n == 0:
        return 0
    return min(4, 1 + int((n - 1) / max(mx / 4, 1)))


def render(weeks, total):
    cell, step, left, top = 11, 14, 72, 96
    width = left + len(weeks) * step + 42
    height = top + 7 * step + 78
    mx = max((c for w in weeks for _, c in w), default=1)
    cur, longest = streaks(weeks)
    o = []
    last, last_i = None, -9
    for i, w in enumerate(weeks):
        m = datetime.date.fromisoformat(w[0][0]).strftime("%b").upper()
        if m != last and i - last_i >= 3:
            last_i = i
            o.append(f'<text x="{left + i*step}" y="{top-8}" class="d" font-size="10">{m}</text>')
        last = m
    for r, label in ((1, "MON"), (3, "WED"), (5, "FRI")):
        o.append(f'<text x="34" y="{top + r*step + 9}" class="d" font-size="10">{label}</text>')
    for i, w in enumerate(weeks):
        delay = round(i * 0.02, 3)
        for r, (dt, n) in enumerate(w):
            o.append(f'<rect style="opacity:0;animation:p .2s {delay}s forwards" x="{left+i*step}" y="{top+r*step}" '
                     f'width="{cell}" height="{cell}" fill="{COLORS[level(n, mx)]}"><title>{n} on {dt}</title></rect>')
    y = height - 38
    o.append(f'<style>@keyframes p{{to{{opacity:1}}}}</style>')
    o.append(f'<text x="34" y="{y}" font-size="12"><tspan class="t">&gt; {total}</tspan><tspan class="d"> COMMITS/12MO  |  STREAK </tspan>'
             f'<tspan class="t">{cur}D</tspan><tspan class="d">  |  BEST </tspan><tspan class="t">{longest}D</tspan>'
             f'<tspan class="t blink"> █</tspan></text>')
    lx = width - 34 - 5 * 14 - 74
    o.append(f'<text x="{lx}" y="{y}" class="d" font-size="10">LESS</text>')
    for i, col in enumerate(COLORS):
        o.append(f'<rect x="{lx+36+i*14}" y="{y-10}" width="11" height="11" fill="{col}"/>')
    o.append(f'<text x="{lx+36+5*14+4}" y="{y}" class="d" font-size="10">MORE</text>')
    return crt(width, height, f"ARVIND-OS ▸ CONTRIBUTIONS.EXE", "\n".join(o))


if __name__ == "__main__":
    if "--demo" in sys.argv:
        weeks, total = demo()
    else:
        if not TOKEN:
            sys.exit("Set GH_TOKEN (or run with --demo)")
        weeks, total = fetch()
    os.makedirs("assets", exist_ok=True)
    open(OUT, "w").write(render(weeks, total))
    print(f"wrote {OUT} ({total} contributions)")
