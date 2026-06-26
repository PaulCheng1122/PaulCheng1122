#!/usr/bin/env python3
"""Generate a SINGLE seamless profile SVG (assets/profile.svg).

All sections are full-width bands that touch edge to edge inside one rounded
frame, so the README reads as one continuous surface instead of separate cards.
The contribution heat-map band is built from the live public contribution graph
(includes anonymized private contributions when that profile setting is on).

Usage: python3 scripts/gen_profile.py [login] [out_path]
"""
import sys, re, datetime, urllib.request

LOGIN = sys.argv[1] if len(sys.argv) > 1 else "PaulCheng1122"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/profile.svg"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")

# ---- band layout (full width 1200; bands stack flush, no gaps) ----
HERO_H, SAND_H, SAGE_H, LAV_H, ACT_H, MARQ_H = 360, 330, 320, 320, 290, 104
HERO_Y = 0
SAND_Y = HERO_Y + HERO_H
SAGE_Y = SAND_Y + SAND_H
LAV_Y  = SAGE_Y + SAGE_H
ACT_Y  = LAV_Y + LAV_H
MARQ_Y = ACT_Y + ACT_H
TOTAL  = MARQ_Y + MARQ_H

# ============================ static section fragments ============================
HERO = '''
<text class="mono rise" style="animation-delay:.05s" x="64" y="74" font-size="13" letter-spacing="2.5" fill="#5e5d59">AI ENGINEERING — FULL-STACK TYPESCRIPT</text>
<text class="serif" x="60" y="196" font-size="78" letter-spacing="-2" fill="#141413"><tspan class="word" style="animation-delay:.18s">Paul</tspan> <tspan class="word" style="animation-delay:.38s">Cheng</tspan></text>
<rect class="acc" style="animation-delay:.55s" x="64" y="222" width="104" height="5" rx="2.5" fill="#d97757"/>
<text class="sans rise" style="animation-delay:.66s" x="64" y="280" font-size="23" fill="#30302e">Turning AI demos into repeatable production practice.</text>
<text class="mono rise" style="animation-delay:1.05s" x="64" y="334" font-size="14" fill="#898781">github.com/PaulCheng1122<tspan fill="#cfccc3">   ·   </tspan><tspan fill="#d97757">building in production →</tspan></text>
<g>
  <path class="ln" pathLength="1" style="animation-delay:.55s" d="M1030 165 Q1066 163 1098 166"/>
  <path class="ln" pathLength="1" style="animation-delay:.61s" d="M1030 165 Q1058 138 1079 116"/>
  <path class="ln" pathLength="1" style="animation-delay:.67s" d="M1030 165 Q1027 129 1031 96"/>
  <path class="ln" pathLength="1" style="animation-delay:.73s" d="M1030 165 Q1000 140 981 117"/>
  <path class="ln" pathLength="1" style="animation-delay:.79s" d="M1030 165 Q994 168 962 164"/>
  <path class="ln" pathLength="1" style="animation-delay:.85s" d="M1030 165 Q1001 192 982 214"/>
  <path class="ln" pathLength="1" style="animation-delay:.91s" d="M1030 165 Q1033 201 1029 234"/>
  <path class="ln" pathLength="1" style="animation-delay:.97s" d="M1030 165 Q1059 190 1079 213"/>
  <circle class="dot" style="animation-delay:1.22s" cx="1079" cy="116" r="6" fill="#d97757"/>
  <circle class="dot" style="animation-delay:1.32s" cx="962" cy="164" r="6" fill="#d97757"/>
  <circle class="dot" style="animation-delay:1.42s" cx="1029" cy="234" r="6" fill="#d97757"/>
</g>'''

