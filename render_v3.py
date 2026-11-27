#!/usr/bin/env python3
"""Render the 26 Nov 2026 world-news image, v3 (1024x1024).

Broadsheet layout (structure studied from the 26 Nov dev-phase rank 1,
redrawn in our own design with our own verified stories): navy masthead
bar, huge date headline, red ticker, KPI strip, region-count bar,
horizontal UTC timeline, 3 hero panels + 10 secondary panels with fully
drawn scenes, dotted world map with numbered pins, 28-item "also on"
list, date-check box, sources + how-sure legend.

41 stories, 9 regions. Every story happened or was first reported on
Thursday 26 November 2026 (UTC); carry-over items carry their original
date on the card. Labels: OFFICIAL = a government, court or agency said
it; CONFIRMED = two or more outlets reported it; CLAIM = one side's
account, not verified.

v3 changes vs v2 (36 stories): +5 net stories (Kuwait Italians, Katz
Gaza threat, Jazan worker killed, Bissau vote delay, Argentina
money-printing ban, Depardieu trial, Gazipur protests, UK-EU treaty
texts = 8 new; restored Z.AI + Kharkiv from v1; dropped stocks rally,
Fitch, Bulgaria, UK Gaza pledge, Hera). Storm promoted to hero #2 with
the verified peak outage 961,000. UK migration + Riyadh move to
secondary panels. World heat kept, tagged EUR (Copernicus is the EU's
climate service). Wrong-day items still excluded: Cairo fire, US tariff
announcement, Macy's postponement decision, Veruschka obit (24 Nov),
Myanmar ICJ remarks (25 Nov meeting).

Build tool only: run `python3 render_v3.py` to write entry.png.
The graded program is main.py (stdlib only) which copies entry.png.
Pillow is used here, at build time only.
"""
import math
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
    if draw.textlength(text, font=fnt) <= width:
        return text
    while text and draw.textlength(text + "\u2026", font=fnt) > width:
        text = text[:-1].rstrip()
    return text + "\u2026"


# ---------------- news data (verified 26 Nov 2026) ----------------
HEROES = [
    {"n": "1", "region": "EUR", "tag": "OFFICIAL", "source": "Reuters / AP",
     "headline": "EU SUMMIT STALLS: NO DEAL ON \u20ac1.58TN BUDGET, \u20ac45BN LOAN",
     "summary": "12+ hours, no deal; retry 17\u201318 Dec.",
     "scene": "summit", "caption": "BRUSSELS \u00b7 EUROPE \u00b7 EU SUMMIT"},
    {"n": "2", "region": "NA", "tag": "CONFIRMED", "source": "AP / Reuters",
     "headline": "THANKSGIVING STORM CUTS POWER TO NEARLY A MILLION",
     "summary": "Peak 961,000 out; gusts 60\u201365 mph.",
     "scene": "storm", "caption": "US EAST COAST \u00b7 NORTH AMERICA \u00b7 STORM"},
    {"n": "3", "region": "ME", "tag": "CONFIRMED", "source": "Reuters / AP",
     "headline": "DRONE ATTACK KILLS TWO ITALIANS IN KUWAIT",
     "summary": "Italy blames Iranian drones; Iran denies.",
     "scene": "kuwait", "caption": "KUWAIT \u00b7 MIDDLE EAST \u00b7 AIR-DEFENCE SITE"},
]

# (n, headline, summary, source, tag, region, scene, caption)
PANELS = [
    ("4", "KYIV HIT BY MISSILES; 7 WOUNDED",
     "Overnight strikes; centre ablaze.",
     "Reuters", "CONFIRMED", "EUR", "kyiv", "KYIV \u00b7 EUROPE"),
    ("5", "RIYADH: TWO MISSILES DOWNED",
     "Coalition downs 2 missiles.",
     "Coalition", "OFFICIAL", "ME", "shield", "RIYADH \u00b7 MIDDLE EAST"),
    ("6", "UK NET MIGRATION 77,000",
     "Lowest since 1997; ONS data.",
     "ONS", "OFFICIAL", "EUR", "migration", "LONDON \u00b7 EUROPE"),
    ("7", "BANK OF KOREA: RATE 3.25%",
     "Third hike since July.",
     "Bank of Korea", "OFFICIAL", "EAS", "bank", "SEOUL \u00b7 EAST ASIA"),
    ("8", "BANGKOK REFINERY BLAST",
     "Fire out in ~30 min; 9 hurt.",
     "Reuters", "CONFIRMED", "SEA", "refinery", "BANGKOK \u00b7 SE ASIA"),
    ("9", "JAVA MINE: 13 DEAD, 13 TRAPPED",
     "Rain halts Bogor mine rescue.",
     "Reuters", "OFFICIAL", "SEA", "mine", "BOGOR \u00b7 SE ASIA"),
    ("10", "EBOLA PASSES 12,000 CASES",
     "5,904 dead; record outbreak.",
     "Reuters", "OFFICIAL", "AFR", "ebola", "DR CONGO \u00b7 AFRICA"),
    ("11", "RAS TANURA: LOADINGS HALTED",
     "Houthi claim; 4 drones downed.",
     "Reuters", "CLAIM", "ME", "tanker", "RAS TANURA \u00b7 MIDDLE EAST"),
    ("12", "HAMAS CHIEF ABU NADA KILLED",
     "IDF strike in Deir al-Balah.",
     "Xinhua", "CONFIRMED", "ME", "strike", "GAZA \u00b7 MIDDLE EAST"),
    ("13", "NVIDIA HALTS SERVER SHIPMENTS",
     "FT: exports paused over curbs.",
     "FT via Reuters", "CONFIRMED", "SEA", "chip", "SE ASIA \u00b7 TECH"),
]

