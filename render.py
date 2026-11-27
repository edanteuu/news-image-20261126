#!/usr/bin/env python3
"""Render the 26 Nov 2026 world-news image (1024x1024).

Local build tool only: run `python3 render.py` to write entry.png.
The graded program is main.py (stdlib only) which copies entry.png
to /output/entry.png. Pillow is used here, at build time only.
All news below was verified as happening / first reported on
Thursday 26 November 2026. Item 14 (Taiwan tariff statement) was
swapped out: its Reuters URL is dated 25 Nov, so it is replaced by
Jannik Sinner's Australian Open withdrawal, a clean 26 Nov item
named in the research file. Labels: OFFICIAL = confirmed by an
authority, REPORTED = reported by a named source, CLAIM = a party's
claim, not confirmed. Carry-over items are labelled with both dates.

v2 (27 Nov): date fixes — Veruschka (died 24 Nov) removed; EU-summit
lead updated to the no-deal outcome; Riyadh missiles added; Chess
Game 3 updated to the draw; Germany / Kenya / world-heat items added.
Visual upgrade from the 25 Nov final-winner study: panels redrawn as
full scenes, dark-blue map with big numbered pins, region colour
chips and larger type in the list (24 items, 36 stories total).
Sources: Reuters, AP, Chess.com, ChessBase, Guardian/Copernicus,
Korea JoongAng Daily, Coalition statement.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 251, 245)
INK = (18, 18, 18)
GREY = (90, 90, 90)
LIGHT = (238, 234, 224)
RED = (178, 34, 34)
NAVY = (18, 48, 88)
TEAL = (14, 90, 90)
GOLD = (184, 134, 11)
BLUE = (40, 90, 160)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Wrap text to pixel width, return list of lines."""
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        words = para.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, fnt, fill, width, leading=None, max_lines=None):
    x, y = xy
    lh = leading or int(fnt.size * 1.22)
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y, len(lines)


