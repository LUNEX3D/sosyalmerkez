"""Ortak çizim yardımcıları (dashtock-stok/kaynak/render_stok.py içinden alındı)."""
import sys, os, math, json, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter


HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "rutin") + "/"
PANEL = "/mnt/project-files/dashtock-panel/"
W, H, FPS = 1080, 1920, 30
OFF = 0.1
DUR = 20.7

NAVY = (7, 10, 24); CARD = (20, 26, 42); CARD2 = (27, 34, 54); WHITE = (244, 247, 255); GREY = (150, 160, 188); DIM = (96, 104, 136)
INDIGO = (112, 88, 240); TEAL = (45, 212, 191); AMBER = (255, 184, 64); GOLD = (255, 200, 70); PURPLE = (150, 90, 245)
GREEN = (72, 214, 130); CORAL = (245, 110, 90); BLUE = (80, 150, 255); PINK = (230, 95, 170); RED = (240, 70, 70)
FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def font(n, s):
    if (n, s) not in _fc: _fc[(n, s)] = ImageFont.truetype(FD + n, s)
    return _fc[(n, s)]
DB, DS, IB, IS, IM = "InterDisplay-Bold.otf", "InterDisplay-SemiBold.otf", "Inter-Bold.otf", "Inter-SemiBold.otf", "Inter-Medium.otf"
DX = "InterDisplay-Black.otf"

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def back_out(x, c=1.7): x = clamp(x); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def mixc(a, b, t): return tuple(int(lerp(x, y, clamp(t))) for x, y in zip(a, b))
def env(t, a, b, fi=0.3, fo=0.3): return clamp((t - a) / fi) * clamp((b - t) / fo)
def tl(v):
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + "₺" + s

_tc = {}
def tc(key, fn):
    if key not in _tc: _tc[key] = fn()
    return _tc[key]
def text_img(s, f, fill=WHITE):
    def mk():
        b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), s, font=f)
        im = Image.new("RGBA", (max(b[2], 1) + 10, int(f.size * 1.3)), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((4, 0), s, font=f, fill=fill)
        return im
    return tc(("t", s, f.path, f.size, fill), mk)
def tlen(s, f): return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(s, font=f)
def fade(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im
def place(c, im, x, y, a=1.0, anchor="c", scale=1.0):
    if a <= 0.01: return
    if abs(scale - 1) > 0.003:
        im = im.resize((max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))), Image.BILINEAR)
    im = fade(im, a)
    if anchor == "c": x, y = x - im.size[0] / 2, y - im.size[1] / 2
    elif anchor == "l": y = y - im.size[1] / 2
    elif anchor == "r": x, y = x - im.size[0], y - im.size[1] / 2
    c.alpha_composite(im, (int(x), int(y)))
def pill(text, f, fg, bg, padx=24, pady=8, outline=None):
    def mk():
        t = text_img(text, f, fg)
        p = Image.new("RGBA", (t.size[0] + padx * 2, t.size[1] + pady * 2), (0, 0, 0, 0))
        ImageDraw.Draw(p).rounded_rectangle((0, 0, p.size[0] - 1, p.size[1] - 1), p.size[1] // 2, fill=bg, outline=outline, width=2 if outline else 0)
        p.alpha_composite(t, (padx, pady)); return p
    return tc(("pill", text, f.path, f.size, fg, bg, padx, pady, outline), mk)
def glow_rect(w, h, col, r=26, blur=22, a=170, width=8):
    def mk():
        pd = blur * 3
        g = Image.new("RGBA", (w + pd * 2, h + pd * 2), col + (0,))
        ImageDraw.Draw(g).rounded_rectangle((pd, pd, pd + w, pd + h), r, outline=col + (a,), width=width)
        return g.filter(ImageFilter.GaussianBlur(blur)), pd
    return tc(("glow", w, h, col, r, blur, a, width), mk)
def card(w, h, border=None, fill=CARD, r=26, bw=3):
    def mk():
        sh = 26
        im = Image.new("RGBA", (w + sh * 2, h + sh * 2), (0, 0, 0, 0))
        s = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(s).rounded_rectangle((sh, sh + 10, sh + w, sh + h + 10), r, fill=(0, 0, 0, 150))
        im.alpha_composite(s.filter(ImageFilter.GaussianBlur(14)))
        ImageDraw.Draw(im).rounded_rectangle((sh, sh, sh + w, sh + h), r, fill=fill + (245,), outline=(border + (230,)) if border else (255, 255, 255, 26), width=bw)
        return im
    return tc(("card", w, h, border, fill, r, bw), mk)
def put_card(c, x, y, w, h, border=None, a=1.0, fill=CARD, glow=0.0, r=26):
    """x,y: sol üst köşe"""
    if a <= 0.01: return
    if glow > 0.01 and border:
        g, pd = glow_rect(w, h, border, r)
        place(c, g, x - pd, y - pd, a * glow, "tl")
    place(c, card(w, h, border, fill, r), x - 26, y - 26, a, "tl")

# ------------- ikonlar -------------
def crown(size, col):
    def mk():
        s = 4; S = size * s
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = [(0.08, 0.78), (0.08, 0.30), (0.30, 0.52), (0.50, 0.16), (0.70, 0.52), (0.92, 0.30), (0.92, 0.78)]
        d.polygon([(x * S, y * S) for x, y in pts], fill=col)
        d.rounded_rectangle((0.06 * S, 0.80 * S, 0.94 * S, 0.94 * S), int(0.03 * S), fill=col)
        hi = tuple(min(255, v + 50) for v in col)
        for x, y in [(0.08, 0.27), (0.50, 0.12), (0.92, 0.27)]:
            r = 0.065 * S; d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=hi)
        for x in (0.30, 0.50, 0.70):
            r = 0.045 * S; d.ellipse((x * S - r, 0.66 * S - r, x * S + r, 0.66 * S + r), fill=(255, 255, 255, 120))
        return im.resize((size, size), Image.LANCZOS)
    return tc(("crown", size, col), mk)