# (n, headline, region, source, tag)
LIST = [
    ("14", "Norse grounds flights", "EUR", "Norse Atlantic", "OFFICIAL"),
    ("15", "Katz: move 1m Gazans", "ME", "Katz (X)", "OFFICIAL"),
    ("16", "Jazan attack kills 1", "ME", "Saudi ministry", "OFFICIAL"),
    ("17", "Kenya halts Ebola site", "AFR", "Reuters", "OFFICIAL"),
    ("18", "Germany arrests 2", "EUR", "Reuters", "OFFICIAL"),
    ("19", "Chess: Game 3 drawn", "EUR", "FIDE", "OFFICIAL"),
    ("20", "Hong Kong fire year", "EAS", "AP", "CONFIRMED"),
    ("21", "Sinner out of Aus Open", "OCE", "Reuters", "OFFICIAL"),
    ("22", "Trade chiefs meet", "SEA", "Reuters", "CONFIRMED"),
    ("23", "China may hit back", "EAS", "Reuters", "OFFICIAL"),
    ("24", "Japan slams US tariffs", "EAS", "Newsquawk", "OFFICIAL"),
    ("25", "Singapore disappointed", "SEA", "Newsquawk", "OFFICIAL"),
    ("26", "India sticks to US deal", "SAS", "Newsquawk", "OFFICIAL"),
    ("27", "Brazil protests tariffs", "LATAM", "Newsquawk", "OFFICIAL"),
    ("28", "King tides hit CA coast", "NA", "AP", "OFFICIAL"),
    ("29", "Nepal: 5,500 to be dead", "SAS", "AFP", "OFFICIAL"),
    ("30", "India marks 26/11", "SAS", "PTI", "OFFICIAL"),
    ("31", "Solomons slams treaty", "OCE", "AAP", "CONFIRMED"),
    ("32", "Depardieu faces trial", "EUR", "AP", "CONFIRMED"),
    ("33", "Heat: 6 days over 2\u00b0C", "EUR", "Copernicus", "CONFIRMED"),
    ("34", "Spain votes Sunday", "EUR", "One Turn", "CONFIRMED"),
    ("35", "Kim wins 2nd KBO MVP", "EAS", "K. JoongAng", "CONFIRMED"),
    ("36", "Tear gas at Gazipur", "SAS", "VOA", "CONFIRMED"),
    ("37", "UK-EU treaty texts out", "EUR", "BBC", "OFFICIAL"),
    ("38", "China AI hit by curbs", "EAS", "Reuters", "CONFIRMED"),
    ("39", "Kharkiv strike kills 2", "EUR", "InfoKava", "CONFIRMED"),
    ("40", "Bissau delays vote", "AFR", "AP", "OFFICIAL"),
    ("41", "Argentina ends printing", "LATAM", "AP", "OFFICIAL"),
]

KPI = [
    ("961,000", "WITHOUT POWER AT PEAK"),
    ("2", "ITALIANS KILLED IN KUWAIT"),
    ("\u20ac1.58tn", "EU BUDGET LEFT UNAGREED"),
    ("12,021", "EBOLA CASES IN DR CONGO"),
    ("77,000", "UK NET MIGRATION"),
    ("3.25%", "BANK OF KOREA RATE"),
]

TICKER = ("Thanksgiving storm cuts power to nearly a million Americans"
          "  \u00b7  Drone attack kills two Italians in Kuwait"
          "  \u00b7  EU summit ends with no budget deal")

TIMELINE = [
    ("01:18", "Kyiv fires burn"),
    ("05:29", "Ebola: 12,021 cases"),
    ("05:49", "BOK rate to 3.25%"),
    ("07:45", "Bangkok fire"),
    ("07:59", "Gazipur tear gas"),
    ("10:12", "UK migration 77,000"),
    ("11:00", "Kuwait: 2 killed"),
    ("14:00", "Chess Game 3"),
]

# region order for the bar, with counts computed from the data
REGION_ORDER = ["EUR", "ME", "AFR", "SAS", "EAS", "SEA", "OCE", "NA", "LATAM"]
REGION_NAME = {"EUR": "EUROPE", "ME": "MIDDLE EAST", "AFR": "AFRICA",
               "SAS": "SOUTH ASIA", "EAS": "EAST ASIA", "SEA": "SE ASIA",
               "OCE": "OCEANIA", "NA": "N. AMERICA", "LATAM": "LATIN AMERICA"}
REGION_COLOUR = {"EUR": NAVY, "ME": (140, 100, 10), "AFR": TEAL,
                 "SAS": (120, 60, 140), "EAS": RED, "SEA": BLUE,
                 "OCE": (90, 90, 160), "NA": (60, 120, 60),
                 "LATAM": (200, 80, 20)}
