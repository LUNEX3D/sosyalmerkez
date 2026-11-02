"""Dashtock "Stokta 1 tane vardı. 2 kişi aldı.": ~19,7 sn dikey kısa, Onur Büyü seslendirmeli (1080x1920), konu: merkezi stok havuzu / overselling.
Tek ürün, aynı saniyede Trendyol + Hepsiburada siparişi, STOK −1 -> "Hangisine gönderirsin?" A/B + geri sayım -> "Fark etmez." iptal, müşteri mağdur,
mağaza puanı düşer -> geri sar "Aynı an. Bu sefer Dashtock'la." -> merkezi stok, 8 pazaryeri, biri satınca hepsinde 0 · Tükendi
-> "Biri satınca, hepsinde biter." -> Dashtock -> döngü. Sessiz izlemeye göre.
Kullanım: python3 render_stok.py <çıktı.mp4> [a0 a1] | kare <sn> <png> | meta
"""
import sys, math, json, random, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter


HERE = "/mnt/project-files/dashtock-stok/kaynak/"
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


# ------------- zaman çizelgesi -------------
VO_OFF = 0.15                       # seslendirme başlangıcı (vo_stok.mp3, kelime zamanları vo_words.json)
T_L2 = 1.7; T_N1 = 1.8; T_NEG = 2.9
T_Q = 3.4; T_FE = 4.85; T_CAS = 5.8
T_RW = 8.25; T_DASHLA = 9.8; T_HUB = 10.8; T_SALE = 11.3; T_ZERO = 12.0; T_WAVE = 12.1; T_OK = 14.1
T_S6 = 15.0; T_S6B = 16.05; T_END = 17.2; T_LOOP = 20.45
CD0, CDS = 0.3, 0.4                 # geri sayım başlangıcı ve adımı

MP = [("Trendyol", (242, 122, 32)), ("Hepsiburada", (255, 96, 40)), ("N11", (150, 90, 245)), ("Amazon", (255, 170, 30)),
      ("ÇiçekSepeti", (80, 150, 255)), ("Pazarama", (45, 200, 180)), ("Ozon", (40, 110, 255)), ("AliExpress", (235, 60, 60))]

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

def notif(name, col):
    def mk():
        w, h = 920, 150
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(244, 246, 252, 250))
        im.alpha_composite(letter_badge(name[0], col, 92), (28, 29))
        d.text((146, 26), name, font=font(DB, 40), fill=(20, 22, 34))
        d.text((146, 80), "Yeni sipariş · Kablosuz kulaklık · 1 adet", font=font(IM, 32), fill=(90, 96, 120))
        d.text((w - 150, 30), "14:32:07", font=font(DB, 30), fill=(120, 126, 150))
        return im
    return tc(("notif", name), mk)

def stock_pill(txt, col, glow=0.0):
    return pill(txt, font(DX, 64), WHITE, col + (255,), 40, 14)