def icon_circle(kind, size, col, fg=WHITE):
    def mk():
        s = 4; S = size * s
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((0, 0, S - 1, S - 1), fill=col + (255,))
        w = int(S * 0.07)
        if kind == "search":
            d.ellipse((S * .28, S * .26, S * .6, S * .58), outline=fg, width=w); d.line((S * .56, S * .55, S * .74, S * .73), fill=fg, width=w)
        elif kind == "bell":
            d.pieslice((S * .28, S * .24, S * .72, S * .72), 180, 360, fill=fg); d.rectangle((S * .28, S * .48, S * .72, S * .66), fill=fg)
            d.rounded_rectangle((S * .22, S * .64, S * .78, S * .70), 4, fill=fg); d.ellipse((S * .44, S * .70, S * .56, S * .80), fill=fg)
        elif kind == "shield":
            d.polygon([(S * .5, S * .2), (S * .76, S * .3), (S * .72, S * .58), (S * .5, S * .8), (S * .28, S * .58), (S * .24, S * .3)], fill=fg)
            d.line([(S * .38, S * .5), (S * .47, S * .59), (S * .63, S * .41)], fill=col, width=w)
        elif kind == "warn":
            d.polygon([(S * .5, S * .2), (S * .8, S * .76), (S * .2, S * .76)], fill=fg)
            d.rectangle((S * .47, S * .38, S * .53, S * .6), fill=col); d.ellipse((S * .465, S * .64, S * .535, S * .71), fill=col)
        elif kind == "check":
            d.line([(S * .3, S * .52), (S * .44, S * .66), (S * .72, S * .36)], fill=fg, width=int(S * .1), joint="curve")
        elif kind == "box":
            d.polygon([(S * .5, S * .22), (S * .78, S * .36), (S * .5, S * .5), (S * .22, S * .36)], fill=fg)
            d.polygon([(S * .22, S * .4), (S * .48, S * .54), (S * .48, S * .82), (S * .22, S * .68)], fill=tuple(int(v * .8) for v in fg))
            d.polygon([(S * .78, S * .4), (S * .52, S * .54), (S * .52, S * .82), (S * .78, S * .68)], fill=tuple(int(v * .65) for v in fg))
        elif kind == "mail":
            d.rounded_rectangle((S * .24, S * .32, S * .76, S * .68), 6, outline=fg, width=w); d.line([(S * .26, S * .35), (S * .5, S * .53), (S * .74, S * .35)], fill=fg, width=w)
        return im.resize((size, size), Image.LANCZOS)
    return tc(("ic", kind, size, col, fg), mk)