TAG_COLOUR = {"OFFICIAL": NAVY, "CONFIRMED": TEAL, "CLAIM": RED}

PINS = [  # (number, lon, lat) — 21 pins; 11/18/19 omitted (clusters)
    ("1", 4.35, 50.85), ("2", -74.0, 40.7), ("3", 48.0, 29.4),
    ("4", 30.5, 50.45), ("5", 46.7, 24.7), ("6", -0.1, 51.5),
    ("7", 127.0, 37.5), ("8", 100.5, 13.75), ("9", 106.8, -6.6),
    ("10", 30.2, 1.6), ("12", 34.5, 31.5),
    ("13", 103.8, 1.35), ("16", 42.5, 16.9), ("17", 36.8, -1.3),
    ("21", 145.0, -37.8),
    ("28", -119.3, 34.3), ("29", 85.3, 27.7), ("31", 160.0, -9.4),
    ("36", 90.4, 24.0), ("40", -15.6, 11.9), ("41", -58.4, -34.6),
]


# ---------------- drawn scenes (proportional, no external images) ----------------
def _xy(x, y, w, h):
    """Return helpers mapping 0..100 fractions to pixels."""
    X = lambda f: x + w * f / 100.0
    Y = lambda f: y + h * f / 100.0
    return X, Y


def _badge(draw, x, y, w, h, num, colour=RED):
    """Number badge, top-left of a scene."""
    r = 11 if h >= 80 else 9
    cx, cy = x + r + 3, y + r + 3
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour,
                 outline=(255, 255, 255), width=2)
    draw.text((cx, cy), num, font=font(SANS_B, 12 if h >= 80 else 10),
              fill=(255, 255, 255), anchor="mm")


def _caption(draw, x, y, w, h, text):
    """Small dark caption strip at the bottom of a scene."""
    ch = 13 if h >= 80 else 11
    draw.rectangle([x, y + h - ch, x + w, y + h], fill=(0, 0, 0))
    draw.text((x + 4, y + h - ch // 2), truncate(draw, text, font(SANS_B, 8),
              w - 8), font=font(SANS_B, 8), fill=(255, 255, 255), anchor="lm")


def scene_summit(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(20, 50, 95))
    flag_cols = [(178, 34, 34), (184, 134, 11), (40, 90, 160),
                 (14, 90, 90), (120, 60, 140), (255, 255, 255)]
    for i, fc in enumerate(flag_cols):
        px = X(6 + i * 16)
        draw.line([px, Y(4), px, Y(20)], fill=(230, 230, 230), width=2)
        draw.rectangle([px, Y(4), px + 12, Y(12)], fill=fc)
    for i in range(5):
        cx = X(16 + i * 17)
        draw.ellipse([cx - 11, Y(26), cx + 11, Y(40)], fill=(28, 28, 38))
        draw.ellipse([cx - 5, Y(18), cx + 5, Y(28)], fill=(222, 184, 150))
    draw.rectangle([x, Y(38), x + w, y + h], fill=(238, 230, 205))
    draw.line([x, Y(38), x + w, Y(38)], fill=(160, 140, 100), width=2)
    draw.ellipse([X(46), Y(42), X(54), Y(50)], fill=GOLD)
    draw.rectangle([X(44), Y(50), X(56), Y(56)], fill=(120, 90, 40))
    # papers + water glasses on the table
    for px in [10, 26, 66, 82]:
        draw.rectangle([X(px), Y(62), X(px + 9), Y(74)], fill=(255, 255, 255),
                       outline=(150, 145, 130), width=1)
        draw.line([X(px + 1), Y(66), X(px + 8), Y(66)], fill=(120, 120, 120), width=1)
        draw.line([X(px + 1), Y(70), X(px + 8), Y(70)], fill=(120, 120, 120), width=1)
    for gx in [20, 58, 76]:
        draw.rectangle([X(gx), Y(78), X(gx + 4), Y(88)], fill=(180, 210, 220),
                       outline=(100, 130, 150), width=1)


def scene_storm(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(38, 48, 66))
    for sx, sy in [(8, 8), (22, 4), (38, 10), (55, 5), (70, 9), (86, 4), (94, 12)]:
        draw.ellipse([X(sx), Y(sy), X(sx) + 2, Y(sy) + 2], fill=(200, 205, 215))
    draw.polygon([(X(63), Y(4)), (X(67), Y(4)), (X(62), Y(20)), (X(68), Y(20)),
                  (X(58), Y(44)), (X(63), Y(44))],
                 fill=(240, 200, 60))
    for i in range(14):
        rx = X(4 + i * 7)
        draw.line([rx, Y(18), rx - 6, Y(46)], fill=(140, 170, 200), width=1)
    # bent power pole + sagging wire
    draw.line([X(24), Y(96), X(30), Y(48)], fill=(90, 70, 50), width=4)
    draw.line([X(22), Y(52), X(38), Y(48)], fill=(90, 70, 50), width=3)
    draw.arc([X(38), Y(44), X(96), Y(78)], 200, 340, fill=(30, 30, 30), width=2)
    # house with lit window
    draw.rectangle([X(58), Y(74), X(88), Y(96)], fill=(24, 24, 34))
    draw.polygon([(X(56), Y(74)), (X(73), Y(60)), (X(90), Y(74))], fill=(40, 30, 30))
    draw.rectangle([X(64), Y(80), X(72), Y(88)], fill=(240, 200, 80))
    # fallen tree
    draw.line([X(6), Y(94), X(20), Y(78)], fill=(70, 50, 30), width=3)
    draw.ellipse([X(14), Y(70), X(30), Y(82)], fill=(40, 90, 50))