# ------------- sahne 1: çakışma -------------
def s1(c, t):
    a = 1 - clamp((t - T_Q) / 0.12)
    if a <= 0.01: return
    caption(c, t, [("Stokta 1 tane vardı.", WHITE)], 250, a, 0.0, size=104)
    if t >= T_L2: caption(c, t, [("2 kişi aynı anda aldı.", CORAL)], 385, a, T_L2, size=96)
    # ürün kartı
    sh = (math.sin(t * 60) * 10 * math.exp(-(t - T_NEG) * 6)) if t >= T_NEG else 0
    put_card(c, 190 + sh, 520, 700, 560, (90, 110, 170), a, CARD, 0.0, 40)
    place(c, emoji("🎧", 230), W / 2 + sh, 700, a, "c", 1 + 0.03 * math.sin(t * 3))
    place(c, text_img("Kablosuz kulaklık", font(DB, 50)), W / 2 + sh, 870, a, "c")
    neg = t >= T_NEG
    sp = stock_pill("STOK: −1" if neg else "STOK: 1", RED if neg else GREEN)
    place(c, sp, W / 2 + sh, 985, a, "c", lerp(1.4, 1, ease_out((t - T_NEG) / 0.2)) if neg else 1)
    if neg:
        g, pd = glow_rect(sp.size[0], sp.size[1], RED, sp.size[1] // 2, 20, int(200 * (0.6 + 0.4 * math.sin(t * 12))))
        place(c, g, W / 2 - sp.size[0] / 2 - pd + sh, 985 - sp.size[1] / 2 - pd, a, "tl")
    # bildirimler: soldan ve sağdan aynı anda
    for i, (nm, col) in enumerate(MP[:2]):
        u = ease_out((t - T_N1) / 0.32)
        if u <= 0: continue
        x0 = -1000 if i == 0 else W + 80
        x = lerp(x0, 80, u); y = 1170 + i * 185
        place(c, notif(nm, col), x, y, a, "tl")
    if t >= T_NEG:
        place(c, native_text("Aynı saniye. Tek ürün.", 58, AMBER), W / 2, 1580, a * clamp((t - T_NEG - 0.1) / 0.2), "c")

# ------------- sahne 2: hangisine? -------------
def s2(c, t):
    a = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_FE) / 0.08))
    if a <= 0.01: return
    place(c, rich([("Hangisine", WHITE)], 120), W / 2, 420, a, "c", back_out((t - T_Q) / 0.3))
    place(c, rich([("gönderirsin?", AMBER), ("emo", "🤔")], 120), W / 2, 560, a, "c", back_out((t - T_Q - 0.08) / 0.3))
    for i, (nm, col) in enumerate(MP[:2]):
        y = 820 + i * 230; ia = clamp((t - T_Q - 0.3 - i * 0.12) / 0.15) * a
        put_card(c, 110, y, 860, 180, col, ia, CARD2, 0.35, 36)
        place(c, letter_badge("AB"[i], col, 110), 160, y + 90, ia, "l")
        place(c, text_img(nm, font(DX, 66)), 310, y + 90, ia, "l")
    # geri sayım
    cd = 3 - int(clamp((t - T_Q - CD0) / CDS, 0, 2.99))
    if t > T_Q + CD0:
        u = ((t - T_Q - CD0) % CDS) / CDS
        place(c, native_text(str(cd), 170, WHITE), W / 2, 1410, a, "c", lerp(1.4, 1, ease_out(u * 3)))
    place(c, text_img("Yoruma yaz: A mı, B mi? 👇".replace(" 👇", ""), font(DB, 44), (200, 206, 228)), W / 2, 1590, a, "c")

# ------------- sahne 3: fark etmez -------------
def s3(c, t):
    a = clamp((t - T_FE) / 0.06) * (1 - clamp((t - T_RW) / 0.1))
    if a <= 0.01: return
    if t < T_CAS:
        place(c, native_text("Fark etmez.", 170, CORAL), W / 2, 900, a, "c", lerp(1.8, 1, ease_out((t - T_FE) / 0.16)))
        return
    ca = clamp((t - T_CAS) / 0.1) * a
    caption(c, t, [("Biri iptal olacak.", WHITE)], 300, ca, T_CAS, size=100)
    place(c, notif("Hepsiburada", MP[1][1]), 80, 520, ca, "tl")
    # İPTAL damgası
    su = clamp((t - T_CAS - 0.15) / 0.12)
    if su > 0:
        st = tc("stamp", lambda: native_text("İPTAL", 120, RED))
        r_ = st.rotate(-12, expand=True, resample=Image.BICUBIC)
        place(c, r_, W / 2 + 140, 590, ca * su, "c", lerp(2.2, 1, ease_out(su)))
    rows = [("❌", "Sipariş iptal"), ("😠", "Müşteri mağdur"), ("📉", "Mağaza puanın düşer")]
    for i, (e, s_) in enumerate(rows):
        ti = T_CAS + 0.35 + i * 0.28; ra = clamp((t - ti) / 0.12) * a
        if ra <= 0.01: continue
        y = 900 + i * 190; dx = 80 * (1 - ease_out((t - ti) / 0.2))
        put_card(c, 110 + dx, y, 860, 150, (240, 90, 90) if i == 2 else (70, 80, 120), ra, CARD, 0.3 if i == 2 else 0, 32)
        place(c, emoji(e, 80), 190 + dx, y + 75, ra, "c")
        place(c, text_img(s_, font(DX, 58), CORAL if i == 2 else WHITE), 270 + dx, y + 75, ra, "l")

