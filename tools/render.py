#!/usr/bin/env python3
"""Front page renderer for news-image-20261124 (24 November 2026).

Draws a 1024x1024 broadsheet: the date is the dominant headline, three lead
stories carry vector artwork that survives a 300px shrink, a strip of hard
numbers sits under the nameplate, a region index is computed from the story
list itself so its counts always sum to the story count, and the rest of the
day is set as a dense three-column brief.

Run:  python3 tools/render.py out/entry.png
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 24
MEASURE = W - 2 * M

INK = (22, 20, 18)
PAPER = (247, 244, 235)
RED = (171, 30, 30)
GREY = (92, 88, 82)
RULE = (168, 162, 150)

FONTS = Path(__file__).resolve().parent.parent / "fonts"


def face(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


BLACK = "ArchivoBlack-Regular.ttf"
SANS = "LibreFranklin.ttf"
SERIF = "LibreBaskerville.ttf"


def tracked(draw, xy, text, font, fill, spacing=0.0, anchor_left=True):
    """Draw text with extra letterspacing; returns the final x."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + spacing
    return x


def tracked_width(text, font, spacing):
    return sum(font.getlength(c) + spacing for c in text) - spacing


def wrap(text, font, width, max_lines=None):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= width:
            cur = trial
            continue
        if cur:
            lines.append(cur)
        cur = word
        if max_lines and len(lines) == max_lines:
            break
    if cur and (not max_lines or len(lines) < max_lines):
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    return lines


# ---------------------------------------------------------------- the day's news

LEADS = [
    {
        "section": "MIDEAST",
        "kicker": "THE GULF",
        "head": "IRAN VOWS TO ANSWER THE BLOCKADE WITH 'EVERY MEANS'",
        "deck": "Tehran calls the U.S. closing of the Strait of Hormuz an act of aggression and "
                "claims $290bn in damages; Washington says ships that run the line will be sunk.",
        "art": "strait",
    },
    {
        "section": "BUSINESS",
        "kicker": "MARKETS",
        "head": "NVIDIA BRINGS BACK HUANG AND ADDS $1 TRILLION IN A DAY",
        "deck": "The board reinstates its co-founder as chief executive 11 days after he resigned "
                "over a spy scandal, after Trump and Vance intervened; shares close up 29%.",
        "art": "chart",
    },
    {
        "section": "EUROPE",
        "kicker": "UKRAINE",
        "head": "STRIKES ON KYIV'S POWER GRID BRING A NIGHT WITHOUT LIGHT",
        "deck": "At least 11 are killed in the region as the Security Council meets on Russia's "
                "winter campaign and on attacks on Black Sea shipping.",
        "art": "grid",
    },
]