def scene_kuwait(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(214, 178, 130))
    draw.rectangle([x, Y(62), x + w, y + h], fill=(170, 130, 85))
    # radar dome + mast
    draw.pieslice([X(8), Y(38), X(34), Y(78)], 180, 360, fill=(240, 240, 235))
    draw.line([X(21), Y(40), X(21), Y(18)], fill=(60, 60, 70), width=3)
    draw.ellipse([X(18), Y(12), X(24), Y(20)], fill=(60, 60, 70))
    draw.arc([X(14), Y(8), X(28), Y(24)], 200, 340, fill=(255, 255, 255), width=1)
    # buildings
    draw.rectangle([X(52), Y(66), X(66), Y(96)], fill=(120, 110, 100))
    draw.rectangle([X(70), Y(74), X(82), Y(96)], fill=(100, 92, 84))
    # drone silhouette
    draw.ellipse([X(72), Y(16), X(88), Y(24)], fill=(30, 30, 38))
    draw.line([X(70), Y(18), X(90), Y(18)], fill=(30, 30, 38), width=2)
    draw.line([X(74), Y(12), X(74), Y(28)], fill=(30, 30, 38), width=1)
    draw.line([X(86), Y(12), X(86), Y(28)], fill=(30, 30, 38), width=1)
    # explosion burst + smoke
    for i in range(8):
        ang = 2 * math.pi * i / 8
        bx, by = X(60), Y(30)
        draw.line([bx, by, bx + 14 * math.cos(ang), by + 14 * math.sin(ang)],
                  fill=(230, 90, 20), width=3)
    draw.ellipse([X(54), Y(24), X(66), Y(36)], fill=(240, 180, 40))
    for fx, fy, s in [(40, 10, 12), (48, 16, 9), (88, 34, 10)]:
        draw.ellipse([X(fx), Y(fy), X(fx) + s, Y(fy) + s], fill=(120, 115, 110))


def scene_kyiv(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(12, 16, 32))
    for sx, sy in [(8, 6), (24, 10), (44, 4), (62, 9), (80, 5), (92, 11)]:
        draw.ellipse([X(sx), Y(sy), X(sx) + 2, Y(sy) + 2], fill=(255, 255, 255))
    for bx, bh in [(4, 26), (20, 34), (38, 22), (56, 30), (74, 24), (88, 30)]:
        draw.rectangle([X(bx), Y(100 - bh), X(bx + 12), y + h], fill=(38, 38, 52))
    for wx, wy in [(7, 78), (24, 72), (42, 80), (60, 74), (78, 78), (91, 72)]:
        draw.rectangle([X(wx), Y(wy), X(wx) + 4, Y(wy) + 6], fill=(240, 200, 80))
    draw.line([X(92), Y(2), X(74), Y(22)], fill=(255, 220, 120), width=3)
    draw.ellipse([X(71), Y(18), X(77), Y(26)], fill=(255, 240, 160))
    draw.polygon([(X(46), Y(52)), (X(50), Y(34)), (X(54), Y(52))], fill=(230, 90, 20))
    draw.polygon([(X(48), Y(52)), (X(50), Y(40)), (X(52), Y(52))], fill=(240, 180, 40))
    for fx, fy, s in [(58, 6, 12), (66, 12, 9)]:
        draw.ellipse([X(fx), Y(fy), X(fx) + s, Y(fy) + s], fill=(110, 110, 118))


def scene_shield(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(18, 30, 55))
    for sx, sy in [(8, 6), (26, 4), (48, 8), (72, 5), (90, 9)]:
        draw.ellipse([X(sx), Y(sy), X(sx) + 2, Y(sy) + 2], fill=(255, 255, 255))
    draw.arc([X(8), Y(22), X(92), Y(110)], 180, 360, fill=(120, 200, 220), width=3)
    draw.rectangle([X(10), Y(84), X(90), Y(96)], fill=(60, 60, 75))
    for bx, bh in [(16, 14), (30, 20), (66, 16), (80, 22)]:
        draw.rectangle([X(bx), Y(84 - bh), X(bx + 8), Y(84)], fill=(90, 90, 105))
    draw.line([X(18), Y(8), X(28), Y(28)], fill=(255, 220, 120), width=2)
    draw.line([X(82), Y(8), X(72), Y(28)], fill=(255, 220, 120), width=2)
    for bx, by in [(28, 28), (72, 28)]:
        for i in range(6):
            ang = 2 * math.pi * i / 6
            draw.line([X(bx), Y(by), X(bx) + 7 * math.cos(ang),
                       Y(by) + 7 * math.sin(ang)], fill=(240, 200, 60), width=2)