SAND = '''
<text class="mono rise" style="animation-delay:.05s" x="48" y="60" font-size="12" letter-spacing="2" fill="#5e5d59">WHAT I BUILD</text>
<text class="serif rise" style="animation-delay:.12s" x="46" y="110" font-size="36" fill="#141413">Turning AI demos into production</text>
<g class="card" style="animation-delay:.22s">
  <rect x="48" y="142" width="352" height="158" rx="8" fill="#19191919"/>
  <text class="mono" x="74" y="178" font-size="11" letter-spacing="1.5" fill="#5e5d59">01 · LLM APPS</text>
  <text class="serif" x="73" y="210" font-size="21" fill="#141413">Streaming + RAG</text>
  <text class="sans" x="74" y="242" font-size="14" fill="#30302e">Function-calling, tool-use, and</text>
  <text class="sans" x="74" y="263" font-size="14" fill="#30302e">DONE-signal parsing over fully</text>
  <text class="sans" x="74" y="284" font-size="14" fill="#30302e">observable model calls.</text>
</g>
<g class="card" style="animation-delay:.30s">
  <rect x="424" y="142" width="352" height="158" rx="8" fill="#19191919"/>
  <text class="mono" x="450" y="178" font-size="11" letter-spacing="1.5" fill="#5e5d59">02 · ROUTING</text>
  <text class="serif" x="449" y="210" font-size="21" fill="#141413">Multi-model</text>
  <text class="sans" x="450" y="242" font-size="14" fill="#30302e">Qwen, GLM, DeepSeek, DashScope</text>
  <text class="sans" x="450" y="263" font-size="14" fill="#30302e">and OpenRouter behind a single</text>
  <text class="sans" x="450" y="284" font-size="14" fill="#30302e">routing layer.</text>
</g>
<g class="card" style="animation-delay:.38s">
  <rect x="800" y="142" width="352" height="158" rx="8" fill="#19191919"/>
  <text class="mono" x="826" y="178" font-size="11" letter-spacing="1.5" fill="#5e5d59">03 · SIGNALS</text>
  <text class="serif" x="825" y="210" font-size="21" fill="#141413">Observability</text>
  <text class="sans" x="826" y="242" font-size="14" fill="#30302e">Logged calls, latency, tokens</text>
  <text class="sans" x="826" y="263" font-size="14" fill="#30302e">and tool traces you can open</text>
  <text class="sans" x="826" y="284" font-size="14" fill="#30302e">up and inspect.</text>
</g>'''

SAGE = '''
<text class="mono rise" style="animation-delay:.05s" x="48" y="60" font-size="12" letter-spacing="2" fill="#30302e">HOW I WORK</text>
<text class="serif rise" style="animation-delay:.12s" x="46" y="110" font-size="34" fill="#141413">Engineering style</text>
<g class="sans" font-size="16.5" fill="#1f2420">
  <g class="rise" style="animation-delay:.24s"><circle cx="54" cy="151" r="4" fill="#d97757"/><text x="74" y="156">Product thinking before implementation detail.</text></g>
  <g class="rise" style="animation-delay:.33s"><circle cx="54" cy="189" r="4" fill="#d97757"/><text x="74" y="194">Small, reviewable changes over big rewrites.</text></g>
  <g class="rise" style="animation-delay:.42s"><circle cx="54" cy="227" r="4" fill="#d97757"/><text x="74" y="232">Explicit architecture decisions through ADRs.</text></g>
  <g class="rise" style="animation-delay:.51s"><circle cx="54" cy="265" r="4" fill="#d97757"/><text x="74" y="270">AI as engineering leverage, not a shortcut.</text></g>
</g>
<g transform="translate(40,-10)">
  <path class="draw" pathLength="1" style="animation-delay:.5s"  d="M946 118 Q1006 150 1066 132"/>
  <path class="draw" pathLength="1" style="animation-delay:.7s"  d="M952 132 Q940 200 996 256"/>
  <path class="draw" pathLength="1" style="animation-delay:.9s"  d="M1066 146 Q1086 210 1018 256"/>
  <circle class="draw" pathLength="1" style="animation-delay:1.05s" cx="946" cy="120" r="26"/>
  <circle class="draw" pathLength="1" style="animation-delay:1.2s"  cx="1074" cy="134" r="26"/>
  <circle class="draw" pathLength="1" style="animation-delay:1.35s" cx="1006" cy="262" r="26"/>
  <circle class="dot" style="animation-delay:1.7s" cx="946" cy="120" r="7" fill="#d97757"/>
</g>'''