# (section, headline) — counts per section are computed from this list, never typed.
BRIEFS = [
    ("MIDEAST", "Tehran puts the bill for the war at $290bn and demands Washington pay it."),
    ("MIDEAST", "Fourteen tankers are readied at Kharg Island; state television denies a convoy."),
    ("MIDEAST", "Houthis say they hit the Rabigh refining complex; Gulf shipping attacks at a wartime high."),
    ("MIDEAST", "Eisenkot and Netanyahu resume unity talks as a row over settler arson widens."),
    ("MIDEAST", "A UNRWA worker is among three killed in an Israeli drone strike in Gaza, medics say."),
    ("EUROPE", "Negotiators blame Saudi pressure for COP31's collapse; the Antalya text named no fossil fuel."),
    ("EUROPE", "NATO holds an emergency meeting after a Russian missile falls on Polish soil."),
    ("EUROPE", "Moscow threatens Estonia with 'all-out war' and warns Kyiv over Baltic strikes."),
    ("EUROPE", "Zelensky says seven naval drones struck a Russian patrol ship at its Libyan base."),
    ("EUROPE", "Greece reopens the Acropolis Museum after a seven-year, EUR6.2m restoration."),
    ("EUROPE", "Brussels opens an antitrust probe into Coca-Cola's bottler over curbs on cross-border sales."),
    ("ASIA", "South Korea orders Ulleung islanders to shelters after an aircraft enters its airspace."),
    ("ASIA", "A candy factory blaze in Banten kills 24, Indonesia says, with dozens still missing."),
    ("ASIA", "Modi pledges $1.62bn for Nepal's flood recovery and signs eight agreements in Delhi."),
    ("ASIA", "Indian and Chinese commanders meet in Arunachal Pradesh to steady the border."),
    ("ASIA", "Dhaka vows to arrest Hasina if she returns; garment unrest costs the sector $428m."),
    ("AFRICA", "Drone strikes hit homes and a UN compound in Khartoum, residents and the UN say."),
    ("AFRICA", "Fighting in Ituri traps a WHO Ebola team for more than a day, the agency says."),
    ("AFRICA", "Ten Libyan port workers are hurt in an attack on a Russian ship at Benghazi."),
    ("AFRICA", "Nigeria sets an $11m capital floor for issuers of stablecoins."),
    ("AMERICAS", "Bukele names the three Salvadoran soldiers killed on Haiti's anti-gang mission."),
    ("AMERICAS", "Sinaloa erupts after the capture of El Chapo Isidro, an FBI most-wanted."),
    ("AMERICAS", "The House ethics panel finds 'substantial evidence' of misconduct by Rep. Jimmy Gomez."),
    ("AMERICAS", "Trump halts a planned detonation at an Iowa plant while a court weighs the case."),
    ("AMERICAS", "Delta says it has fixed the fault that delayed 1,300 flights across its network."),
    ("BUSINESS", "Nvidia stops licensed H200 sales to China even though Washington approved them."),
    ("BUSINESS", "Gold rebounds above $3,600 from a one-year low; Brent holds just under $90."),
    ("BUSINESS", "Sixty aviation groups ask Congress for $30bn to modernise U.S. air traffic control."),
    ("BUSINESS", "China and Singapore sign 29 trade, finance and public-health agreements."),
    ("SPORT", "Alcaraz takes his first ATP Finals title, beating Zverev 6-2, 7-6(6) in Turin."),
    ("SPORT", "FIFA names the U.S., Mexico, Costa Rica and Jamaica as hosts of the 2031 Women's World Cup."),
    ("SPORT", "Gukesh opens his world championship defence against Sindarov in Geneva."),
    ("SPORT", "India and New Zealand draw the first Test after the hosts bat out the final day."),
]

NUMBERS = [
    ("24", "killed in the\nBanten factory fire"),
    ("11", "killed in strikes\non Kyiv's region"),
    ("$290B", "Iran's damages\nclaim on America"),
    ("29%", "Nvidia's one-day\nshare price surge"),
    ("$1.62B", "pledged by India\nfor Nepal's floods"),
    ("7", "naval drones that\nhit a Russian ship"),
]

SECTION_ORDER = ["MIDEAST", "EUROPE", "ASIA", "AFRICA", "AMERICAS", "BUSINESS", "SPORT"]

TABS = {
    "MIDEAST": (150, 40, 40),
    "EUROPE": (40, 82, 140),
    "ASIA": (32, 112, 96),
    "AFRICA": (140, 96, 30),
    "AMERICAS": (96, 58, 120),
    "BUSINESS": (30, 30, 30),
    "SPORT": (70, 96, 40),
}


def section_counts():
    """Region index computed from the story list, leads included."""
    counts = {s: 0 for s in SECTION_ORDER}
    for b in BRIEFS:
        counts[b[0]] += 1
    for lead in LEADS:
        counts[lead["section"]] += 1
    return counts


# ---------------------------------------------------------------- artwork