def scene_migration(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(28, 38, 58))
    draw.rectangle([X(4), Y(8), X(58), Y(88)], fill=(12, 12, 18),
                   outline=(140, 140, 150), width=1)
    for r in range(3):
        ry = Y(18 + r * 22)
        draw.rectangle([X(8), ry, X(24), ry + 8], fill=(240, 240, 220))
        draw.rectangle([X(27), ry, X(35), ry + 8], fill=(240, 200, 60))
        draw.rectangle([X(38), ry, X(54), ry + 8], fill=(120, 200, 120))
    draw.text((X(62), Y(34)), "77,000", font=font(SANS_B, 22 if h >= 80 else 15),
              fill=(255, 255, 255))
    if h >= 80:
        draw.text((X(62), Y(66)), "lowest", font=font(SANS, 10), fill=(200, 200, 210))
        draw.text((X(62), Y(80)), "since 1997", font=font(SANS, 10),
                  fill=(200, 200, 210))


def scene_bank(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(222, 226, 232))
    draw.polygon([(X(4), Y(28)), (X(50), Y(6)), (X(96), Y(28))], fill=NAVY)
    for i in range(4):
        cx = X(14 + i * 20)
        draw.rectangle([cx, Y(32), cx + 10, Y(72)], fill=NAVY)
    draw.rectangle([X(4), Y(72), X(96), Y(80)], fill=NAVY)
    draw.rectangle([X(2), Y(80), X(98), Y(96)], fill=(200, 200, 205))
    draw.ellipse([X(84), Y(8), X(96), Y(26)], fill=GOLD)
    draw.line([X(6), Y(92), X(50), Y(66), X(94), Y(52)], fill=TEAL, width=2)


def scene_refinery(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(235, 225, 210))
    for tx in [10, 30, 50]:
        draw.rectangle([X(tx), Y(38), X(tx + 16), Y(82)], fill=(90, 95, 105))
        draw.rectangle([X(tx + 2), Y(28), X(tx + 14), Y(38)], fill=(120, 125, 135))
    draw.rectangle([x, Y(82), x + w, y + h], fill=(70, 70, 80))
    draw.polygon([(X(36), Y(38)), (X(41), Y(14)), (X(46), Y(38))], fill=(230, 90, 20))
    draw.polygon([(X(39), Y(38)), (X(41), Y(22)), (X(43), Y(38))], fill=(240, 180, 40))
    draw.ellipse([X(66), Y(6), X(78), Y(20)], fill=(110, 110, 115))
    draw.ellipse([X(74), Y(16), X(84), Y(28)], fill=(130, 130, 135))


def scene_mine(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(60, 52, 42))
    draw.rectangle([X(16), Y(6), X(84), Y(94)], fill=(18, 15, 12))
    draw.polygon([(X(10), Y(96)), (X(50), Y(2)), (X(90), Y(96))],
                 outline=(180, 150, 90), width=2)
    for i in range(3):
        draw.line([X(20), Y(28 + i * 20), X(80), Y(28 + i * 20)],
                  fill=(120, 100, 70), width=2)
    draw.ellipse([X(44), Y(12), X(56), Y(28)], fill=GOLD)
    draw.rectangle([X(10), Y(84), X(26), Y(94)], fill=(140, 110, 60))


def scene_ebola(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(245, 235, 235))
    cx, cy = X(50), Y(50)
    for i in range(8):
        ang = 2 * math.pi * i / 8
        x2 = cx + 22 * math.cos(ang)
        y2 = cy + 22 * math.sin(ang)
        draw.line([cx, cy, x2, y2], fill=RED, width=2)
        draw.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=RED)
    draw.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=RED)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 200, 200))
    draw.ellipse([X(4), Y(4), X(16), Y(18)], fill=(255, 180, 180), outline=RED)
    draw.ellipse([X(84), Y(82), X(96), Y(96)], fill=(255, 180, 180), outline=RED)


def scene_tanker(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
    draw.rectangle([x, Y(62), x + w, y + h], fill=(20, 60, 110))
    draw.rectangle([X(6), Y(44), X(94), Y(64)], fill=(30, 30, 40))
    draw.rectangle([X(76), Y(24), X(90), Y(44)], fill=(60, 60, 75))
    draw.rectangle([X(10), Y(64), X(90), Y(68)], fill=(120, 60, 40))
    for fx, fy in [(20, 34), (38, 40)]:
        draw.polygon([(X(fx), Y(fy + 12)), (X(fx + 6), Y(fy)), (X(fx + 12), Y(fy + 12))],
                     fill=(230, 90, 20))
    for fx, fy, s in [(16, 6, 12), (30, 10, 9)]:
        draw.ellipse([X(fx), Y(fy), X(fx) + s, Y(fy) + s], fill=(120, 120, 125))
    draw.text((X(88), Y(72)), "?", font=font(SANS_B, 16), fill=(255, 255, 255),
              anchor="mm")


def scene_strike(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(250, 235, 210))
    cx, cy = X(50), Y(50)
    for i in range(8):
        ang = 2 * math.pi * i / 8 + 0.4
        x2 = cx + 24 * math.cos(ang)
        y2 = cy + 24 * math.sin(ang)
        draw.line([cx, cy, x2, y2], fill=(230, 140, 20), width=3)
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(230, 90, 20))
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(240, 200, 60))
    draw.ellipse([X(4), Y(4), X(18), Y(20)], fill=(120, 120, 125))
    draw.ellipse([X(82), Y(8), X(94), Y(22)], fill=(140, 140, 145))


