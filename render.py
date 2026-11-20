#!/usr/bin/env python3
"""Render the front page for Friday 20 November 2026 as a 1024x1024 PNG.

Layout (newspaper front page, top to bottom):
  masthead with the date -> lead story (Shenzhen summit) -> three
  secondary stories (ICJ ruling, Kyiv strikes, Riyadh missile) ->
  "The day in brief" strip -> footer.
Everything is drawn with Pillow and DejaVu fonts; no network, no
randomness, so the output is byte-deterministic.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (20, 20, 20)
RED = (176, 30, 36)
NAVY = (18, 57, 91)
TEAL = (15, 92, 96)
GOLD = (201, 148, 42)
GREY = (110, 110, 104)
DARK = (32, 38, 48)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w pixels."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    """Draw wrapped paragraph; return y just below the last line."""
    lh = leading or int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def headline(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    """Draw a wrapped headline; return y just below the last line."""
    lh = leading or int(fnt.size * 1.12)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def rule(draw, x0, y, x1, w=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)


# ---- small flat illustrations (simple geometry, no text) ----

def draw_globe_flags(d, x, y, w, h):
    """Globe with three small flags (US / China / Russia) above it."""
    import math
    cx = x + w // 2
    r = 40
    cy = y + 34 + r
    # flags on poles along the top
    fw, fh = 40, 26
    for i, fx in enumerate((x + 2, cx - fw // 2, x + w - fw - 2)):
        fy = y
        d.line([(fx + fw // 2, fy + fh), (fx + fw // 2, fy + fh + 10)],
               fill=INK, width=3)
        if i == 0:  # US: stripes + canton
            for stripe in range(4):
                d.rectangle([fx, fy + stripe * 7, fx + fw, fy + stripe * 7 + 3],
                            fill=(178, 30, 36) if stripe % 2 == 0
                            else (255, 255, 255))
            d.rectangle([fx, fy, fx + 16, fy + 13], fill=NAVY)
        elif i == 1:  # China: red field, gold stars
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
            d.ellipse([fx + 4, fy + 3, fx + 12, fy + 11], fill=GOLD)
            for sx, sy in ((24, 4), (30, 10), (30, 17), (24, 20)):
                d.ellipse([fx + sx, fy + sy, fx + sx + 4, fy + sy + 4], fill=GOLD)
        else:  # Russia: white / blue / red tricolour
            d.rectangle([fx, fy, fx + fw, fy + 8], fill=(255, 255, 255))
            d.rectangle([fx, fy + 8, fx + fw, fy + 17], fill=(0, 57, 166))
            d.rectangle([fx, fy + 17, fx + fw, fy + 26], fill=(213, 0, 50))
            d.rectangle([fx, fy, fx + fw, fy + fh], outline=INK, width=1)
    # globe
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 214, 232),
              outline=NAVY, width=4)
    for k in (-2, -1, 1, 2):
        rx = int(r * abs(k) / 3)
        d.arc([cx - rx, cy - r, cx + rx, cy + r], 90, 270, fill=NAVY, width=3)
        d.arc([cx - rx, cy - r, cx + rx, cy + r], 270, 90, fill=NAVY, width=3)
    d.line([(cx - r, cy - r // 3), (cx + r, cy - r // 3)], fill=NAVY, width=3)
    d.line([(cx - r, cy + r // 3), (cx + r, cy + r // 3)], fill=NAVY, width=3)
    d.line([(cx, cy - r), (cx, cy + r)], fill=NAVY, width=3)


def draw_court(d, x, y, w, h):
    """Courthouse pediment + columns on a navy panel."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.polygon([(x + 26, y + 40), (x + w - 26, y + 40), (x + w // 2, y + 12)],
              fill=(248, 244, 233))
    d.ellipse([x + w // 2 - 6, y + 22, x + w // 2 + 6, y + 34], fill=RED)
    for i in range(4):
        cx = x + 40 + i * ((w - 80) // 3)
        d.rectangle([cx - 5, y + 48, cx + 5, y + h - 14], fill=(248, 244, 233))
    d.rectangle([x + 20, y + h - 14, x + w - 20, y + h - 7],
                fill=(248, 244, 233))


def draw_burst(d, x, y, w, h):
    """Starburst over a dark skyline (Kyiv strikes)."""
    import math
    d.rectangle([x, y, x + w, y + h], fill=DARK)
    for bx in (x + 52, x + w // 2 + 18, x + w - 60):
        d.rectangle([bx, y + h - 40, bx + 26, y + h - 22], fill=(52, 56, 66))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(70, 74, 84))
    cx, cy = x + w // 2, y + h // 2 - 8
    pts = []
    for i in range(24):
        ang = math.pi * i / 12
        r = 44 if i % 2 == 0 else 17
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=(245, 176, 28))
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(255, 236, 170))


def draw_tower(d, x, y, w, h):
    """Riyadh tower with a strike flash on a teal panel."""
    import math
    d.rectangle([x, y, x + w, y + h], fill=TEAL)
    d.rectangle([x + w // 2 - 24, y + 24, x + w // 2 + 24, y + h], fill=(16, 42, 54))
    d.polygon([(x + w // 2 - 24, y + 24), (x + w // 2 + 24, y + 24),
               (x + w // 2, y + 8)], fill=(16, 42, 54))
    for row in range(5):
        for col in range(3):
            wx = x + w // 2 - 17 + col * 12
            wy = y + 38 + row * 14
            d.rectangle([wx, wy, wx + 6, wy + 8], fill=(255, 214, 120))
    cx, cy = x + w - 40, y + 20
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        r = 24 if i % 2 == 0 else 9
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=(255, 236, 170))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36  # margin
    rx = W - mx

    # ---------- masthead (fits inside the margins) ----------
    title = "THE WORLD IN ONE PAGE"
    size = 64
    f_mast = font(SERIF_B, size)
    while d.textlength(title, font=f_mast) > rx - mx and size > 20:
        size -= 2
        f_mast = font(SERIF_B, size)
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 22), title, font=f_mast, fill=INK)
    rule(d, mx, 96, rx, 3)
    f_date = font(SANS_B, 28)
    dateline = "FRIDAY  •  20 NOVEMBER 2026"
    dw = d.textlength(dateline, font=f_date)
    d.text(((W - dw) / 2, 106), dateline, font=f_date, fill=RED)
    f_tag = font(SANS, 21)
    tag = "The day's world news — one day, one page"
    tw2 = d.textlength(tag, font=f_tag)
    d.text(((W - tw2) / 2, 140), tag, font=f_tag, fill=GREY)
    rule(d, mx, 170, rx, 2)

    # ---------- lead story ----------
    y = 184
    f_kick = font(SANS_B, 23)
    d.text((mx, y), "SHENZHEN SUMMIT  •  19 NOV", font=f_kick, fill=RED)
    y += 36
    f_head = font(SERIF_B, 52)
    y = headline(d, mx, y, "TRUMP, XI AND PUTIN SIGN JOINT PEACE DECLARATION",
                 f_head, 880, leading=58)
    y += 10
    deck_top = y
    f_deck = font(SERIF, 25)
    para(d, mx, deck_top,
         "First-ever three-way summit ends with a four-point pact on "
         "nuclear risk, UN reform and energy — but no deal on Ukraine "
         "or Iran.",
         f_deck, 640, leading=32)
    draw_globe_flags(d, rx - 250, deck_top - 6, 250, 150)
    y = deck_top + 116
    rule(d, mx, y, rx, 2)

    # ---------- three secondary stories ----------
    y += 16
    cols = [
        ("THE HAGUE",
         "COURT: MYANMAR COMMITTED GENOCIDE",
         "The world court finds Myanmar responsible for genocide "
         "against the Rohingya. Decided 9–6.",
         draw_court),
        ("KYIV  •  20 NOV",
         "OVERNIGHT STRIKES KILL 8 IN KYIV",
         "Russian attacks target bridges in the capital; 28 hurt across "
         "nine regions, the mayor says.",
         draw_burst),
        ("RIYADH  •  20 NOV",
         "HOUTHI MISSILE DAMAGES RIYADH TOWER",
         "A strike hits the Saudi wealth fund tower in the financial "
         "district; more missiles intercepted.",
         draw_tower),
    ]
    col_w = (W - 2 * mx - 2 * 24) // 3
    f_ck = font(SANS_B, 19)
    f_ch = font(SANS_B, 27)
    f_cs = font(SANS, 20)
    sec_top = y
    for i, (kick, head, summ, art) in enumerate(cols):
        cx = mx + i * (col_w + 24)
        art(d, cx, y, col_w, 100)
        yy = y + 110
        d.text((cx, yy), kick, font=f_ck, fill=RED)
        yy += 28
        yy = headline(d, cx, yy, head, f_ch, col_w, leading=30)
        yy += 6
        para(d, cx, yy, summ, f_cs, col_w, leading=25)
    y = sec_top + 336
    rule(d, mx, y, rx, 2)

    # ---------- the day in brief ----------
    y += 14
    f_bh = font(SANS_B, 23)
    d.text((mx, y), "THE DAY IN BRIEF", font=f_bh, fill=INK)
    y += 34
    f_bl = font(SANS_B, 19)
    f_bt = font(SANS, 19)
    briefs = [
        ("POLAND — ", "Russian missiles and a drone violated Polish "
         "airspace overnight."),
        ("COP31 — ", "Draft deal in Antalya drops any call to phase out "
         "fossil fuels."),
        ("WASHINGTON — ", "Senate Republicans block a measure to end the "
         "US war in Iran, 51–48."),
        ("MARKETS — ", "Stocks fall a fifth straight day; Nikkei drops 4.8% "
         "as AI shares slide."),
        ("KENYA — ", "Last Ebola patient discharged, 37 days after the "
         "first case."),
    ]
    for lead, text in briefs:
        d.text((mx + 16, y), "■", font=f_bl, fill=RED)
        d.text((mx + 40, y), lead, font=f_bl, fill=INK)
        lw = d.textlength(lead, font=f_bl)
        para(d, mx + 40 + lw, y, text, f_bt, rx - (mx + 40 + lw), leading=24)
        y += 24

    # ---------- footer ----------
    rule(d, mx, 992, rx, 1, fill=GREY)
    f_ft = font(SANS, 15)
    foot = "Drawn from the day's briefings: Reuters • Just Security • One Turn • The Times"
    fw = d.textlength(foot, font=f_ft)
    d.text(((W - fw) / 2, 1000), foot, font=f_ft, fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size, "briefs end y =", y)


if __name__ == "__main__":
    main()