def art_strait(d, box):
    """Hormuz: water down the middle, Iran north, Oman south, ships held at the line."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(168, 190, 196))                     # the gulf
    # Iran, the northern shore
    d.polygon([(x0, y0), (x1, y0), (x1, y0 + int(h * 0.24)),
               (x0 + int(w * 0.62), y0 + int(h * 0.33)),
               (x0 + int(w * 0.34), y0 + int(h * 0.27)),
               (x0, y0 + int(h * 0.20))], fill=(216, 204, 176), outline=(146, 132, 106))
    # the peninsula, southern shore
    d.polygon([(x0, y1), (x1, y1), (x1, y1 - int(h * 0.26)),
               (x0 + int(w * 0.46), y1 - int(h * 0.30)),
               (x0 + int(w * 0.22), y1 - int(h * 0.40)),
               (x0, y1 - int(h * 0.34))], fill=(216, 204, 176), outline=(146, 132, 106))
    # the narrows: the two shores almost meet on the right
    d.polygon([(x1 - int(w * 0.14), y0 + int(h * 0.24)), (x1, y0 + int(h * 0.22)),
               (x1, y0 + int(h * 0.34)), (x1 - int(w * 0.10), y0 + int(h * 0.31))],
              fill=(216, 204, 176), outline=(146, 132, 106))
    # shipping lane through the water
    lane_y = y0 + int(h * 0.50)
    for i in range(0, w, 14):
        d.line([(x0 + i, lane_y), (x0 + i + 7, lane_y)], fill=(240, 246, 246), width=1)
    # the blockade: a hard line of hulls across the lane
    bx = x0 + int(w * 0.60)
    d.line([(bx, y0 + int(h * 0.22)), (bx, y1 - int(h * 0.20))], fill=RED, width=3)
    for i in range(3):
        hy = y0 + int(h * (0.30 + 0.17 * i))
        d.polygon([(bx - 13, hy), (bx + 2, hy - 4), (bx + 2, hy + 4)], fill=(38, 44, 50))
    # tankers waiting on the wrong side of it
    for i in range(4):
        px = x0 + int(w * (0.16 + 0.10 * i))
        py = lane_y + (6 if i % 2 else -6)
        d.polygon([(px, py), (px + 15, py - 5), (px + 15, py + 5)], fill=(44, 52, 58))
        d.rectangle([px + 4, py - 9, px + 11, py - 4], fill=(44, 52, 58))
    d.text((x0 + 5, y0 + 5), "IRAN", font=face(BLACK, 9), fill=(84, 70, 48))
    d.text((x0 + 5, y1 - 14), "OMAN", font=face(BLACK, 9), fill=(84, 70, 48))
    d.text((bx + 4, y0 + int(h * 0.13)), "U.S. LINE", font=face(BLACK, 8), fill=RED)
    d.text((bx + 4, y1 - int(h * 0.17)), "STOPPED", font=face(BLACK, 8), fill=RED)
    d.text((x0 + int(w * 0.30), y0 + int(h * 0.60)), "14 TANKERS", font=face(BLACK, 8), fill=(26, 52, 58))
    d.text((x1 - 44, lane_y + 6), "HORMUZ", font=face(BLACK, 8), fill=(240, 246, 246))


def art_chart(d, box):
    """NVDA: the 33% fall and the one-day recovery, with the trillion marked."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(16, 20, 27))
    # baseline at the crash low
    base = y1 - 16
    for i in range(1, 4):
        gy = y0 + int((base - y0) * i / 4)
        d.line([(x0 + 7, gy), (x1 - 7, gy)], fill=(36, 42, 54), width=1)
    # price path: high, long slide, then the spike
    steps = [0.92, 0.88, 0.80, 0.74, 0.66, 0.58, 0.50, 0.46, 0.44, 0.42, 0.41, 0.40, 0.40]
    spike = [0.46, 0.52, 0.57, 0.62, 0.68, 0.73, 0.78, 0.82, 0.85, 0.87, 0.88]
    vals = steps + spike
    path = []
    for i, v in enumerate(vals):
        px = x0 + 8 + int((w - 30) * i / (len(vals) - 1))
        py = base - int((h - 30) * v)
        path.append((px, py))
    d.line(path[:len(steps)], fill=(214, 98, 82), width=2)
    d.line(path[len(steps) - 1:], fill=(104, 226, 150), width=3)
    # mark the low and the close
    lo = path[len(steps) - 1]
    hi = path[-1]
    d.ellipse([lo[0] - 3, lo[1] - 3, lo[0] + 3, lo[1] + 3], fill=(214, 98, 82))
    d.ellipse([hi[0] - 4, hi[1] - 4, hi[0] + 4, hi[1] + 4], fill=(240, 252, 244))
    d.text((x0 + 6, y0 + 4), "NVDA", font=face(BLACK, 11), fill=(212, 220, 230))
    d.text((x1 - 46, y0 + 4), "+29%", font=face(BLACK, 14), fill=(104, 226, 150))
    d.text((lo[0] - 30, lo[1] - 11), "-33%", font=face(BLACK, 8), fill=(224, 118, 100))
    d.text((x0 + 6, y1 - 13), "$1 TRILLION BACK", font=face(BLACK, 9), fill=(180, 192, 206))
    d.text((x1 - 40, y1 - 13), "1 DAY", font=face(BLACK, 9), fill=(104, 226, 150))