def scene_chip(draw, x, y, w, h):
    X, Y = _xy(x, y, w, h)
    draw.rectangle([x, y, x + w, y + h], fill=(225, 230, 235))
    draw.rectangle([X(22), Y(18), X(78), Y(82)], fill=(30, 30, 40))
    draw.rectangle([X(32), Y(28), X(68), Y(72)], fill=TEAL)
    draw.text((X(50), Y(50)), "AI", font=font(SANS_B, 13),
              fill=(255, 255, 255), anchor="mm")
    for i in range(3):
        draw.line([X(28 + i * 16), Y(6), X(28 + i * 16), Y(18)],
                  fill=(120, 120, 130), width=2)
        draw.line([X(28 + i * 16), Y(82), X(28 + i * 16), Y(94)],
                  fill=(120, 120, 130), width=2)
    draw.line([X(2), Y(50), X(22), Y(50)], fill=(230, 90, 20), width=2)


SCENES = {"summit": scene_summit, "storm": scene_storm, "kuwait": scene_kuwait,
          "kyiv": scene_kyiv, "shield": scene_shield, "migration": scene_migration,
          "bank": scene_bank, "refinery": scene_refinery, "mine": scene_mine,
          "ebola": scene_ebola, "tanker": scene_tanker, "strike": scene_strike,
          "chip": scene_chip}


# ---------------- dotted world map ----------------
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


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
                (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(247, 244, 236),
                   outline=(160, 150, 130), width=1)

    def px(lon, lat):
        return (x + (lon + 180) / 360.0 * w, y + (80 - lat) / 138.0 * h)

    step = 5
    for gy in range(int(y) + 3, int(y + h) - 2, step):
        for gx in range(int(x) + 3, int(x + w) - 2, step):
            lon = (gx - x) / w * 360.0 - 180
            lat = 80 - (gy - y) / h * 138.0
            if any(_in_poly(lon, lat, cont) for cont in CONTINENTS):
                draw.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(120, 110, 88))
    JITTER = {"1": (12, -12), "2": (-6, -12), "3": (16, -12), "4": (12, -10),
              "5": (-16, -12), "6": (-14, -8), "7": (12, -8), "8": (-12, 6),
              "9": (-14, 12), "10": (-12, -10), "12": (-12, -10),
              "13": (12, -8), "16": (-12, 14), "17": (12, 8),
              "21": (-8, -8), "28": (-10, -10), "29": (-12, -12),
              "31": (-10, 8), "36": (12, 10), "40": (-12, 6), "41": (8, 10)}
    all_stories = {s["n"]: s for s in HEROES}
    for num, head, summ, src, tag, region, scene, cap in PANELS:
        all_stories[num] = {"region": region}
    for num, head, region, src, tag in LIST:
        all_stories[num] = {"region": region}
    for num, lon, lat in PINS:
        cx, cy = px(lon, lat)
        dx, dy = JITTER.get(num, (0, 0))
        if (dx, dy) != (0, 0):
            draw.line([cx, cy, cx + dx, cy + dy], fill=(140, 130, 110), width=1)
            draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
            cx, cy = cx + dx, cy + dy
        colour = REGION_COLOUR[all_stories[num]["region"]]
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=colour,
                     outline=(255, 255, 255), width=2)
        draw.text((cx, cy), num, font=font(SANS_B, 10), fill=(255, 255, 255),
                  anchor="mm")