LAV = '''
<g transform="translate(0,-6)">
  <path class="draw" pathLength="1" style="animation-delay:.45s" d="M120 96 L360 96 Q380 96 380 116 L380 250 Q380 270 360 270 L120 270 Q100 270 100 250 L100 116 Q100 96 120 96 Z"/>
  <path class="draw" pathLength="1" style="animation-delay:1.05s" d="M100 138 L380 138"/>
  <circle class="draw" pathLength="1" style="animation-delay:1.2s" cx="124" cy="117" r="6"/>
  <circle class="draw" pathLength="1" style="animation-delay:1.28s" cx="146" cy="117" r="6"/>
  <circle class="draw" pathLength="1" style="animation-delay:1.36s" cx="168" cy="117" r="6"/>
  <path class="draw" pathLength="1" style="animation-delay:1.45s" d="M126 174 L150 188 L126 202" stroke-width="5"/>
  <path class="draw" pathLength="1" style="animation-delay:1.6s" d="M166 204 L250 204" stroke-width="5"/>
  <path class="draw" pathLength="1" style="animation-delay:1.7s" d="M126 234 L300 234" stroke-width="5"/>
  <rect class="blink" x="312" y="222" width="16" height="20" fill="#d97757"/>
</g>
<text class="mono rise" style="animation-delay:.05s" x="470" y="92" font-size="12" letter-spacing="2" fill="#30302e">THE STACK</text>
<text class="serif rise" style="animation-delay:.12s" x="468" y="142" font-size="34" fill="#141413">Tools I reach for</text>
<g class="sans" font-size="16.5" fill="#1f2030">
  <text class="rise" style="animation-delay:.26s" x="470" y="188"><tspan fill="#5e5d59" class="mono" font-size="13">lang  </tspan>  TypeScript · JavaScript · Python · SQL</text>
  <text class="rise" style="animation-delay:.35s" x="470" y="222"><tspan fill="#5e5d59" class="mono" font-size="13">web   </tspan>  Next.js · React · Tailwind · Framer Motion</text>
  <text class="rise" style="animation-delay:.44s" x="470" y="256"><tspan fill="#5e5d59" class="mono" font-size="13">data  </tspan>  Node · Postgres · Prisma · FastAPI · MinIO</text>
  <text class="rise" style="animation-delay:.53s" x="470" y="290"><tspan fill="#5e5d59" class="mono" font-size="13">ops   </tspan>  Docker · AWS EC2 · pnpm · SSH deploy</text>
</g>'''

MARQUEE = '''
<rect x="0" y="0.5" width="1200" height="1" fill="#d8d4c7"/>
<rect x="0" y="102.5" width="1200" height="1" fill="#d8d4c7"/>
<g class="scroller"><use href="#m-trk" x="0"/><use href="#m-trk" x="2400"/></g>'''

# ============================ dynamic activity band ============================
def build_activity():
    req = urllib.request.Request(
        f"https://github.com/users/{LOGIN}/contributions", headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    cells = []
    for tag in re.findall(r'<td\b[^>]*class="ContributionCalendar-day"[^>]*>', html):
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        lv = re.search(r'data-level="(\d)"', tag)
        if d and lv:
            cells.append((d.group(1), int(lv.group(1))))
    counts = {}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r'\s*([\d,]+)\s+contribution', text)
        counts[cid] = int(m.group(1).replace(",", "")) if m else 0
    total = sum(counts.values())

    dates = [datetime.date.fromisoformat(d) for d, _ in cells]
    row_of = lambda dt: dt.isoweekday() % 7
    anchor = min(dates) - datetime.timedelta(days=row_of(min(dates)))
    CELL, STEP, GX, GY = 11, 14, 120, 150
    RAMP = ["#e9e5d8", "#c6d8a6", "#93bd68", "#5e9a43", "#3a6b28"]

    rects, max_col = [], 0
    for ds, lv in cells:
        dt = datetime.date.fromisoformat(ds)
        col, row = (dt - anchor).days // 7, row_of(dt)
        max_col = max(max_col, col)
        delay = round(0.30 + col * 0.018, 3)
        rects.append(f'<rect class="cell" style="animation-delay:{delay}s" x="{GX+col*STEP}" '
                     f'y="{GY+row*STEP}" width="{CELL}" height="{CELL}" rx="2" fill="{RAMP[lv]}"/>')

    MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    months, last_m, last_c = [], None, -3
    for col in range(max_col + 1):
        first = anchor + datetime.timedelta(days=col * 7)
        if first.month != last_m and col - last_c >= 3:
            months.append(f'<text class="lbl" x="{GX+col*STEP}" y="{GY-12}" font-size="12" fill="#8a8780">{MON[first.month-1]}</text>')
            last_m, last_c = first.month, col
    wk = []
    for r, name in ((1,"Mon"),(3,"Wed"),(5,"Fri")):
        wk.append(f'<text class="lbl" x="100" y="{GY+r*STEP+9}" font-size="11" fill="#8a8780" text-anchor="end">{name}</text>')
    gx0, ly = GX + (max_col-4)*STEP - 86, GY + 7*STEP + 16
    legend = [f'<text class="lbl" x="{gx0-8}" y="{ly+9}" font-size="11" fill="#8a8780" text-anchor="end">Less</text>']
    for i, c in enumerate(RAMP):
        legend.append(f'<rect x="{gx0+i*16}" y="{ly}" width="11" height="11" rx="2" fill="{c}"/>')
    legend.append(f'<text class="lbl" x="{gx0+5*16+4}" y="{ly+9}" font-size="11" fill="#8a8780">More</text>')

    inner = (f'<text class="mono rise" style="animation-delay:.05s" x="56" y="58" font-size="12" letter-spacing="2" fill="#5e5d59">LAST YEAR ON GITHUB</text>'
             f'<text class="serif rise" style="animation-delay:.12s" x="54" y="104" font-size="32" fill="#141413">{total} contributions</text>'
             f'<g>{"".join(months)}</g><g>{"".join(wk)}</g><g>{"".join(rects)}</g>'
             f'<g class="rise" style="animation-delay:1.2s">{"".join(legend)}</g>')
    return inner, total

