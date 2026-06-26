#!/usr/bin/env python3
"""Generate assets/06-activity.svg from a user's PUBLIC GitHub contribution graph.

Scrapes https://github.com/users/<login>/contributions (the same calendar GitHub
shows on the public profile, which includes anonymized private contributions when
the user has "Include private contributions on my profile" enabled) and renders an
animated heat-map SVG in the Anthropic/Claude palette. Cells sweep in column by
column on load (CSS @keyframes, so the motion survives GitHub's <img> sanitizing).

Usage: python3 scripts/gen_activity.py [login] [out_path]
"""
import sys, re, datetime, urllib.request

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "PaulCheng1122"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/06-activity.svg"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

# ---- fetch ----
req = urllib.request.Request(
    f"https://github.com/users/{LOGIN}/contributions", headers={"User-Agent": UA})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")

# ---- parse day cells (id, date, level) ----
cells = []
for tag in re.findall(r'<td\b[^>]*class="ContributionCalendar-day"[^>]*>', html):
    d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
    lv = re.search(r'data-level="(\d)"', tag)
    cid = re.search(r'id="([^"]+)"', tag)
    if d and lv:
        cells.append((cid.group(1) if cid else "", d.group(1), int(lv.group(1))))

# ---- parse counts from tool-tips (for the total) ----
counts = {}
for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
    m = re.match(r'\s*([\d,]+)\s+contribution', text)
    counts[cid] = int(m.group(1).replace(",", "")) if m else 0
total = sum(counts.values())

# ---- geometry ----
dates = [datetime.date.fromisoformat(d) for _, d, _ in cells]
row_of = lambda dt: dt.isoweekday() % 7            # Sun=0 .. Sat=6
anchor = min(dates) - datetime.timedelta(days=row_of(min(dates)))  # Sunday of first column

CELL, GAP = 11, 3
STEP = CELL + GAP
GX, GY = 120, 150                                   # grid origin
RAMP = ["#e9e5d8", "#c6d8a6", "#93bd68", "#5e9a43", "#3a6b28"]

rects = []
max_col = 0
for _, ds, lv in cells:
    dt = datetime.date.fromisoformat(ds)
    col = (dt - anchor).days // 7
    row = row_of(dt)
    max_col = max(max_col, col)
    x = GX + col * STEP
    y = GY + row * STEP
    delay = round(0.30 + col * 0.018, 3)
    rects.append(
        f'<rect class="cell" style="animation-delay:{delay}s" x="{x}" y="{y}" '
        f'width="{CELL}" height="{CELL}" rx="2" fill="{RAMP[lv]}"/>')

# ---- month labels ----
MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
month_labels, last_m, last_c = [], None, -3
for col in range(max_col + 1):
    first = anchor + datetime.timedelta(days=col * 7)
    if first.month != last_m and col - last_c >= 3:
        x = GX + col * STEP
        month_labels.append(
            f'<text class="lbl" x="{x}" y="{GY-12}" font-size="12" fill="#8a8780">{MON[first.month-1]}</text>')
        last_m, last_c = first.month, col

# ---- weekday labels ----
wk = []
for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    y = GY + r * STEP + 9
    wk.append(f'<text class="lbl" x="100" y="{y}" font-size="11" fill="#8a8780" text-anchor="end">{name}</text>')

# ---- legend ----
gx0 = GX + (max_col - 4) * STEP - 86
ly = GY + 7 * STEP + 16
legend = [f'<text class="lbl" x="{gx0-8}" y="{ly+9}" font-size="11" fill="#8a8780" text-anchor="end">Less</text>']
for i, c in enumerate(RAMP):
    legend.append(f'<rect x="{gx0 + i*16}" y="{ly}" width="11" height="11" rx="2" fill="{c}"/>')
legend.append(f'<text class="lbl" x="{gx0 + 5*16 + 4}" y="{ly+9}" font-size="11" fill="#8a8780">More</text>')

H = ly + 30
svg = f'''<svg viewBox="0 0 1200 {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
<title id="t">GitHub activity</title>
<desc id="d">{total} contributions over the last year, shown as a heat-map that animates in column by column.</desc>
<style>
  .serif{{font-family:Georgia,Charter,"Iowan Old Style","Times New Roman",serif}}
  .mono{{font-family:"SF Mono","DM Mono","JetBrains Mono",ui-monospace,Menlo,monospace}}
  .lbl{{font-family:"SF Mono","DM Mono",ui-monospace,Menlo,monospace}}
  .rise{{opacity:0;animation:rise .75s cubic-bezier(.25,1,.5,1) both}}
  @keyframes rise{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
  .cell{{transform-box:fill-box;transform-origin:center;opacity:0;animation:cin .5s cubic-bezier(.25,1,.5,1) both}}
  @keyframes cin{{from{{opacity:0;transform:scale(.3)}}to{{opacity:1;transform:scale(1)}}}}
</style>
<rect width="1200" height="{H}" rx="16" fill="#faf9f5"/>
<text class="mono rise" style="animation-delay:.05s" x="56" y="58" font-size="12" letter-spacing="2" fill="#5e5d59">LAST YEAR ON GITHUB</text>
<text class="serif rise" style="animation-delay:.12s" x="54" y="104" font-size="34" fill="#141413">{total} contributions</text>
<g>{''.join(month_labels)}</g>
<g>{''.join(wk)}</g>
<g>{''.join(rects)}</g>
<g class="rise" style="animation-delay:1.2s">{''.join(legend)}</g>
</svg>
'''

with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}: total={total}, cells={len(cells)}, cols={max_col+1}, height={H}")