# ------------- sahne 4: geri sar -------------
def s4(c, t):
    a = clamp((t - T_RW) / 0.05) * (1 - clamp((t - T_HUB) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (8, 10, 30, int(200 * a))))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for k in range(14):
        yy = (k * 157 + (t - T_RW) * 2600) % H
        d.rectangle((0, yy, W, yy + 5), fill=(255, 255, 255, int(40 * a)))
    c.alpha_composite(ov)
    place(c, native_text("⏪".replace("⏪", "<<"), 200, WHITE), W / 2, 760, a, "c", 1 + 0.08 * math.sin(t * 30))
    place(c, native_text("Aynı an.", 120, WHITE), W / 2, 980, a, "c")
    place(c, native_text("Bu sefer Dashtock'la.", 92, TEAL), W / 2, 1120, a * clamp((t - T_DASHLA) / 0.12), "c", lerp(1.3, 1, ease_out((t - T_DASHLA) / 0.2)))

# ------------- sahne 5: merkezi stok -------------
CX, CY, RX, RY = W / 2, 1080, 330, 450
_m = dict(MP)
RING = [(n, _m[n]) for n in ("Trendyol", "Hepsiburada", "Amazon", "ÇiçekSepeti", "N11", "Ozon", "Pazarama", "AliExpress")] + [("Web siten", GOLD)]   # kendi web mağazası da aynı stok havuzundan beslenir
NR = len(RING)
POS = [(CX + RX * math.cos(-math.pi / 2 + k * 2 * math.pi / NR), CY + RY * math.sin(-math.pi / 2 + k * 2 * math.pi / NR)) for k in range(NR)]
def zero_t(k):  # Trendyol (0) satar; dalga diğerlerine yayılır
    return T_ZERO if k == 0 else T_WAVE + 0.09 * k
def s5(c, t):
    a = clamp((t - T_HUB) / 0.12) * (1 - clamp((t - T_S6) / 0.1))
    if a <= 0.01: return
    if t < T_OK:
        caption(c, t, [("Tek stok havuzu:", WHITE), ("web siten + 8 pazaryeri.", TEAL)], 250, a, T_HUB, size=84)
    else:
        caption(c, t, [("Hepsinde \"Tükendi\".", WHITE), ("İptal yok.", GREEN)], 250, a, T_OK, emo="✅", size=96)
    d = ImageDraw.Draw(c)
    for k, (x, y) in enumerate(POS):
        la = clamp((t - T_HUB - 0.05 * k) / 0.2) * a
        col = RED if t >= zero_t(k) else (80, 90, 130)
        d.line((CX, CY, x, y), fill=col + (int(200 * la),), width=5)
        # akan nabız
        if k == 0 and T_SALE <= t < T_ZERO:
            u = (t - T_SALE) / (T_ZERO - T_SALE); px, py = lerp(x, CX, u), lerp(y, CY, u)
            d.ellipse((px - 18, py - 18, px + 18, py + 18), fill=AMBER + (255,))
        if k > 0 and T_WAVE <= t < zero_t(k) + 0.05:
            u = clamp((t - T_WAVE) / (zero_t(k) - T_WAVE + 0.001)); px, py = lerp(CX, x, u), lerp(CY, y, u)
            d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=RED + (int(255 * la),))
    # merkez
    z = t >= T_ZERO
    hub = tc(("hub", z), lambda: None) or None
    r = 150; pulse = 1 + 0.15 * math.exp(-(t - T_ZERO) * 6) * z
    d.ellipse((CX - r * pulse, CY - r * pulse, CX + r * pulse, CY + r * pulse), fill=(20, 26, 46, int(255 * a)), outline=(RED if z else TEAL) + (int(255 * a),), width=8)
    place(c, text_img("Merkezi stok", font(DB, 34), GREY), CX, CY - 70, a, "c")
    place(c, native_text("0" if z else "1", 140, RED if z else WHITE), CX, CY + 20, a, "c", pulse)
    for k, (x, y) in enumerate(POS):
        la = clamp((t - T_HUB - 0.05 * k) / 0.2) * a
        nm, col = RING[k]; zz = t >= zero_t(k)
        p_ = pill(nm, font(DX, 42), (30, 22, 4) if nm == "Web siten" else WHITE, col + (255,), 24, 10)
        sc = 1 + (0.25 * math.exp(-(t - zero_t(k)) * 8) if zz else 0) + (0.2 * math.sin(math.pi * clamp((t - T_SALE) / 0.3)) if k == 0 and t < T_ZERO else 0)
        place(c, p_, x, y, la, "c", sc)
        bt = "0 · Tükendi" if zz else "Stok 1"
        place(c, pill(bt, font(IB, 30), WHITE, (RED if zz else (40, 48, 76)) + (255,), 14, 4), x, y + 60, la, "c")
        if k == 0 and t >= T_SALE:
            place(c, pill("Satıldı!", font(DX, 32), (30, 22, 4), AMBER + (255,), 16, 6), x, y - 58, la * clamp((t - T_SALE) / 0.1), "c")