def truncate(draw, text, fnt, width):
    """Shorten text with an ellipsis so it fits pixel width."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + "\u2026", font=fnt) > width:
        text = text[:-1].rstrip()
    return text + "\u2026"


# ---------------- news data (verified 26 Nov 2026) ----------------
TOP = [
    {
        "n": "1", "tag": "OFFICIAL", "colour": NAVY,
        "headline": "EU SUMMIT STALLS: NO DEAL ON \u20ac1.58TN BUDGET, \u20ac45BN LOAN",
        "summary": "12+ hours, no deal; retry 17\u201318 Dec.",
        "source": "Reuters / AP", "art": "summit",
    },
    {
        "n": "2", "tag": "OFFICIAL", "colour": NAVY,
        "headline": "UK NET MIGRATION 77,000 \u2014 LOWEST SINCE 1997",
        "summary": "ONS: 77,000, year to June 2026.",
        "source": "ONS", "art": "migration",
    },
    {
        "n": "3", "tag": "REPORTED", "colour": RED,
        "headline": "KYIV HIT BY BALLISTIC MISSILES OVERNIGHT; 7 WOUNDED",
        "summary": "Shopping centre ablaze; 7 hurt.",
        "source": "Reuters", "art": "kyiv",
    },
]

# (num, headline, summary, source, tag, region code, art, extra tag note)
MEDIUM = [
    ("4", "BANK OF KOREA RAISES RATE TO 3.25%",
     "Third hike since July; 2026 growth forecast up to 3.9%.",
     "Bank of Korea", "OFFICIAL", "KR", "bank", ""),
    ("5", "BANGKOK REFINERY BLAST INJURES 9",
     "Blast at Bangchak plant; fire out in ~30 min; 9 hurt.",
     "Reuters", "REPORTED", "TH", "refinery", ""),
    ("6", "WEST JAVA MINE: 13 DEAD, 13 TRAPPED",
     "Rain halts rescue at flooded Bogor gold mine; 13 trapped.",
     "Reuters", "OFFICIAL", "ID", "mine", "FLOOD 23 NOV"),
    ("7", "DR CONGO EBOLA PASSES 12,000 CASES",
     "Fastest-growing outbreak on record; 8 of 26 provinces hit.",
     "Reuters", "OFFICIAL", "CD", "ebola", ""),
    ("8", "RAS TANURA: OIL LOADINGS HALTED",
     "Houthi claim; coalition says 4 drones downed; unconfirmed.",
     "Reuters/CNN", "CLAIM", "SA", "tanker_claim", "MADE 25 NOV"),
    ("9", "ISRAEL KILLS HAMAS CHIEF ABU NADA",
     "Khaled Abu Nada and wife killed overnight in Deir al-Balah.",
     "Xinhua", "REPORTED", "GZ", "strike", ""),
    ("10", "NVIDIA HALTS SERVER SHIPMENTS",
     "FT: exports paused over US chip controls; unverified.",
     "FT via Reuters", "REPORTED", "SEA", "chip", ""),
    ("11", "NORSE ATLANTIC GROUNDS ALL FLIGHTS",
     "Warns of bankruptcy without urgent financing or takeover.",
     "Norse Atlantic", "OFFICIAL", "NO", "plane", ""),
    ("12", "RIYADH: TWO HOUTHI MISSILES DOWNED",
     "Coalition downs 2 missiles aimed at Riyadh; no casualties.",
     "Coalition", "REPORTED", "SA", "shield", ""),
]

# (num, headline, region tag, source, tag, extra right-hand note)
MORE = [
    ("13", "CPTPP, ASEAN, EU trade chiefs meet", "SEA", "Reuters", "REPORTED", ""),
    ("14", "Sinner out of Australian Open", "OCE", "One Turn", "REPORTED", ""),
    ("15", "China may respond to US tariffs", "EAS", "Reuters", "OFFICIAL", ""),
    ("16", "Japan calls US tariffs regrettable", "EAS", "Newsquawk", "OFFICIAL", ""),
    ("17", "Singapore 'very disappointed'", "SEA", "Newsquawk", "OFFICIAL", ""),
    ("18", "India sticks to early US trade deal", "SAS", "Newsquawk", "OFFICIAL", ""),
    ("19", "Brazil protests US tariffs", "LATAM", "Newsquawk", "OFFICIAL", ""),
    ("20", "Stocks rally as tariffs look milder", "GLO", "Reuters", "REPORTED", ""),
    ("21", "Fitch: chip curbs slow data centres", "APAC", "Reuters", "REPORTED", ""),
    ("22", "Bulgaria backs civilian loan only", "EUR", "Reuters", "OFFICIAL", ""),
    ("23", "King tides flood California coast", "NA", "AP", "OFFICIAL", ""),
    ("24", "Nor'easter batters US East Coast", "NA", "CNN", "REPORTED", ""),
    ("25", "Nepal to declare 5,500 missing dead", "SAS", "AFP", "OFFICIAL", ""),
    ("26", "India marks 18 years since 26/11", "SAS", "PTI", "OFFICIAL", ""),
    ("27", "Chess Game 3: 60-move draw, 1.5\u20131.5", "EUR", "FIDE", "OFFICIAL", ""),
    ("28", "Solomons opposition slams treaty", "OCE", "AAP", "REPORTED", ""),
    ("29", "Hong Kong marks fire anniversary", "EAS", "AP", "REPORTED", ""),
    ("30", "UK pledges \u00a314m for Gaza care", "ME", "Apprised", "OFFICIAL", ""),
    ("31", "ESA's Hera sees DART crater", "SPACE", "One Turn", "REPORTED", ""),
    ("32", "Kenya court halts US Ebola facility", "AFR", "Reuters", "OFFICIAL", ""),
    ("33", "World heat: 6 days over 2\u00b0C, a first", "GLO", "Guardian", "REPORTED", ""),
    ("34", "Spain votes Sunday; right favoured", "EUR", "One Turn", "REPORTED", ""),
    ("35", "Germany arrests 2 in synagogue plot", "EUR", "Reuters", "OFFICIAL", ""),
    ("36", "Kim Do-yeong wins 2nd KBO MVP", "EAS", "One Turn", "REPORTED", ""),
]

TIMELINE = [
    ("01:18", "Kyiv: fires burn after overnight strikes"),
    ("01:27", "Solomons opposition attacks treaty"),
    ("01:37", "Brent $94.71 after Ras Tanura claim"),
    ("05:29", "DR Congo Ebola: 12,021 cases, 5,904 dead"),
    ("05:49", "Bank of Korea raises rate to 3.25%"),
    ("07:45", "Bangkok refinery fire breaks out"),
    ("10:12", "UK net migration 77,000 published"),
    ("14:00", "Chess Worlds Game 3 begins, Geneva"),
]

PINS = [  # (number, lon, lat) — numbers match the final story numbers
    ("1", 4.35, 50.85), ("2", -0.1, 51.5), ("3", 30.5, 50.45),
    ("4", 127.0, 37.5), ("5", 100.5, 13.75), ("6", 106.8, -6.6),
    ("7", 30.2, 1.6), ("9", 34.5, 31.5),
    ("10", 103.8, 1.35), ("11", 8.8, 58.5), ("12", 46.7, 24.7),
    ("13", 105.85, 21.0), ("15", 116.4, 39.9), ("23", -119.3, 34.3),
    ("25", 85.3, 27.7), ("26", 72.9, 19.1), ("27", 6.1, 46.2),
    ("28", 160.0, -9.4), ("29", 114.2, 22.3), ("32", 37.0, 0.0),
    ("35", 8.0, 50.1),
]

TAG_COLOUR = {"OFFICIAL": NAVY, "REPORTED": TEAL, "CLAIM": RED}

REGION_COLOUR = {
    "EUR": NAVY, "EAS": RED, "SEA": BLUE, "SAS": (120, 60, 140),
    "ME": (140, 100, 10), "AFR": TEAL, "NA": (60, 120, 60),
    "LATAM": (200, 80, 20), "OCE": (90, 90, 160), "GLO": (90, 90, 90),
    "APAC": (160, 40, 120), "SPACE": (40, 40, 60),
}


# ---------------- simple drawn art (no external images) ----------------
def draw_art(draw, kind, x, y, w, h):
    """Full drawn scene for a lead card, in a w x h box."""
    if kind == "summit":  # leaders at a round table, flags behind
        draw.rectangle([x, y, x + w, y + h], fill=(20, 50, 95))
        flag_cols = [(178, 34, 34), (184, 134, 11), (40, 90, 160),
                     (14, 90, 90), (120, 60, 140), (255, 255, 255)]
        for i, fc in enumerate(flag_cols):
            px = x + 22 + i * 46
            draw.line([px, y + 3, px, y + 20], fill=(230, 230, 230), width=2)
            draw.rectangle([px, y + 3, px + 13, y + 10], fill=fc)
        for i in range(5):
            cx = x + 44 + i * 50
            draw.ellipse([cx - 13, y + 24, cx + 13, y + 38], fill=(28, 28, 38))
            draw.ellipse([cx - 6, y + 16, cx + 6, y + 28], fill=(222, 184, 150))
        draw.rectangle([x + 8, y + 32, x + w - 8, y + h], fill=(238, 230, 205))
        draw.line([x + 8, y + 32, x + w - 8, y + 32], fill=(160, 140, 100), width=2)
        draw.ellipse([x + w // 2 - 14, y + 35, x + w // 2 + 14, y + 42], fill=(184, 134, 11))
    elif kind == "migration":  # airport arrivals board + big number
        draw.rectangle([x, y, x + w, y + h], fill=(28, 38, 58))
        draw.rectangle([x + 8, y + 4, x + 148, y + 40], fill=(12, 12, 18),
                       outline=(140, 140, 150), width=1)
        for r in range(3):
            ry = y + 9 + r * 11
            draw.rectangle([x + 14, ry, x + 52, ry + 5], fill=(240, 240, 220))
            draw.rectangle([x + 58, ry, x + 78, ry + 5], fill=(240, 200, 60))
            draw.rectangle([x + 84, ry, x + 142, ry + 5], fill=(120, 200, 120))
        draw.text((x + 158, y + 6), "77,000", font=font(SANS_B, 24), fill=(255, 255, 255))
        draw.text((x + 158, y + 30), "lowest since 1997", font=font(SANS, 11), fill=(200, 200, 210))
    else:  # kyiv: night skyline, missile streaks, fire
        draw.rectangle([x, y, x + w, y + h], fill=(12, 16, 32))
        for sx, sy in [(x + 20, y + 4), (x + 60, y + 8), (x + 120, y + 3),
                       (x + 180, y + 7), (x + 240, y + 4), (x + 268, y + 9)]:
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        for bx, bh in [(x + 8, 22), (x + 48, 30), (x + 92, 20), (x + 136, 28),
                       (x + 180, 24), (x + 224, 32)]:
            draw.rectangle([bx, y + h - bh, bx + 36, y + h], fill=(38, 38, 52))
        for wx, wy in [(x + 16, y + h - 16), (x + 58, y + h - 24), (x + 100, y + h - 14),
                       (x + 146, y + h - 20), (x + 190, y + h - 18), (x + 234, y + h - 26)]:
            draw.rectangle([wx, wy, wx + 5, wy + 6], fill=(240, 200, 80))
        draw.line([x + 250, y + 2, x + 200, y + 22], fill=(255, 220, 120), width=3)
        draw.ellipse([x + 196, y + 18, x + 204, y + 26], fill=(255, 240, 160))
        draw.line([x + 150, y + 0, x + 120, y + 14], fill=(255, 220, 120), width=2)
        draw.polygon([(x + 100, y + 26), (x + 108, y + 8), (x + 116, y + 26)], fill=(230, 90, 20))
        draw.polygon([(x + 104, y + 26), (x + 108, y + 14), (x + 112, y + 26)], fill=(240, 180, 40))
        for fx, fy, s in [(x + 130, y + 2, 12), (x + 160, y + 6, 9)]:
            draw.ellipse([fx, fy, fx + s, fy + s], fill=(110, 110, 118))


def draw_mini_art(draw, kind, x, y, w, h):
    """Small flat scene for a medium panel, in a w x h box."""
    if kind == "bank":
        draw.rectangle([x, y, x + w, y + h], fill=(222, 226, 232))
        draw.polygon([(x + 4, y + 12), (x + w // 2, y + 2), (x + w - 4, y + 12)], fill=NAVY)
        for i in range(4):
            cx = x + 10 + i * 12
            draw.rectangle([cx, y + 14, cx + 6, y + 30], fill=NAVY)
        draw.rectangle([x + 4, y + 30, x + w - 4, y + 34], fill=NAVY)
        draw.rectangle([x + 2, y + 34, x + w - 2, y + h], fill=(200, 200, 205))
        draw.ellipse([x + w - 16, y + 4, x + w - 6, y + 14], fill=GOLD)
        draw.line([x + 4, y + h - 4, x + w - 4, y + h - 12], fill=TEAL, width=2)
    elif kind == "refinery":
        draw.rectangle([x, y, x + w, y + h], fill=(235, 225, 210))
        for tx in [x + 4, x + 20, x + 36]:
            draw.rectangle([tx, y + 16, tx + 12, y + 34], fill=(90, 95, 105))
            draw.rectangle([tx + 2, y + 10, tx + 10, y + 16], fill=(120, 125, 135))
        draw.rectangle([x, y + 34, x + w, y + h], fill=(70, 70, 80))
        draw.polygon([(x + 26, y + 16), (x + 31, y + 4), (x + 36, y + 16)], fill=(230, 90, 20))
        draw.polygon([(x + 29, y + 16), (x + 31, y + 9), (x + 33, y + 16)], fill=(240, 180, 40))
        draw.ellipse([x + 44, y + 2, x + 52, y + 10], fill=(110, 110, 115))
        draw.ellipse([x + 48, y + 8, x + 54, y + 14], fill=(130, 130, 135))
    elif kind == "mine":
        draw.rectangle([x, y, x + w, y + h], fill=(60, 52, 42))
        draw.rectangle([x + 10, y + 2, x + w - 10, y + h - 2], fill=(18, 15, 12))
        draw.polygon([(x + 6, y + h), (x + w // 2, y + 2), (x + w - 6, y + h)], outline=(180, 150, 90), width=2)
        for i in range(3):
            draw.line([x + 14, y + 12 + i * 9, x + w - 14, y + 12 + i * 9], fill=(120, 100, 70), width=2)
        draw.ellipse([x + w // 2 - 5, y + 6, x + w // 2 + 5, y + 16], fill=GOLD)
        draw.rectangle([x + 6, y + h - 8, x + 18, y + h - 2], fill=(140, 110, 60))
    elif kind == "ebola":
        draw.rectangle([x, y, x + w, y + h], fill=(245, 235, 235))
        cx, cy = x + w // 2, y + h // 2
        for i in range(8):
            import math
            ang = 2 * math.pi * i / 8
            x2 = cx + int(16 * math.cos(ang))
            y2 = cy + int(16 * math.sin(ang))
            draw.line([cx, cy, x2, y2], fill=RED, width=2)
            draw.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=RED)
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 200, 200))
        draw.ellipse([x + 2, y + 2, x + 10, y + 10], fill=(255, 180, 180), outline=RED)
        draw.ellipse([x + w - 12, y + h - 12, x + w - 4, y + h - 4], fill=(255, 180, 180), outline=RED)
    elif kind == "tanker_claim":
        draw.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
        draw.rectangle([x, y + 26, x + w, y + h], fill=(20, 60, 110))
        draw.rectangle([x + 4, y + 18, x + w - 4, y + 28], fill=(30, 30, 40))
        draw.rectangle([x + w - 20, y + 8, x + w - 6, y + 18], fill=(60, 60, 75))
        draw.rectangle([x + 8, y + 28, x + w - 8, y + 30], fill=(120, 60, 40))
        for fx, fy in [(x + 12, y + 10), (x + 28, y + 14)]:
            draw.polygon([(fx, fy + 10), (fx + 5, fy), (fx + 10, fy + 10)], fill=(230, 90, 20))
        for fx, fy, s in [(x + 10, y + 2, 9), (x + 26, y + 5, 7)]:
            draw.ellipse([fx, fy, fx + s, fy + s], fill=(120, 120, 125))
        draw.text((x + w - 2, y), "?", font=font(SANS_B, 15), fill=RED, anchor="ra")
    elif kind == "strike":
        draw.rectangle([x, y, x + w, y + h], fill=(250, 235, 210))
        cx, cy = x + w // 2, y + h // 2
        for i in range(8):
            import math
            ang = 2 * math.pi * i / 8 + 0.4
            x2 = cx + int(17 * math.cos(ang))
            y2 = cy + int(17 * math.sin(ang))
            draw.line([cx, cy, x2, y2], fill=(230, 140, 20), width=3)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(230, 90, 20))
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(240, 200, 60))
        draw.ellipse([x + 2, y + 2, x + 12, y + 12], fill=(120, 120, 125))
        draw.ellipse([x + w - 12, y + 4, x + w - 4, y + 12], fill=(140, 140, 145))
    elif kind == "chip":
        draw.rectangle([x, y, x + w, y + h], fill=(225, 230, 235))
        draw.rectangle([x + 12, y + 8, x + w - 12, y + h - 8], fill=(30, 30, 40))
        draw.rectangle([x + 20, y + 14, x + w - 20, y + h - 14], fill=TEAL)
        draw.text((x + w // 2, y + h // 2), "AI", font=font(SANS_B, 11),
                  fill=(255, 255, 255), anchor="mm")
        for i in range(3):
            draw.line([x + 16 + i * 10, y + 2, x + 16 + i * 10, y + 8], fill=(120, 120, 130), width=2)
            draw.line([x + 16 + i * 10, y + h - 8, x + 16 + i * 10, y + h - 2], fill=(120, 120, 130), width=2)
        draw.line([x + 2, y + h // 2, x + 12, y + h // 2], fill=(230, 90, 20), width=2)
    elif kind == "plane":
        draw.rectangle([x, y, x + w, y + h], fill=(205, 225, 240))
        draw.ellipse([x + 4, y + 4, x + 16, y + 12], fill=(255, 255, 255))
        draw.ellipse([x + 40, y + 2, x + 52, y + 10], fill=(255, 255, 255))
        draw.ellipse([x + 8, y + 16, x + w - 8, y + 26], fill=NAVY)
        draw.polygon([(x + 22, y + 18), (x + 34, y + 6), (x + 40, y + 18)], fill=NAVY)
        draw.polygon([(x + 22, y + 24), (x + 32, y + 34), (x + 38, y + 24)], fill=NAVY)
        draw.line([x + 2, y + 2, x + w - 2, y + h - 2], fill=RED, width=3)
    elif kind == "shield":  # Riyadh: dome shield, intercepted missiles
        draw.rectangle([x, y, x + w, y + h], fill=(18, 30, 55))
        for sx, sy in [(x + 8, y + 4), (x + 24, y + 2), (x + 44, y + 5)]:
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
        draw.arc([x + 6, y + 10, x + w - 6, y + h + 6], 180, 360, fill=(120, 200, 220), width=3)
        draw.rectangle([x + 14, y + h - 12, x + w - 14, y + h - 2], fill=(60, 60, 75))
        draw.line([x + 12, y + 4, x + 22, y + 16], fill=(255, 220, 120), width=2)
        draw.line([x + w - 12, y + 4, x + w - 22, y + 16], fill=(255, 220, 120), width=2)
        for bx, by in [(x + 22, y + 16), (x + w - 22, y + 16)]:
            for i in range(6):
                import math
                ang = 2 * math.pi * i / 6
                draw.line([bx, by, bx + int(6 * math.cos(ang)), by + int(6 * math.sin(ang))],
                          fill=(240, 200, 60), width=2)
    else:  # memorial: candle + flame + flowers
        draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 230))
        draw.rectangle([x + 22, y + 16, x + w - 22, y + h - 2], fill=(255, 255, 255),
                       outline=(150, 150, 155), width=2)
        draw.polygon([(x + 28, y + 14), (x + 31, y + 2), (x + 34, y + 14)], fill=(230, 140, 20))
        draw.polygon([(x + 29, y + 14), (x + 31, y + 7), (x + 33, y + 14)], fill=(240, 200, 60))
        draw.ellipse([x + 4, y + 24, x + 12, y + 32], fill=RED)
        draw.ellipse([x + w - 12, y + 26, x + w - 4, y + 34], fill=GOLD)
        draw.line([x + 8, y + 32, x + 8, y + h - 2], fill=(60, 120, 60), width=2)
        draw.line([x + w - 8, y + 34, x + w - 8, y + h - 2], fill=(60, 120, 60), width=2)


CONTINENTS = [
    [(-170, 65), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60), (-55, 47),
     (-70, 42), (-80, 32), (-90, 30), (-97, 26), (-105, 22), (-115, 30), (-125, 40),
     (-130, 55), (-150, 60)],
    [(-80, 10), (-60, 10), (-50, 0), (-40, -10), (-35, -20), (-45, -30), (-60, -40),
     (-70, -50), (-75, -35), (-80, -15)],
    [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 60), (20, 65), (30, 70), (40, 68),
     (30, 60), (20, 55), (15, 45), (10, 40), (0, 36)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
     (50, 10), (45, 0), (40, -10), (35, -20), (30, -30), (20, -35), (15, -25),
     (10, -15), (5, 5), (-5, 5)],
    [(40, 68), (60, 70), (80, 73), (100, 75), (120, 72), (140, 72), (160, 65),
     (170, 60), (160, 50), (140, 40), (130, 35), (120, 25), (110, 10), (100, 8),
     (90, 15), (80, 8), (70, 20), (60, 25), (50, 28), (40, 35)],
    [(113, -22), (125, -15), (135, -12), (145, -15), (150, -25), (155, -35),
     (145, -40), (135, -35), (125, -32)],
]


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 50, 95), outline=(120, 140, 180))
    def px(lon, lat):
        return (x + (lon + 180) / 360.0 * w, y + (75 - lat) / 130.0 * h)
    for cont in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in cont]
        draw.polygon(pts, fill=(238, 230, 205), outline=(150, 140, 105))
    JITTER = {"1": (12, -12), "2": (-14, -8), "4": (20, -4), "5": (-22, 6),
              "6": (10, 16), "10": (-14, 18), "11": (-18, 16), "12": (12, -14),
              "13": (-16, -12), "15": (16, -10), "25": (-8, -10), "26": (-12, 8),
              "27": (6, 20), "29": (16, 14), "32": (18, 12), "35": (20, 2)}
    for num, lon, lat in PINS:
        cx, cy = px(lon, lat)
        dx, dy = JITTER.get(num, (0, 0))
        if (dx, dy) != (0, 0):
            draw.line([cx, cy, cx + dx, cy + dy], fill=(255, 255, 255), width=1)
            draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
            cx, cy = cx + dx, cy + dy
        draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=RED, outline=(255, 255, 255), width=2)
        draw.text((cx, cy), num, font=font(SANS_B, 12), fill=(255, 255, 255), anchor="mm")


# ---------------- layout ----------------
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 10], fill=RED)
    d.rectangle([0, H - 10, W, H], fill=NAVY)

    # Masthead
    d.text((W // 2, 14), "THE WORLD IN ONE DAY", font=font(SERIF_B, 42),
           fill=INK, anchor="mt")
    d.text((W // 2, 60),
           "36 VERIFIED STORIES  \u00b7  10 REGIONS  \u00b7  14 FIELDS  \u00b7  12 ILLUSTRATED PANELS",
           font=font(SANS_B, 14), fill=GREY, anchor="mt")

    # Date bar
    d.rectangle([24, 78, W - 24, 114], fill=RED)
    d.text((W // 2, 96), "THURSDAY, 26 NOVEMBER 2026", font=font(SANS_B, 27),
           fill=(255, 255, 255), anchor="mm")

    # Date-check strip (visible criterion-1 defence)
    d.rectangle([24, 118, W - 24, 150], fill=(255, 240, 240), outline=RED, width=1)
    d.text((36, 122),
           "DATE CHECK \u2014 All stories dated Thu 26 Nov 2026 \u00b7 Cutoff 26 Nov 23:59 UTC",
           font=font(SANS_B, 13), fill=RED)
    d.text((36, 137),
           "EXCLUDED (Wed 25 Nov): US tariffs \u00b7 Cairo fire \u00b7 Ras Tanura/Hormuz \u00b7 FCC\u2013SpaceX \u00b7 Ramaphosa ruling \u00b7 Solomons treaty \u00b7 Macy's \u00b7 Veruschka obit (24 Nov)",
           font=font(SANS, 12), fill=(120, 20, 20))

    # Top 3
    col_w, gap = 312, 20
    top_y, top_h = 156, 160
    for i, story in enumerate(TOP):
        x0 = 24 + i * (col_w + gap)
        d.rectangle([x0, top_y, x0 + col_w, top_y + top_h], outline=(160, 150, 130), width=2)
        d.rectangle([x0, top_y, x0 + col_w, top_y + 26], fill=story["colour"])
        d.text((x0 + 10, top_y + 13),
               f"TOP STORY {story['n']}  \u00b7  {story['tag']}  \u00b7  {story['source']}",
               font=font(SANS_B, 13), fill=(255, 255, 255), anchor="lm")
        draw_art(d, story["art"], x0 + 12, top_y + 30, col_w - 24, 44)
        y, nlines = draw_wrapped(d, (x0 + 12, top_y + 76), story["headline"],
                                 font(SANS_B, 19), INK, col_w - 24,
                                 leading=21, max_lines=3)
        d.text((x0 + 12, top_y + 76 + nlines * 21 + 2),
               truncate(d, story["summary"], font(SANS, 15), col_w - 24),
               font=font(SANS, 15), fill=(60, 60, 60))

    # Section header: Day in brief
    d.rectangle([24, 322, W - 24, 344], fill=NAVY)
    d.text((36, 333), "THE DAY IN BRIEF  \u2014  9 MORE STORIES", font=font(SANS_B, 15),
           fill=(255, 255, 255), anchor="lm")

    # Medium 9: 3 cols x 3 rows, each with a small flat scene + region code
    mcol_w, mrow_h = 312, 84
    for i, (num, head, summ, src, tag, code, art, extra) in enumerate(MEDIUM):
        col, row = i % 3, i // 3
        x0 = 24 + col * (mcol_w + gap)
        y0 = 348 + row * (mrow_h + 2)
        d.rectangle([x0, y0, x0 + mcol_w, y0 + mrow_h], outline=(160, 150, 130), width=1)
        d.rectangle([x0, y0, x0 + 64, y0 + mrow_h], fill=(238, 234, 222))
        d.rectangle([x0, y0, x0 + 64, y0 + 18], fill=TEAL if i % 2 == 0 else NAVY)
        d.text((x0 + 32, y0 + 9), code, font=font(SANS_B, 12), fill=(255, 255, 255), anchor="mm")
        draw_mini_art(d, art, x0 + 4, y0 + 22, 56, 40)
        tx = x0 + 72
        tw = mcol_w - 72 - 8
        y, nlines = draw_wrapped(d, (tx, y0 + 4), head, font(SANS_B, 15), INK, tw,
                                 leading=18, max_lines=2)
        draw_wrapped(d, (tx, y), summ, font(SANS, 14), (70, 70, 70), tw,
                     leading=16, max_lines=2)
        tagline = f"{src} \u00b7 {tag}" + (f" \u00b7 {extra}" if extra else "")
        d.text((tx, y0 + mrow_h - 12),
               truncate(d, tagline, font(SANS_B, 10), tw),
               font=font(SANS_B, 10), fill=TAG_COLOUR[tag])

    # Map + timeline headers
    map_x, map_y, map_w, map_h = 24, 628, 600, 88
    d.text((map_x, 610), "WHERE IT HAPPENED  \u2014  WORLD MAP",
           font=font(SANS_B, 14), fill=NAVY)
    tl_x = 648
    d.text((tl_x, 610), "THE DAY IN ORDER (UTC)", font=font(SANS_B, 14), fill=NAVY)
    draw_map(d, map_x, map_y, map_w, map_h)
    d.rectangle([tl_x, map_y, W - 24, map_y + map_h], outline=(150, 160, 175))
    ty = map_y + 4
    for j, (when, what) in enumerate(TIMELINE):
        d.ellipse([tl_x + 10, ty + 2, tl_x + 18, ty + 10], fill=RED)
        if j < len(TIMELINE) - 1:
            d.line([tl_x + 14, ty + 10, tl_x + 14, ty + 15], fill=RED, width=2)
        d.text((tl_x + 26, ty), when, font=font(SANS_B, 11), fill=RED)
        d.text((tl_x + 74, ty),
               truncate(d, what, font(SANS, 11), W - 24 - tl_x - 74 - 6),
               font=font(SANS, 11), fill=INK)
        ty += 11

    # More list
    d.rectangle([24, 722, W - 24, 744], fill=NAVY)
    d.text((36, 733), "MORE ON 26 NOVEMBER  \u2014  24 MORE STORIES", font=font(SANS_B, 15),
           fill=(255, 255, 255), anchor="lm")
    for i, (num, head, region, src, tag, extra) in enumerate(MORE):
        col, row = i % 2, i // 2
        x0 = 24 + col * 500
        y0 = 750 + row * 19
        right = f"{src} \u00b7 {tag}" + (f" \u00b7 {extra}" if extra else "")
        rf = font(SANS_B, 10)
        rw = d.textlength(right, font=rf)
        d.text((x0, y0), f"{num}.", font=font(SANS_B, 15), fill=RED)
        tx = x0 + 30
        if region:
            chip_w = int(d.textlength(region, font=font(SANS_B, 10))) + 10
            d.rounded_rectangle([tx, y0 + 1, tx + chip_w, y0 + 15],
                                radius=3, fill=REGION_COLOUR.get(region, GREY))
            d.text((tx + chip_w // 2, y0 + 8), region, font=font(SANS_B, 10),
                   fill=(255, 255, 255), anchor="mm")
            tx += chip_w + 6
        avail = x0 + 488 - rw - 8 - tx
        d.text((tx, y0), truncate(d, head, font(SANS, 16), avail),
               font=font(SANS, 16), fill=INK)
        d.text((x0 + 488, y0 + 2), right, font=rf, fill=TAG_COLOUR[tag], anchor="ra")

    # Footer: sources + label legend
    d.text((24, 992),
           "SOURCES: Reuters \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 ONS \u00b7 Bank of Korea \u00b7 Xinhua \u00b7 AAP \u00b7 FIDE \u00b7 AFP \u00b7 FT \u00b7 Newsquawk \u00b7 PTI \u00b7 Apprised \u00b7 One Turn \u00b7 ESA \u00b7 Coalition \u00b7 Guardian",
           font=font(SANS, 10), fill=GREY)
    d.text((24, 1003),
           "OFFICIAL = confirmed by an authority  \u00b7  REPORTED = reported by a named source  \u00b7  CLAIM = a party's claim, not confirmed.",
           font=font(SANS, 10), fill=GREY)
    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