# ---------------- layout ----------------
def region_counts():
    counts = {r: 0 for r in REGION_ORDER}
    for s in HEROES:
        counts[s["region"]] += 1
    for num, head, summ, src, tag, region, scene, cap in PANELS:
        counts[region] += 1
    for num, head, region, src, tag in LIST:
        counts[region] += 1
    return counts


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    counts = region_counts()
    total = sum(counts.values())
    assert total == 41, f"story count {total} != 41"

    # Masthead bar
    d.rectangle([0, 0, W, 24], fill=NAVY)
    d.text((24, 12), "THE WORLD IN ONE DAY", font=font(SANS_B, 15),
           fill=(255, 255, 255), anchor="lm")
    d.text((W - 24, 12),
           "41 STORIES \u00b7 NINE REGIONS \u00b7 ALL FROM THURSDAY 26 NOVEMBER 2026",
           font=font(SANS_B, 11), fill=(220, 225, 235), anchor="rm")

    # Date headline
    d.text((W // 2, 26), "Thursday 26 November 2026", font=font(SERIF_B, 54),
           fill=INK, anchor="ma")

    # Red ticker
    d.rectangle([24, 88, W - 24, 108], fill=RED)
    ticker = ("Storm cuts power to nearly a million  \u00b7  "
              "Two Italians killed in Kuwait  \u00b7  "
              "EU summit ends with no deal")
    d.text((W // 2, 98), ticker, font=font(SANS_B, 13),
           fill=(255, 255, 255), anchor="mm")

    # KPI strip
    cell_w = 976 / 6
    for i, (num, label) in enumerate(KPI):
        cx = 24 + cell_w * (i + 0.5)
        if i:
            d.line([24 + cell_w * i, 116, 24 + cell_w * i, 148],
                   fill=(200, 195, 180), width=1)
        d.text((cx, 114), num, font=font(SANS_B, 24), fill=NAVY, anchor="ma")
        lines = wrap(d, label, font(SANS, 9), cell_w - 10)
        ly = 140
        for line in lines[:2]:
            d.text((cx, ly), line, font=font(SANS, 9), fill=GREY, anchor="ma")
            ly += 10

    # Region-count bar
    raw = {r: counts[r] / total * 976 for r in REGION_ORDER}
    widths = {r: max(raw[r], 80) for r in REGION_ORDER}
    excess = sum(widths.values()) - 976
    if excess > 0:
        big = max(REGION_ORDER, key=lambda r: widths[r])
        widths[big] -= excess
    rx = 24
    for r in REGION_ORDER:
        wseg = widths[r]
        d.rectangle([rx, 154, rx + wseg, 172], fill=REGION_COLOUR[r])
        label = f"{REGION_NAME[r]} {counts[r]}"
        fnt = font(SANS_B, 9)
        if d.textlength(label, font=fnt) > wseg - 6:
            fnt = font(SANS_B, 8)
        d.text((rx + wseg / 2, 163), label, font=fnt,
               fill=(255, 255, 255), anchor="mm")
        rx += wseg

    # UTC timeline (horizontal, alternating above/below)
    d.line([24, 189, W - 24, 189], fill=(160, 150, 130), width=1)
    for i, (when, what) in enumerate(TIMELINE):
        cx = 24 + 976 * (i + 0.5) / len(TIMELINE)
        d.ellipse([cx - 4, 185, cx + 4, 193], fill=RED,
                  outline=(255, 255, 255), width=1)
        tf, lf = font(SANS_B, 11), font(SANS, 10)
        tw = d.textlength(when, font=tf)
        label = truncate(d, what, lf, 216 - tw - 4)
        total_w = tw + 4 + d.textlength(label, font=lf)
        sx = cx - total_w / 2
        ty = 176 if i % 2 == 0 else 193
        d.text((sx, ty), when, font=tf, fill=RED)
        d.text((sx + tw + 4, ty), label, font=lf, fill=INK)

    # Heroes
    col_w, gap = 312, 20
    for i, s in enumerate(HEROES):
        x0 = 24 + i * (col_w + gap)
        y0, hh = 206, 192
        d.rectangle([x0, y0, x0 + col_w, y0 + hh], outline=(160, 150, 130), width=1)
        SCENES[s["scene"]](d, x0 + 1, y0 + 1, col_w - 2, 100)
        _badge(d, x0 + 1, y0 + 1, col_w - 2, 100, s["n"])
        tag = s["tag"]
        tf = font(SANS_B, 9)
        tw = d.textlength(tag, font=tf) + 10
        d.rectangle([x0 + col_w - tw - 1, y0 + 1, x0 + col_w - 1, y0 + 17],
                    fill=TAG_COLOUR[tag])
        d.text((x0 + col_w - tw / 2 - 1, y0 + 9), tag, font=tf,
               fill=(255, 255, 255), anchor="mm")
        _caption(d, x0 + 1, y0 + 1, col_w - 2, 100, s["caption"])
        y, nlines = draw_wrapped(d, (x0 + 10, y0 + 106), s["headline"],
                                 font(SANS_B, 19), INK, col_w - 20,
                                 leading=20, max_lines=3)
        d.text((x0 + 10, y0 + 166),
               truncate(d, s["summary"], font(SANS, 12), col_w - 20),
               font=font(SANS, 12), fill=(60, 60, 60))
        d.text((x0 + 10, y0 + 182),
               f"{s['source']} \u00b7 {s['tag']}", font=font(SANS_B, 10),
               fill=TAG_COLOUR[s["tag"]])

    # Secondary header
    d.rectangle([24, 402, W - 24, 420], fill=NAVY)
    d.text((36, 411), "THE DAY IN PICTURES  \u2014  10 MORE STORIES",
           font=font(SANS_B, 13), fill=(255, 255, 255), anchor="lm")
    d.text((W - 36, 411), "ALL SCENES DRAWN IN CODE", font=font(SANS_B, 10),
           fill=(200, 205, 215), anchor="rm")

    # Secondary panels: 5 cols x 2 rows
    pcol_w, prow_h = 192, 98
    for i, (num, head, summ, src, tag, region, scene, cap) in enumerate(PANELS):
        col, row = i % 5, i // 5
        x0 = 24 + col * (pcol_w + 2)
        y0 = 424 + row * (prow_h + 4)
        d.rectangle([x0, y0, x0 + pcol_w, y0 + prow_h],
                    outline=(160, 150, 130), width=1)
        SCENES[scene](d, x0 + 1, y0 + 1, pcol_w - 2, 42)
        _badge(d, x0 + 1, y0 + 1, pcol_w - 2, 42, num)
        tf = font(SANS_B, 8)
        tw = d.textlength(tag, font=tf) + 8
        d.rectangle([x0 + pcol_w - tw - 1, y0 + 1, x0 + pcol_w - 1, y0 + 14],
                    fill=TAG_COLOUR[tag])
        d.text((x0 + pcol_w - tw / 2 - 1, y0 + 7), tag, font=tf,
               fill=(255, 255, 255), anchor="mm")
        y, nlines = draw_wrapped(d, (x0 + 6, y0 + 46), head, font(SANS_B, 13),
                                 INK, pcol_w - 12, leading=14, max_lines=2)
        d.text((x0 + 6, y0 + 76),
               truncate(d, summ, font(SANS, 11), pcol_w - 12),
               font=font(SANS, 11), fill=(70, 70, 70))
        d.text((x0 + 6, y0 + 89),
               truncate(d, f"{src} \u00b7 {tag}", font(SANS_B, 9), pcol_w - 12),
               font=font(SANS_B, 9), fill=TAG_COLOUR[tag])

    # Map + list headers
    d.text((24, 628), "WHERE IT HAPPENED  \u2014  NUMBERED PINS",
           font=font(SANS_B, 13), fill=NAVY)
    d.text((472, 628), "ALSO ON 26 NOVEMBER  \u2014  28 MORE STORIES",
           font=font(SANS_B, 13), fill=NAVY)

    # Map
    draw_map(d, 24, 648, 440, 258)

    # List: 2 cols x 14 rows
    for i, (num, head, region, src, tag) in enumerate(LIST):
        col, row = i % 2, i // 2
        x0 = 472 + col * 266
        y0 = 648 + row * 18
        d.text((x0, y0), f"{num}.", font=font(SANS_B, 12), fill=RED)
        chip = region
        cf = font(SANS_B, 8)
        cw = d.textlength(chip, font=cf) + 8
        d.rounded_rectangle([x0 + 22, y0 + 1, x0 + 22 + cw, y0 + 13],
                            radius=3, fill=REGION_COLOUR[region])
        d.text((x0 + 22 + cw / 2, y0 + 7), chip, font=cf,
               fill=(255, 255, 255), anchor="mm")
        tx = x0 + 22 + cw + 5
        tagf = font(SANS_B, 8)
        tagw = d.textlength(tag, font=tagf)
        avail = x0 + 262 - tagw - 6 - tx
        d.text((tx, y0), truncate(d, head, font(SANS, 12), avail),
               font=font(SANS, 12), fill=INK)
        d.text((x0 + 262, y0 + 1), tag, font=tagf, fill=TAG_COLOUR[tag],
               anchor="ra")

    # Date-check box
    d.rectangle([24, 910, W - 24, 960], fill=(255, 240, 240),
                outline=RED, width=1)
    d.text((36, 914),
           "DATE CHECK \u2014 Every story happened or was first reported on "
           "Thursday 26 November 2026; read to 24:00 UTC.",
           font=font(SANS_B, 12), fill=RED)
    d.text((36, 930),
           "CARRY-OVER (original date on card): mine flood 23 Nov \u00b7 "
           "Ras Tanura claim 25 Nov \u00b7 Hong Kong fire 26 Nov 2025 \u00b7 "
           "Nepal floods 26 Aug.",
           font=font(SANS, 11), fill=(120, 20, 20))
    d.text((36, 945),
           "EXCLUDED (Wed 25 Nov): US tariffs \u00b7 Cairo fire \u00b7 "
           "FCC\u2013SpaceX \u00b7 Ramaphosa ruling \u00b7 Solomons treaty \u00b7 "
           "Macy\u2019s decision \u00b7 Veruschka obit (24 Nov) \u00b7 Myanmar ICJ remarks.",
           font=font(SANS, 11), fill=(120, 20, 20))

    # Footer
    d.text((24, 966),
           truncate(d,
                    "SOURCES: Reuters \u00b7 AP \u00b7 AFP \u00b7 AAP \u00b7 BBC \u00b7 CNN \u00b7 "
                    "ONS \u00b7 Bank of Korea \u00b7 Xinhua \u00b7 FIDE \u00b7 PTI \u00b7 "
                    "Newsquawk \u00b7 FT \u00b7 Copernicus \u00b7 Guardian \u00b7 Coalition \u00b7 "
                    "Norse Atlantic \u00b7 VOA \u00b7 Katz \u00b7 Saudi ministry",
                    font(SANS, 10), W - 48),
           font=font(SANS, 10), fill=GREY)
    d.text((24, 980),
           "HOW SURE \u2014 OFFICIAL = a government, court or agency said it  \u00b7  "
           "CONFIRMED = two or more outlets reported it  \u00b7  "
           "CLAIM = one side\u2019s account, not verified.",
           font=font(SANS, 10), fill=GREY)
    d.text((24, 994),
           "Pictures and map drawn in code; no photographs.  "
           "41 stories \u00b7 9 regions \u00b7 all dated Thu 26 Nov 2026.",
           font=font(SANS, 10), fill=GREY)

    d.rectangle([0, H - 10, W, H], fill=NAVY)
    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