# ------------- sahne 6: slogan -------------
def s6(c, t):
    a = clamp((t - T_S6) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(238 * a))))
    for i, (w_, col, ti) in enumerate((("Biri satınca,", WHITE, T_S6), ("hepsinde biter.", TEAL, T_S6B))):
        wa = clamp((t - ti) / 0.1) * a
        place(c, native_text(w_, 140, col), W / 2, 840 + i * 180, wa, "c", lerp(1.5, 1, ease_out((t - ti) / 0.18)))

PACKS = [("Pazaryeri Pro", "8 pazaryeri: stok, sipariş, e-fatura, kargo", (242, 122, 32)),
         ("Web + Mağaza", "Kendi web siten: tema, domain, online ödeme", GOLD),
         ("Full", "Web siten + pazaryerlerin, tek panelde", TEAL)]
def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(242 * a))))
    place(c, logo(120), W / 2, 430, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, native_text("Sana uyan paketi seç.", 82, WHITE), W / 2, 590, la, "c")
    for i, (nm, sub, col) in enumerate(PACKS):
        ia = clamp((t - T_END - 0.45 - i * 0.18) / 0.18) * a; dx = 90 * (1 - ease_out((t - T_END - 0.45 - i * 0.18) / 0.25))
        y = 700 + i * 200
        put_card(c, 90 + dx, y, 900, 170, col, ia, CARD, 0.35, 34)
        place(c, letter_badge(str(i + 1), col, 96), 130 + dx, y + 85, ia, "l")
        place(c, text_img(nm, font(DX, 56)), 260 + dx, y + 58, ia, "l")
        place(c, text_img(sub, font(DS, 34), (205, 210, 232)), 260 + dx, y + 118, ia, "l")
    fa = clamp((t - T_END - 1.1) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1360, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 76), GOLD), W / 2, 1470, fa, "c")

FLASH = (T_NEG, T_Q, T_FE, T_CAS, T_HUB, T_ZERO, T_S6, T_END)
def frame(t):
    c = BG.copy().convert("RGBA")
    s1(c, t); s2(c, t); s3(c, t); s5(c, t); s4(c, t); s6(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.15))))
    out = c.convert("RGB")
    sh = 0
    for x in (T_NEG, T_FE, T_CAS + 0.15, T_ZERO, T_S6, T_S6B):
        if 0 <= t - x < 0.25: sh += 11 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.0), clamp((t - T_LOOP) / 0.25))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, l2=T_L2, n1=T_N1, neg=T_NEG, q=T_Q, fe=T_FE, cas=T_CAS, rw=T_RW, hub=T_HUB, sale=T_SALE, zero=T_ZERO,
                              wave=[zero_t(k) for k in range(NR)], ok=T_OK, s6b=T_S6B, vo_off=VO_OFF, cd0=CD0, cds=CDS, dashla=T_DASHLA, s6=T_S6, end=T_END, loop=T_LOOP)))
        sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    a0 = float(sys.argv[2]) if len(sys.argv) > 3 else 0.0
    a1 = float(sys.argv[3]) if len(sys.argv) > 3 else DUR
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(a0 * FPS)), int(round(a1 * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