def cursor_img():
    def mk():
        s = 3; im = Image.new("RGBA", (44 * s, 60 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = [(4, 2), (4, 44), (15, 33), (23, 52), (31, 48), (23, 30), (38, 30)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=(255, 255, 255))
        d.line([(x * s, y * s) for x, y in pts + [pts[0]]], fill=(15, 15, 25), width=2 * s)
        return im.resize((48, 66), Image.LANCZOS)
    return tc("cursor", mk)
def draw_cursor(c, x, y, a, tclick, col=WHITE):
    if a <= 0.01: return
    d = ImageDraw.Draw(c)
    if 0 <= tclick <= 1:
        rr = 12 + 60 * tclick
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=col + (int(255 * (1 - tclick) * a),), width=5)
    ci = cursor_img(); cs = 1 - 0.15 * math.sin(math.pi * clamp(tclick))
    place(c, ci, x - 5, y - 3, a, "tl", cs)

MARK = Image.open(HERE + "logo_mark.png").convert("RGBA")
def mark(h): return tc(("mark", h), lambda: MARK.resize((h, h), Image.LANCZOS))
def logo(h):
    def mk():
        m = mark(h); t = text_img("Dashtock", font(DB, int(h * 0.8)), WHITE)
        out = Image.new("RGBA", (h + int(h * 0.24) + t.size[0], max(h, t.size[1])), (0, 0, 0, 0))
        out.alpha_composite(m, (0, (out.size[1] - h) // 2)); out.alpha_composite(t, (h + int(h * 0.24), (out.size[1] - t.size[1]) // 2 - int(h * 0.04)))
        return out
    return tc(("logo", h), mk)

# ------------- arka plan -------------
def make_bg():
    bg = Image.new("RGB", (W, H), NAVY)
    g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
    for i in range(40):
        r = int(H * (1 - i / 40)); d.ellipse((W / 2 - r, -r * 0.5, W / 2 + r, r * 0.8), fill=int(4 * i))
    bg.paste(Image.new("RGB", (W, H), (18, 22, 52)), (0, 0), g.filter(ImageFilter.GaussianBlur(90)))
    d2 = ImageDraw.Draw(bg)
    for x in range(0, W, 60): d2.line((x, 0, x, H), fill=(13, 17, 38))
    for y in range(0, H, 60): d2.line((0, y, W, y), fill=(13, 17, 38))
    return bg.convert("RGBA")
BG = make_bg()
def blob(col, r=420):
    def mk():
        pd = r // 2
        b = Image.new("RGBA", (r * 2 + pd * 2, r * 2 + pd * 2), col + (0,))
        ImageDraw.Draw(b).ellipse((pd, pd, pd + r * 2 - 1, pd + r * 2 - 1), fill=col + (75,))
        return b.filter(ImageFilter.GaussianBlur(r // 3)), r + pd
    return tc(("blob", col, r), mk)
random.seed(5)
DUST = [(random.uniform(0, W), random.uniform(0, H), random.uniform(0.3, 1.0), random.uniform(0, 6.28)) for _ in range(60)]

MARK = Image.open(HERE + "logo_mark.png").convert("RGBA")
def mark(h): return tc(("mark", h), lambda: MARK.resize((h, h), Image.LANCZOS))
def logo(h, col=WHITE):
    def mk():
        m = mark(h); t = text_img("Dashtock", font(DB, int(h * 0.8)), col)
        out = Image.new("RGBA", (h + int(h * 0.24) + t.size[0], max(h, t.size[1])), (0, 0, 0, 0))
        out.alpha_composite(m, (0, (out.size[1] - h) // 2)); out.alpha_composite(t, (h + int(h * 0.24), (out.size[1] - t.size[1]) // 2 - int(h * 0.04)))
        return out
    return tc(("logo", h, col), mk)



EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
def emoji(ch, size):
    def mk():
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), ch, font=EMO, embedded_color=True)
        im = im.crop(im.getbbox())
        return im.resize((size, int(size * im.size[1] / im.size[0])), Image.LANCZOS)
    return tc(("emo", ch, size), mk)

def native_text(s, size, fill=WHITE):
    """Reels/TikTok tarzı yazı: kalın, siyah konturlu."""
    def mk():
        f = font(DX, size); b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), s, font=f, stroke_width=max(4, size // 9))
        im = Image.new("RGBA", (b[2] - b[0] + 20, b[3] - b[1] + 20), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10 - b[0], 10 - b[1]), s, font=f, fill=fill, stroke_width=max(4, size // 9), stroke_fill=(0, 0, 0))
        return im
    return tc(("nt", s, size, fill), mk)
def caption(c, t, lines, y, a, s0=None, emo=None, size=78):
    """lines: [(metin, renk)], emo: satır sonuna emoji"""
    if a <= 0.01: return
    sc = back_out((t - s0) / 0.3) if s0 is not None else 1
    lh = int(size * 1.25)
    for i, (s, col) in enumerate(lines):
        im = native_text(s, size, col)
        if emo and i == len(lines) - 1:
            e = emoji(emo, int(size * 1.05)); comb = Image.new("RGBA", (im.size[0] + e.size[0] + 10, max(im.size[1], e.size[1])), (0, 0, 0, 0))
            comb.alpha_composite(im, (0, (comb.size[1] - im.size[1]) // 2)); comb.alpha_composite(e, (im.size[0] + 10, (comb.size[1] - e.size[1]) // 2)); im = comb
        place(c, im, W / 2, y + i * lh, a, "c", sc)

def tl2(v): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
def rich(parts, size, col=WHITE):
    def mk():
        ims = []
        for q in parts:
            if isinstance(q, tuple) and q[0] == "emo": ims.append(emoji(q[1], int(size * 1.0)))
            else:
                s_, c_ = (q, col) if isinstance(q, str) else q
                ims.append(native_text(s_, size, c_))
        w = sum(i.size[0] for i in ims) + 8 * (len(ims) - 1); h = max(i.size[1] for i in ims)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); x = 0
        for i in ims: out.alpha_composite(i, (x, (h - i.size[1]) // 2)); x += i.size[0] + 8
        return out
    return tc(("rich", repr(parts), size, col), mk)

def letter_badge(ch, col, size=88):
    def mk():
        s = 4; S = size * s; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, S - 1, S - 1), S // 4, fill=col + (255,))
        f = font(DX, int(S * 0.55)); b = d.textbbox((0, 0), ch, font=f)
        d.text(((S - (b[2] - b[0])) / 2 - b[0], (S - (b[3] - b[1])) / 2 - b[1]), ch, font=f, fill=WHITE)
        return im.resize((size, size), Image.LANCZOS)
    return tc(("lb", ch, col, size), mk)

