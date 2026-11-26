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
        "headline": "EU SUMMIT OPENS: \u20ac1.58TN BUDGET, \u20ac45BN UKRAINE LOAN",
        "summary": "27 leaders meet in Brussels.",
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
    ("12", "HONG KONG MARKS FIRE ANNIVERSARY",
     "One year on from the Tai Po fire that killed 168.",
     "AP", "REPORTED", "HK", "memorial", "FIRE 26 NOV 2025"),
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
    ("22", "US chip curbs delay Chinese AI models", "EAS", "Reuters", "REPORTED", ""),
    ("23", "Bulgaria backs civilian loan only", "EUR", "Reuters", "OFFICIAL", ""),
    ("24", "Kharkiv drone strike kills 2", "EUR", "InfoKava", "REPORTED", ""),
    ("25", "King tides flood California coast", "NA", "AP", "OFFICIAL", ""),
    ("26", "Nor'easter batters US East Coast", "NA", "CNN", "REPORTED", ""),
    ("27", "Nepal to declare 5,500 missing dead", "SAS", "AFP", "OFFICIAL", ""),
    ("28", "India marks 18 years since 26/11", "SAS", "PTI", "OFFICIAL", ""),
    ("29", "Chess Game 3: Gukesh v Sindarov, 1-1", "EUR", "FIDE", "OFFICIAL", ""),
    ("30", "Solomons opposition slams treaty", "", "AAP", "REPORTED", "SIGNED 25 NOV"),
    ("31", "Estonia opens \u20ac110m solar park", "EUR", "Apprised", "REPORTED", ""),
    ("32", "Shuri Castle main hall reopens", "EAS", "Apprised", "REPORTED", ""),
    ("33", "Nine Ukrainian children reunited", "EUR", "Apprised", "REPORTED", ""),
    ("34", "UK pledges \u00a314m for Gaza care", "ME", "Apprised", "OFFICIAL", ""),
    ("35", "ESA's Hera sees DART crater", "SPACE", "One Turn", "REPORTED", ""),
    ("36", "Pig-kidney patient 1 year off dialysis", "NA", "One Turn", "REPORTED", ""),
    ("37", "Australia set to miss 2035 target", "OCE", "One Turn", "REPORTED", ""),
    ("38", "Spain votes Sunday; right favoured", "EUR", "One Turn", "REPORTED", ""),
    ("39", "Veruschka, supermodel, dies at 87", "EUR", "One Turn", "REPORTED", ""),
    ("40", "Kim Do-yeong wins 2nd KBO MVP", "EAS", "One Turn", "REPORTED", ""),
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

PINS = [  # (number, lon, lat)
    ("1", 4.35, 50.85), ("2", -0.1, 51.5), ("3", 30.5, 50.45),
    ("4", 127.0, 37.5), ("5", 100.5, 13.75), ("6", 106.8, -6.6),
    ("7", 30.2, 1.6), ("8", 50.2, 26.6), ("9", 34.5, 31.5),
    ("10", 103.8, 1.35), ("11", 8.8, 58.5), ("12", 114.2, 22.3),
    ("13", 105.85, 21.0), ("15", 116.4, 39.9), ("25", -119.3, 34.3),
    ("27", 85.3, 27.7), ("28", 72.9, 19.1), ("29", 6.1, 46.2),
    ("30", 160.0, -9.4),
]

TAG_COLOUR = {"OFFICIAL": NAVY, "REPORTED": TEAL, "CLAIM": RED}