def art_grid(d, box):
    """Kyiv: a dark skyline whose windows are out, one substation still standing."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(17, 19, 24))
    # moonless night sky wash
    d.rectangle([x0, y0, x1, y0 + int(h * 0.42)], fill=(21, 24, 32))
    heights = [0.34, 0.50, 0.40, 0.58, 0.36, 0.66, 0.44, 0.54, 0.38, 0.60, 0.46, 0.33]
    bw = (w - 10) // len(heights)
    for i, hh in enumerate(heights):
        top = y1 - 8 - int((h - 16) * hh)
        bx0 = x0 + 5 + i * bw
        d.rectangle([bx0, top, bx0 + bw - 2, y1 - 8], fill=(31, 33, 39))
        # windows: dark rooms, only three lights left in the whole city
        for r, wy in enumerate(range(top + 4, y1 - 12, 7)):
            for c, wx in enumerate(range(bx0 + 2, bx0 + bw - 4, 5)):
                lit = (i * 7 + r * 3 + c) % 23 == 0
                if lit:
                    d.rectangle([wx, wy, wx + 1, wy + 2], fill=(236, 178, 64))
                else:
                    d.rectangle([wx, wy, wx + 1, wy + 2], fill=(44, 47, 54))
    # the substation pylon, intact, with one severed line
    px = x0 + int(w * 0.83)
    topy = y0 + int(h * 0.28)
    d.line([(px, y1 - 8), (px, topy)], fill=(120, 126, 138), width=2)
    for arm in (0, 12, 24):
        ay = topy + arm
        d.line([(px - 13, ay), (px + 13, ay)], fill=(120, 126, 138), width=2)
        d.line([(px, ay + 6), (px - 13, ay)], fill=(96, 102, 114), width=1)
        d.line([(px, ay + 6), (px + 13, ay)], fill=(96, 102, 114), width=1)
    # the lines run left, and break
    for arm in (0, 12, 24):
        ay = topy + arm
        d.line([(px - 13, ay), (px - 40, ay + 6)], fill=(96, 102, 114), width=1)
        for i in range(0, 14, 5):
            d.line([(px - 44 - i, ay + 7 + i // 3), (px - 40 - i, ay + 3 + i // 3)], fill=RED, width=2)
    d.text((x0 + 6, y0 + 5), "KYIV REGION", font=face(BLACK, 10), fill=(230, 132, 100))
    d.text((x0 + 6, y1 - 14), "POWER CUT", font=face(BLACK, 8), fill=(200, 208, 220))
    d.text((px - 22, y1 - 14), "SUBSTATION", font=face(BLACK, 7), fill=(150, 158, 172))


ART = {"strait": art_strait, "chart": art_chart, "grid": art_grid}


# ---------------------------------------------------------------- the page


def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    f_small = face(SANS, 9)
    d.text((M, 22), "THE WORLD TODAY", font=face(BLACK, 13), fill=INK)
    d.text((M + 150, 26), "one page for one day", font=face(SERIF, 9), fill=GREY)
    right = "No. 328  \u00b7  compiled 23:59 UTC"
    d.text((W - M - f_small.getlength(right), 24), right, font=f_small, fill=GREY)
    d.line([(M, 42), (W - M, 42)], fill=INK, width=2)

    # the date is the headline
    y = 48
    f_day = face(BLACK, 22)
    end = tracked(d, (M, y), "T U E S D A Y", f_day, RED, 1.2)
    d.text((end + 14, y + 2), "issue 328", font=face(SERIF, 10), fill=GREY)
    y += 30
    f_date = face(BLACK, 78)
    date_line = "24 NOVEMBER 2026"
    while f_date.getlength(date_line) > MEASURE and f_date.size > 40:
        f_date = face(BLACK, f_date.size - 1)
    d.text((M, y), date_line, font=f_date, fill=INK)
    y += int(f_date.size * 1.02)

    f_sub = face(SERIF, 11)
    d.text((M, y), "The day in 36 stories, filed from 21 countries \u2014 conflict, markets, "
                   "climate and sport, set in one page.", font=f_sub, fill=GREY)
    y += 18
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
    y += 7

    # numbers strip
    strip_top = y
    f_num = face(BLACK, 25)
    f_cap = face(SANS, 7)
    cell = MEASURE // len(NUMBERS)
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cell
        d.text((cx, strip_top), num, font=f_num, fill=RED)
        for j, line in enumerate(cap.split("\n")):
            d.text((cx, strip_top + 30 + j * 9), line, font=f_cap, fill=GREY)
        if i:
            d.line([(cx - 8, strip_top + 2), (cx - 8, strip_top + 46)], fill=RULE, width=1)
    y = strip_top + 52
    d.line([(M, y), (W - M, y)], fill=INK, width=1)
    y += 8

    # three leads with artwork
    gutter = 12
    card_w = (MEASURE - 2 * gutter) // 3
    art_h = 118
    f_kick = face(SANS, 8)
    f_lead = face(BLACK, 17)
    f_deck = face(SERIF, 9)
    lead_bottom = y
    for i, lead in enumerate(LEADS):
        cx = M + i * (card_w + gutter)
        art_box = (cx, y, cx + card_w, y + art_h)
        ART[lead["art"]](d, art_box)
        d.rectangle(art_box, outline=(120, 116, 106))
        ty = y + art_h + 5
        kw = tracked_width(lead["kicker"], f_kick, 1.0)
        d.rectangle([cx, ty, cx + kw + 8, ty + 10], fill=TABS[lead["section"]])
        d.text((cx + 4, ty + 1), lead["kicker"], font=f_kick, fill=(250, 248, 242))
        ty += 13
        size = 17
        f_l = f_lead
        while size > 12:
            lines = wrap(lead["head"], f_l, card_w, max_lines=3)
            if len(lines) <= 3 and all(f_l.getlength(l) <= card_w for l in lines):
                break
            size -= 1
            f_l = face(BLACK, size)
        hlines = wrap(lead["head"], f_l, card_w, max_lines=3)
        for line in hlines:
            d.text((cx, ty), line, font=f_l, fill=INK)
            ty += int(size * 1.06)
        ty += 2
        d.line([(cx, ty), (cx + 26, ty)], fill=RED, width=2)
        ty += 5
        for line in wrap(lead["deck"], f_deck, card_w, max_lines=4):
            d.text((cx, ty), line, font=f_deck, fill=(58, 54, 48))
            ty += 11
        lead_bottom = max(lead_bottom, ty)

    y = lead_bottom + 6
    d.line([(M, y), (W - M, y)], fill=INK, width=1)
    y += 6

    # region index: counts computed from the story list
    counts = section_counts()
    total = sum(counts.values())
    fx = M
    f_tab = face(BLACK, 8)
    for sec in SECTION_ORDER:
        label = "%s %d" % (sec, counts[sec])
        tw = f_tab.getlength(label) + 10
        d.rectangle([fx, y, fx + tw, y + 13], fill=TABS[sec])
        d.text((fx + 5, y + 2), label, font=f_tab, fill=(250, 248, 242))
        fx += tw + 4
    note = "%d stories" % total
    d.text((W - M - f_tab.getlength(note), y + 2), note, font=f_tab, fill=GREY)
    y += 19
    d.line([(M, y), (W - M, y)], fill=RULE, width=1)
    y += 7

    # dense briefs, three columns, sized to fit exactly
    col_gap = 16
    col_w = (MEASURE - 2 * col_gap) // 3
    avail = H - 26 - y
    chosen = None
    for size in (13, 12.5, 12, 11.5, 11, 10.5, 10, 9.5):
        f_h = face(BLACK, size)
        f_k = face(SANS, max(6.5, size * 0.60))
        lh = int(size * 1.18)
        gap = int(size * 0.55)
        blocks = []
        for sec, head in BRIEFS:
            lines = wrap(head, f_h, col_w, max_lines=3)
            hgt = len(lines) * lh + int(size * 0.72) + gap
            blocks.append((sec, lines, hgt))
        # greedy flow into three columns
        cols = [[] for _ in range(3)]
        heights = [0, 0, 0]
        ok = True
        for blk in blocks:
            idx = heights.index(min(heights))
            if heights[idx] + blk[2] > avail:
                ok = False
                break
            cols[idx].append(blk)
            heights[idx] += blk[2]
        if ok:
            chosen = (size, f_h, f_k, lh, gap, cols)
            break
    if chosen is None:
        raise SystemExit("briefs do not fit")

    size, f_h, f_k, lh, gap, cols = chosen
    for ci, col in enumerate(cols):
        cx = M + ci * (col_w + col_gap)
        cy = y
        for sec, lines, hgt in col:
            kw = f_k.getlength(sec) + 6
            d.rectangle([cx, cy, cx + kw, cy + int(size * 0.66)], fill=TABS[sec])
            d.text((cx + 3, cy), sec, font=f_k, fill=(250, 248, 242))
            cy += int(size * 0.74)
            for line in lines:
                d.text((cx, cy), line, font=f_h, fill=INK)
                cy += lh
            cy += gap
            d.line([(cx, cy - gap // 2), (cx + col_w, cy - gap // 2)], fill=(214, 209, 197), width=1)

    # footer
    fy = H - 20
    d.line([(M, fy - 5), (W - M, fy - 5)], fill=INK, width=1)
    f_foot = face(SANS, 7)
    d.text((M, fy), "WIRE: Reuters \u00b7 AP \u00b7 AFP \u00b7 Anadolu \u00b7 Al Jazeera \u00b7 BBC \u00b7 The Hindu "
                     "\u00b7 Khaleej Times \u00b7 Dawn \u00b7 USGS", font=f_foot, fill=GREY)
    tag = "24 NOV 2026"
    d.text((W - M - f_foot.getlength(tag), fy), tag, font=f_foot, fill=RED)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    if out.stat().st_size > 1048576:
        raise SystemExit("over 1 MiB: %d" % out.stat().st_size)
    return out, total, size


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "out/entry.png"
    path, total, size = build(dest)
    print("wrote %s  %d bytes  %d stories  brief size %.1f" % (path, path.stat().st_size, total, size))