ACT_INNER, TOTAL_C = build_activity()

# ============================ assemble one SVG ============================
M_TRK = ('<text id="m-trk" class="mono" y="62" font-size="17" textLength="2400" lengthAdjust="spacing">'
    + "".join(f'<tspan fill="#3d3d3a">{w}</tspan><tspan fill="#d97757">   •   </tspan>' for w in
        ["TypeScript","Next.js","React","Node.js","PostgreSQL","Prisma","Docker","FastAPI",
         "Python","RAG","function-calling","multi-model routing","LLM observability","prompt engineering"])
    + '</text>')

STYLE = '''
  .serif{font-family:Georgia,Charter,"Iowan Old Style","Times New Roman",serif}
  .sans{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
  .mono,.lbl{font-family:"SF Mono","DM Mono","JetBrains Mono",ui-monospace,Menlo,monospace}
  .rise{opacity:0;animation:rise .8s cubic-bezier(.25,1,.5,1) both}
  @keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
  .word{fill-opacity:0;animation:wfade 1s cubic-bezier(.25,1,.5,1) both}
  @keyframes wfade{to{fill-opacity:1}}
  .acc{transform-box:fill-box;transform-origin:left center;animation:grow .7s cubic-bezier(.25,1,.5,1) both}
  @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
  .ln{fill:none;stroke:#141413;stroke-width:5;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw .9s cubic-bezier(.25,1,.5,1) forwards}
  .draw{fill:none;stroke:#141413;stroke-width:6;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.45s cubic-bezier(.25,1,.5,1) forwards}
  @keyframes draw{to{stroke-dashoffset:0}}
  .dot{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop .5s cubic-bezier(.34,1.4,.5,1) both}
  @keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:scale(1)}}
  .card{opacity:0;animation:craise .45s cubic-bezier(.25,1,.5,1) both}
  @keyframes craise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
  .cell{transform-box:fill-box;transform-origin:center;opacity:0;animation:cin .5s cubic-bezier(.25,1,.5,1) both}
  @keyframes cin{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}
  .blink{animation:blink 1.1s steps(1) infinite;animation-delay:1.9s}
  @keyframes blink{50%{opacity:0}}
  .scroller{animation:marquee 60s linear infinite}
  @keyframes marquee{from{transform:translateX(0)}to{transform:translateX(-2400px)}}'''

svg = f'''<svg viewBox="0 0 1200 {TOTAL}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d">
<title id="t">Paul Cheng — AI engineering</title>
<desc id="d">One continuous profile: hero, what I build, how I work, the stack, {TOTAL_C} contributions over the last year, and a looping tools marquee.</desc>
<style>{STYLE}</style>
<defs>
  <clipPath id="frame"><rect width="1200" height="{TOTAL}" rx="18"/></clipPath>
  {M_TRK}
</defs>
<g clip-path="url(#frame)">
  <rect x="0" y="{HERO_Y}" width="1200" height="{HERO_H}" fill="#faf9f5"/>
  <rect x="0" y="{SAND_Y}" width="1200" height="{SAND_H}" fill="#e3dacc"/>
  <rect x="0" y="{SAGE_Y}" width="1200" height="{SAGE_H}" fill="#bcd1ca"/>
  <rect x="0" y="{LAV_Y}" width="1200" height="{LAV_H}" fill="#cbcadb"/>
  <rect x="0" y="{ACT_Y}" width="1200" height="{ACT_H}" fill="#faf9f5"/>
  <rect x="0" y="{MARQ_Y}" width="1200" height="{MARQ_H}" fill="#f0eee6"/>
  <g transform="translate(0,{HERO_Y})">{HERO}</g>
  <g transform="translate(0,{SAND_Y})">{SAND}</g>
  <g transform="translate(0,{SAGE_Y})">{SAGE}</g>
  <g transform="translate(0,{LAV_Y})">{LAV}</g>
  <g transform="translate(0,{ACT_Y})">{ACT_INNER}</g>
  <g transform="translate(0,{MARQ_Y})">{MARQUEE}</g>
</g>
</svg>
'''
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}: total_contributions={TOTAL_C}, height={TOTAL}")