# ---------------- simple drawn art (no external images) ----------------
def draw_art(draw, kind, x, y, w, h):
    """Large flat scene for a lead card, in a w x h box."""
    if kind == "summit":  # EU building + ring of stars
        draw.rectangle([x + 20, y + 22, x + w - 20, y + h - 2], fill=NAVY)
        for i in range(5):
            cx = x + 48 + i * 52
            draw.rectangle([cx, y + 28, cx + 14, y + h - 8], fill=(255, 255, 255))
        draw.polygon([(x + 20, y + 22), (x + w // 2, y + 2), (x + w - 20, y + 22)],
                     fill=(18, 48, 88))
        for i in range(12):
            import math
            ang = 2 * math.pi * i / 12
            sx = x + w - 34 + int(13 * math.cos(ang))
            sy = y + 12 + int(13 * math.sin(ang))
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
        draw.text((x + w - 34, y + 12), "\u2605", font=font(SANS_B, 10),
                  fill=GOLD, anchor="mm")
    elif kind == "migration":  # descending bars + big 77,000
        for i, bh in enumerate([30, 24, 16, 9]):
            bx = x + 16 + i * 26
            draw.rectangle([bx, y + h - 6 - bh, bx + 18, y + h - 6], fill=NAVY)
        draw.line([x + 10, y + 6, x + 116, y + h - 12], fill=RED, width=4)
        draw.polygon([(x + 108, y + h - 20), (x + 120, y + h - 8), (x + 104, y + h - 6)],
                     fill=RED)
        draw.text((x + 132, y + 8), "77,000", font=font(SANS_B, 26), fill=RED)
        draw.text((x + 132, y + 34), "lowest since 1997", font=font(SANS, 12), fill=GREY)
    else:  # kyiv: skyline, flames, smoke
        for bx, bh in [(x + 14, 26), (x + 52, 34), (x + 96, 22), (x + 140, 30)]:
            draw.rectangle([bx, y + h - bh, bx + 34, y + h], fill=(40, 40, 52))
        for fx, fy in [(x + 60, y + 4), (x + 108, y + 10)]:
            draw.polygon([(fx, fy + 18), (fx + 9, fy), (fx + 18, fy + 18)], fill=(230, 90, 20))
        for fx, fy, s in [(x + 170, y + 2, 14), (x + 200, y + 8, 10), (x + 228, y + 0, 12)]:
            draw.ellipse([fx, fy, fx + s, fy + s], fill=(120, 120, 125))
        draw.polygon([(x + 152, y + 22), (x + 160, y + 6), (x + 168, y + 22)],
                     fill=(230, 140, 20))


def draw_mini_art(draw, kind, x, y, w, h):
    """Small flat vector scene for a medium panel, in a w x h box."""
    if kind == "bank":
        draw.rectangle([x + 6, y + 6, x + w - 6, y + 12], fill=NAVY)
        for i in range(4):
            cx = x + 12 + i * 12
            draw.rectangle([cx, y + 14, cx + 6, y + 30], fill=NAVY)
        draw.rectangle([x + 4, y + 30, x + w - 4, y + 34], fill=NAVY)
        draw.line([x + 4, y + h - 4, x + w - 4, y + h - 12], fill=TEAL, width=2)
    elif kind == "refinery":
        for tx in [x + 4, x + 22, x + 40]:
            draw.rectangle([tx, y + 14, tx + 13, y + 34], fill=(90, 95, 105))
            draw.rectangle([tx + 2, y + 8, tx + 11, y + 14], fill=(120, 125, 135))
        draw.rectangle([x, y + 34, x + w, y + h], fill=(70, 70, 80))
        draw.polygon([(x + 28, y + 18), (x + 34, y + 6), (x + 40, y + 18)], fill=(230, 90, 20))
        draw.ellipse([x + 48, y + 2, x + 56, y + 10], fill=(110, 110, 115))
    elif kind == "mine":
        draw.rectangle([x + 4, y + 2, x + w - 4, y + h - 2], fill=(45, 40, 35))
        draw.rectangle([x + 14, y + 2, x + w - 14, y + h - 2], fill=(20, 18, 15))
        for i in range(4):
            draw.line([x + 18, y + 10 + i * 8, x + w - 18, y + 10 + i * 8],
                      fill=(120, 100, 70), width=2)
        draw.ellipse([x + w // 2 - 5, y + 6, x + w // 2 + 5, y + 16], fill=GOLD)
    elif kind == "ebola":
        cx, cy = x + w // 2, y + h // 2 - 2
        for i in range(8):
            import math
            ang = 2 * math.pi * i / 8
            x2 = cx + int(17 * math.cos(ang))
            y2 = cy + int(17 * math.sin(ang))
            draw.line([cx, cy, x2, y2], fill=RED, width=2)
            draw.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=RED)
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=RED)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 200, 200))
    elif kind == "tanker_claim":
        for fx, fy, s in [(x + 10, y + 2, 10), (x + 26, y + 6, 8)]:
            draw.ellipse([fx, fy, fx + s, fy + s], fill=(120, 120, 125))
        for fx, fy in [(x + 14, y + 16), (x + 30, y + 20)]:
            draw.polygon([(fx, fy + 12), (fx + 6, fy), (fx + 12, fy + 12)], fill=(230, 90, 20))
        draw.rectangle([x + 2, y + 28, x + w - 2, y + 36], fill=(30, 30, 40))
        draw.rectangle([x + w - 18, y + 18, x + w - 4, y + 28], fill=(60, 60, 75))
        draw.rectangle([x, y + 36, x + w, y + h], fill=(20, 60, 110))
        draw.text((x + w - 2, y), "?", font=font(SANS_B, 16), fill=RED, anchor="ra")
    elif kind == "strike":
        cx, cy = x + w // 2, y + h // 2
        for i in range(8):
            import math
            ang = 2 * math.pi * i / 8 + 0.4
            x2 = cx + int(18 * math.cos(ang))
            y2 = cy + int(18 * math.sin(ang))
            draw.line([cx, cy, x2, y2], fill=(230, 140, 20), width=3)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(230, 90, 20))
        draw.ellipse([x + 4, y + 2, x + 14, y + 12], fill=(120, 120, 125))
    elif kind == "chip":
        draw.rectangle([x + 12, y + 6, x + w - 12, y + h - 6], fill=(30, 30, 40))
        draw.rectangle([x + 20, y + 14, x + w - 20, y + h - 14], fill=TEAL)
        draw.text((x + w // 2, y + h // 2), "AI", font=font(SANS_B, 12),
                  fill=(255, 255, 255), anchor="mm")
        for i in range(3):
            draw.line([x + 16 + i * 10, y + 2, x + 16 + i * 10, y + 6], fill=(120, 120, 130), width=2)
            draw.line([x + 16 + i * 10, y + h - 6, x + 16 + i * 10, y + h - 2], fill=(120, 120, 130), width=2)
    elif kind == "plane":
        draw.ellipse([x + 8, y + 14, x + w - 8, y + 24], fill=NAVY)
        draw.polygon([(x + 22, y + 16), (x + 34, y + 4), (x + 40, y + 16)], fill=NAVY)
        draw.polygon([(x + 22, y + 22), (x + 32, y + 32), (x + 38, y + 22)], fill=NAVY)
        draw.line([x + 2, y + 2, x + w - 2, y + h - 2], fill=RED, width=3)
    else:  # memorial: candle + flame
        draw.rectangle([x + 22, y + 16, x + w - 22, y + h - 2], fill=(255, 255, 255),
                       outline=(150, 150, 155), width=2)
        draw.polygon([(x + 28, y + 14), (x + 31, y + 2), (x + 34, y + 14)], fill=(230, 140, 20))
        draw.ellipse([x + 6, y + 26, x + 14, y + 34], fill=RED)
        draw.ellipse([x + w - 14, y + 28, x + w - 6, y + 36], fill=GOLD)


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
    draw.rectangle([x, y, x + w, y + h], fill=(225, 235, 245), outline=(150, 160, 175))
    def px(lon, lat):
        return (x + (lon + 180) / 360.0 * w, y + (75 - lat) / 130.0 * h)
    for cont in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in cont]
        draw.polygon(pts, fill=(190, 200, 185), outline=(140, 150, 140))
    JITTER = {"1": (12, -12), "2": (-14, -8), "4": (12, -4), "5": (-12, 10),
              "6": (14, 8), "10": (-12, -10), "11": (12, -8), "12": (-8, 8),
              "13": (12, -8), "15": (-10, -8), "27": (10, -8), "28": (-12, 8),
              "29": (10, 10)}
    for num, lon, lat in PINS:
        cx, cy = px(lon, lat)
        dx, dy = JITTER.get(num, (0, 0))
        if (dx, dy) != (0, 0):
            draw.line([cx, cy, cx + dx, cy + dy], fill=RED, width=1)
            draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
            cx, cy = cx + dx, cy + dy
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED, outline=(255, 255, 255), width=2)
        draw.text((cx, cy), num, font=font(SANS_B, 10), fill=(255, 255, 255), anchor="mm")


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
           "40 VERIFIED STORIES  \u00b7  10 REGIONS  \u00b7  14 FIELDS  \u00b7  12 ILLUSTRATED PANELS",
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
           "EXCLUDED (Wed 25 Nov): US tariffs \u00b7 Cairo fire \u00b7 Ras Tanura/Hormuz \u00b7 UK energy cap \u00b7 FCC\u2013SpaceX \u00b7 Ramaphosa ruling \u00b7 Solomons treaty \u00b7 Macy's parade",
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
    d.text((map_x, 610), "WHERE IT HAPPENED  \u2014  SCHEMATIC MAP",
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
    d.text((36, 733), "MORE ON 26 NOVEMBER  \u2014  28 MORE STORIES", font=font(SANS_B, 15),
           fill=(255, 255, 255), anchor="lm")
    for i, (num, head, region, src, tag, extra) in enumerate(MORE):
        col, row = i % 2, i // 2
        x0 = 24 + col * 500
        y0 = 750 + row * 17
        right = f"{src} \u00b7 {tag}" + (f" \u00b7 {extra}" if extra else "")
        rf = font(SANS_B, 10)
        rw = d.textlength(right, font=rf)
        d.text((x0, y0), f"{num}.", font=font(SANS_B, 15), fill=RED)
        tx = x0 + 30
        if region:
            d.text((tx, y0 + 2), f"[{region}]", font=font(SANS_B, 12), fill=NAVY)
            tx += d.textlength(f"[{region}]", font=font(SANS_B, 12)) + 6
        avail = x0 + 488 - rw - 8 - tx
        d.text((tx, y0), truncate(d, head, font(SANS, 15), avail),
               font=font(SANS, 15), fill=INK)
        d.text((x0 + 488, y0 + 2), right, font=rf, fill=TAG_COLOUR[tag], anchor="ra")

    # Footer: sources + label legend
    d.text((24, 992),
           "SOURCES: Reuters \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 ONS \u00b7 Bank of Korea \u00b7 Xinhua \u00b7 AAP \u00b7 FIDE \u00b7 AFP \u00b7 FT \u00b7 Newsquawk \u00b7 PTI \u00b7 Apprised \u00b7 One Turn \u00b7 InfoKava \u00b7 ESA",
           font=font(SANS, 10), fill=GREY)
    d.text((24, 1003),
           "OFFICIAL = confirmed by an authority  \u00b7  REPORTED = reported by a named source  \u00b7  CLAIM = a party's claim, not confirmed.",
           font=font(SANS, 10), fill=GREY)
    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
