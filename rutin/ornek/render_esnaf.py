"""Dashtock "Bu site kaç satır kodla yapıldı?": ~22 sn dikey kısa, Onur Büyü seslendirmeli (1080x1920).
Konu: Web + Mağaza paketi, sürükle-bırak site editörü, temalar (Zephra, Lumen, Esnaf3D), Esnaf3D temasının anında 3D baskı fiyat teklifi,
web siparişine otomatik fatura + kargo etiketi.
Akış: telefonda Esnaf3D mağazası + "kaç satır kod?" A/B/C -> "Sıfır." -> editörde blok sürükle-bırak + tema değiştir
-> müşteri dosya yükler, anında fiyat (ÖRNEK), öder -> panelde sipariş, fatura, kargo etiketi -> "Siteni kodlama. Sürükle." -> paketler.
Kullanım: python3 render_esnaf.py <çıktı.mp4> [a0 a1] | kare <sn> <png> | meta
"""
import sys, math, json, subprocess
sys.path.insert(0, "/mnt/project-files/dashtock-esnaf3d/kaynak/")
from yardimci import *

DUR = 22.0
VO_OFF = 0.2
def V(x): return x + VO_OFF          # seslendirme kelime zamanı -> video zamanı (vo_a.mp3)

T_A, T_B, T_C = V(2.24), V(3.28), V(4.40)
T_ZERO = V(5.52)
T_ED = V(6.40); T_DRAG = V(6.48); T_DROP = V(7.25); T_TEMA = V(7.76)
T_TH = (V(7.95), V(8.25), V(8.55))
T_UP = V(8.77); T_FILE = V(9.2); T_PRICE = V(10.32); T_PAY = V(11.92)
T_PANEL = V(12.55); T_R = (V(12.64), V(13.36), V(13.92)); T_READY = V(15.12)
T_S1 = V(15.92); T_S2 = V(17.12); T_END = V(17.92); T_LOOP = 21.7

# ------------- temalar -------------
THEMES = {
    "Esnaf3D": dict(bg=(255, 255, 255), soft=(255, 238, 226), ink=(24, 24, 32), sub=(105, 108, 124), acc=(255, 106, 26), card=(246, 246, 249), serif=False),
    "Zephra": dict(bg=(16, 18, 26), soft=(30, 36, 52), ink=(240, 244, 255), sub=(150, 160, 186), acc=(40, 220, 230), card=(28, 32, 46), serif=False),
    "Lumen": dict(bg=(250, 245, 238), soft=(240, 226, 236), ink=(52, 36, 48), sub=(130, 112, 124), acc=(200, 80, 140), card=(244, 236, 230), serif=True),
}
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
def hfont(th, s): return ImageFont.truetype(SERIF, int(s * 0.9)) if th["serif"] else font(DX, s)

def vase_r(u):                                   # u: 0 (alt) .. 1 (üst)
    return 0.55 + 0.32 * math.sin(math.pi * (u * 1.15 + 0.05)) - 0.18 * u
def vase(w, h, col, ang=0.0, line=None, bg=None):
    """Katman çizgili (3D baskı gibi) vazo."""
    s = 2; W_, H_ = w * s, h * s
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = W_ / 2; R = W_ * 0.42; n = 26
    pts_l, pts_r = [], []
    for k in range(n + 1):
        u = k / n; y = H_ * 0.94 - u * H_ * 0.86; r = R * vase_r(u)
        pts_l.append((cx - r, y)); pts_r.append((cx + r, y))
    d.polygon(pts_l + pts_r[::-1], fill=col + (255,))
    dark = tuple(int(v * 0.78) for v in col); lite = tuple(min(255, int(v * 1.12) + 12) for v in col)
    for k in range(n + 1):                       # katman çizgileri
        u = k / n; y = H_ * 0.94 - u * H_ * 0.86; r = R * vase_r(u)
        d.arc((cx - r, y - r * 0.18, cx + r, y + r * 0.18), 0, 180, fill=dark + (255,), width=s * 2)
    for j in range(5):                           # dönen meridyenler
        a = ang + j * math.pi / 5
        if math.sin(a) < 0: continue
        pl = []
        for k in range(n + 1):
            u = k / n; y = H_ * 0.94 - u * H_ * 0.86; r = R * vase_r(u)
            pl.append((cx + r * math.cos(a), y + r * 0.18 * math.sin(a)))
        d.line(pl, fill=lite + (170,), width=s * 2)
    top = H_ * 0.08; rt = R * vase_r(1)
    d.ellipse((cx - rt, top - rt * 0.18, cx + rt, top + rt * 0.18), fill=dark + (255,))
    return im.resize((w, h), Image.LANCZOS)

def cube_icon(sz, col):
    def mk():
        s = 4; S = sz * s; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.polygon([(S * .5, S * .08), (S * .92, S * .3), (S * .5, S * .52), (S * .08, S * .3)], fill=col)
        d.polygon([(S * .08, S * .34), (S * .48, S * .56), (S * .48, S * .96), (S * .08, S * .74)], fill=tuple(int(v * .8) for v in col))
        d.polygon([(S * .92, S * .34), (S * .52, S * .56), (S * .52, S * .96), (S * .92, S * .74)], fill=tuple(int(v * .62) for v in col))
        return im.resize((sz, sz), Image.LANCZOS)
    return tc(("cube", sz, col), mk)

def dashed_rrect(d, box, col, r=24, dash=18, gap=12, width=4):
    x0, y0, x1, y1 = box
    def seg(p, q):
        L = math.dist(p, q); k = 0
        while k < L:
            a = k / L; b = min(L, k + dash) / L
            d.line((lerp(p[0], q[0], a), lerp(p[1], q[1], a), lerp(p[0], q[0], b), lerp(p[1], q[1], b)), fill=col, width=width); k += dash + gap
    seg((x0 + r, y0), (x1 - r, y0)); seg((x0 + r, y1), (x1 - r, y1)); seg((x0, y0 + r), (x0, y1 - r)); seg((x1, y0 + r), (x1, y1 - r))
    for bx, by, st in ((x0, y0, 180), (x1 - 2 * r, y0, 270), (x1 - 2 * r, y1 - 2 * r, 0), (x0, y1 - 2 * r, 90)):
        d.arc((bx, by, bx + 2 * r, by + 2 * r), st, st + 90, fill=col, width=width)

SW = 620
def nav(d, im, th, y=0):
    d.rectangle((0, y, SW, y + 96), fill=th["bg"])
    im.alpha_composite(cube_icon(46, th["acc"] + (255,)), (30, y + 25))
    d.text((88, y + 22), "Esnaf3D", font=hfont(th, 38), fill=th["ink"])
    for k in range(3): d.rounded_rectangle((SW - 74, y + 34 + k * 13, SW - 36, y + 40 + k * 13), 3, fill=th["ink"])
    im.alpha_composite(emoji("🛒", 38), (SW - 140, y + 28))
    d.line((0, y + 96, SW, y + 96), fill=th["soft"], width=2)

def site_img(theme, quote=True):
    """Esnaf3D mağazasının ana sayfası (temaya göre renkler). Yükseklik 1500."""
    def mk():
        th = THEMES[theme]; H_ = 1500
        im = Image.new("RGBA", (SW, H_), th["bg"] + (255,)); d = ImageDraw.Draw(im)
        nav(d, im, th)
        d.rounded_rectangle((24, 120, SW - 24, 500), 30, fill=th["soft"])
        f1 = hfont(th, 52)
        d.text((52, 160), "Fikrini yükle,", font=f1, fill=th["ink"]); d.text((52, 222), "biz basalım.", font=f1, fill=th["acc"])
        d.text((52, 300), "Anında 3D baskı", font=font(IS, 27), fill=th["sub"]); d.text((52, 336), "fiyat teklifi", font=font(IS, 27), fill=th["sub"])
        d.rounded_rectangle((52, 400, 300, 466), 33, fill=th["acc"]); d.text((82, 414), "Dosya yükle →", font=font(IB, 28), fill=(255, 255, 255))
        im.alpha_composite(vase(200, 300, th["acc"], 0.6), (370, 170))
        y = 530
        if quote:
            d.rounded_rectangle((24, y, SW - 24, y + 250), 28, fill=th["card"])
            d.text((52, y + 26), "3D Fiyat Teklifi", font=hfont(th, 34), fill=th["ink"])
            dashed_rrect(d, (52, y + 84, SW - 52, y + 170), th["acc"] + (255,), 20, 16, 10, 3)
            d.text((SW / 2 - tlen("Model dosyanı buraya bırak", font(IS, 26)) / 2, y + 112), "Model dosyanı buraya bırak", font=font(IS, 26), fill=th["sub"])
            x = 52
            for m in ("PLA", "PETG", "Reçine"):
                wv = tlen(m, font(IB, 24)) + 40
                d.rounded_rectangle((x, y + 190, x + wv, y + 230), 20, outline=th["acc"], width=2); d.text((x + 20, y + 196), m, font=font(IB, 24), fill=th["acc"]); x += wv + 14
            y += 280
        d.text((30, y), "Çok satanlar", font=hfont(th, 36), fill=th["ink"]); y += 66
        items = [("🏺", "Vazo"), ("⚙️", "Dişli seti"), ("🦖", "Mini dinozor"), ("🎲", "Oyun zarı"), ("🪴", "Saksı"), ("🔑", "Anahtarlık")]
        for i, (e, nm) in enumerate(items):
            cx_ = 24 + (i % 2) * 292; cy_ = y + (i // 2) * 290
            d.rounded_rectangle((cx_, cy_, cx_ + 280, cy_ + 270), 24, fill=th["card"])
            ei = emoji(e, 120); im.alpha_composite(ei, (int(cx_ + 140 - ei.size[0] / 2), int(cy_ + 30)))
            d.text((cx_ + 24, cy_ + 186), nm, font=font(IB, 28), fill=th["ink"])
            d.text((cx_ + 24, cy_ + 226), "★★★★★", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22), fill=th["acc"])
        return im
    return tc(("site", theme, quote), mk)

def phone(c, x, y, sw, sh, screen, a=1.0, scale=1.0):
    """x,y: ekran sol üst. screen: sw x sh RGBA"""
    if a <= 0.01: return
    b = 22
    def mk():
        im = Image.new("RGBA", (sw + b * 2 + 60, sh + b * 2 + 60), (0, 0, 0, 0))
        s = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(s).rounded_rectangle((30, 44, 30 + sw + 2 * b, 44 + sh + 2 * b), 70, fill=(0, 0, 0, 170))
        im.alpha_composite(s.filter(ImageFilter.GaussianBlur(18)))
        ImageDraw.Draw(im).rounded_rectangle((30, 30, 30 + sw + 2 * b, 30 + sh + 2 * b), 70, fill=(12, 12, 18), outline=(70, 74, 96), width=3)
        return im
    fr = tc(("phone", sw, sh), mk).copy()
    mask = Image.new("L", (sw, sh), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), 50, fill=255)
    scr = Image.new("RGBA", (sw, sh), (0, 0, 0, 0)); scr.paste(screen, (0, 0), mask)
    fr.alpha_composite(scr, (30 + b, 30 + b))
    ImageDraw.Draw(fr).rounded_rectangle((30 + b + sw / 2 - 70, 30 + b + 14, 30 + b + sw / 2 + 70, 30 + b + 44), 15, fill=(12, 12, 18))
    place(c, fr, x - 30 - b + (fr.size[0] * (1 - scale)) / 2, y - 30 - b + (fr.size[1] * (1 - scale)) / 2, a, "tl", scale)

def word_cap(c, t, words, y, size=100):
    """Kelimeler söylendikçe beliren tek satır başlık (satır baştan ortalanır). words: [(metin, renk, zaman)]"""
    allim = [native_text(w_, size, col) for w_, col, ti in words]
    ims = [(im, ti) for im, (w_, col, ti) in zip(allim, words) if t >= ti]
    if not ims: return
    tw = sum(i.size[0] for i in allim) + 6 * (len(allim) - 1); x = W / 2 - tw / 2
    for im, ti in ims:
        place(c, im, x + im.size[0] / 2, y, 1, "c", back_out((t - ti) / 0.25)); x += im.size[0] + 6

# ------------- sahne 1: soru -------------
OPTS = [("A", "12.000 satır", T_A, CORAL), ("B", "1.200 satır", T_B, AMBER), ("C", "0 satır", T_C, GREEN)]
def s1(c, t):
    a = 1 - clamp((t - T_ED) / 0.12)
    if a <= 0.01: return
    caption(c, t, [("Bu site kaç satır", WHITE)], 170, a, 0.0, size=92)
    if t >= 0.35: caption(c, t, [("kodla yapıldı?", AMBER)], 285, a, 0.35, emo="🤔", size=92)
    sc = clamp(t / 6.0)
    scroll = 380 * ease_io(clamp((t - 0.6) / 4.5))
    scr = Image.new("RGBA", (SW, 860), THEMES["Esnaf3D"]["bg"] + (255,))
    scr.alpha_composite(site_img("Esnaf3D").crop((0, int(scroll), SW, int(scroll) + 800)), (0, 60))
    scr = scr.resize((540, 749), Image.LANCZOS)
    phone(c, 270, 420, 540, 749, scr, a, 1 + 0.02 * sc)
    place(c, pill("Esnaf3D teması", font(IB, 30), WHITE, (255, 106, 26, 255), 20, 6), W / 2, 395, a, "c")
    for i, (L, s_, ti, col) in enumerate(OPTS):
        if t < ti: continue
        ia = clamp((t - ti) / 0.12) * a; y = 1290 + i * 168
        win = t >= T_ZERO and L == "C"; lose = t >= T_ZERO and L != "C"
        ia2 = ia * (0.35 if lose else 1)
        put_card(c, 130, y, 820, 140, GREEN if win else (90, 100, 150), ia2, CARD2, 0.6 if win else 0, 34)
        place(c, letter_badge(L, col, 96), 175, y + 70, ia2, "l", back_out((t - ti) / 0.3))
        place(c, text_img(s_, font(DX, 62)), 310, y + 70, ia2, "l")
        if lose:
            u = ease_out((t - T_ZERO) / 0.2); d = ImageDraw.Draw(c)
            d.line((300, y + 72, 300 + 520 * u, y + 72), fill=RED + (int(230 * a),), width=8)
        if win: place(c, icon_circle("check", 80, GREEN), 880, y + 70, ia, "c", back_out((t - T_ZERO) / 0.3))
    if T_ZERO <= t:
        za = clamp((t - T_ZERO) / 0.08) * a
        c.alpha_composite(Image.new("RGBA", (W, H), (6, 8, 20, int(150 * za))))
        place(c, native_text("Sıfır.", 210, GREEN), W / 2, 760, za, "c", lerp(1.9, 1, ease_out((t - T_ZERO) / 0.18)))
        place(c, native_text("0 satır kod", 80, WHITE), W / 2, 930, za * clamp((t - T_ZERO - 0.25) / 0.15), "c")
    if t < T_ZERO and t >= T_A:
        place(c, text_img("Yoruma yaz: A, B, C?", font(DB, 40), (200, 206, 228)), W / 2, 1810, a * clamp((t - T_A) / 0.3), "c")

# ------------- sahne 2: editör -------------
BLOCKS = [("Başlık", "T"), ("3D Fiyat Teklifi", "3D"), ("Ürün ızgarası", "Ü"), ("Yorumlar", "★"), ("Banner", "B")]
EX, EY, EW, EH = 40, 470, 1000, 1180          # editör penceresi
PX = EX + 360; PW = EW - 380; PY = EY + 110   # canlı önizleme alanı
def editor_frame():
    def mk():
        im = Image.new("RGBA", (EW, EH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, EW - 1, EH - 1), 34, fill=(22, 26, 40, 250), outline=(70, 80, 120), width=3)
        d.rounded_rectangle((0, 0, EW - 1, 90), 34, fill=(30, 36, 56)); d.rectangle((0, 60, EW - 1, 90), fill=(30, 36, 56))
        for k, col in enumerate((CORAL, AMBER, GREEN)): d.ellipse((28 + k * 34, 34, 50 + k * 34, 56), fill=col)
        d.text((150, 26), "Site Editörü", font=font(DB, 34), fill=WHITE)
        im.alpha_composite(pill("● Canlı önizleme", font(IB, 24), GREEN, (20, 60, 40, 255), 16, 6), (470, 26))
        im.alpha_composite(pill("Yayınla", font(IB, 26), WHITE, INDIGO + (255,), 22, 8), (EW - 170, 22))
        d.text((30, 116), "Bloklar", font=font(DB, 30), fill=GREY)
        for i, (nm, ic) in enumerate(BLOCKS):
            y = 170 + i * 120
            d.rounded_rectangle((26, y, 320, y + 100), 22, fill=(34, 40, 62), outline=(64, 74, 110), width=2)
            d.rounded_rectangle((44, y + 22, 100, y + 78), 14, fill=(255, 106, 26) if i == 1 else (70, 80, 120))
            fi = font(DX, 26 if len(ic) > 1 else 32); bw = tlen(ic, fi)
            d.text((72 - bw / 2, y + 32 if len(ic) > 1 else y + 28), ic, font=fi, fill=WHITE)
            d.text((116, y + 32), nm, font=font(IB, 28), fill=WHITE)
        d.text((30, 800), "Tema", font=font(DB, 30), fill=GREY)
        return im
    return tc("editor", mk)
def theme_at(t):
    if t < T_TH[0]: return "Esnaf3D"
    if t < T_TH[1]: return "Zephra"
    if t < T_TH[2]: return "Lumen"
    return "Esnaf3D"
def s2(c, t):
    a = clamp((t - T_ED) / 0.12) * (1 - clamp((t - T_UP) / 0.12))
    if a <= 0.01: return
    word_cap(c, t, [("Sürükle,", WHITE, T_DRAG - 0.05), ("bırak,", AMBER, V(7.2))], 190, 96)
    word_cap(c, t, [("temanı seç.", TEAL, T_TEMA)], 310, 96)
    slide = 60 * (1 - ease_out((t - T_ED) / 0.3))
    place(c, editor_frame(), EX, EY + slide, a, "tl")
    th_name = theme_at(t); dropped = t >= T_DROP
    # canlı önizleme (sitenin üst kısmı)
    pv = site_img(th_name, dropped).crop((0, 0, SW, 1000)).resize((PW, int(1000 * PW / SW)), Image.LANCZOS)
    ph = EH - 140 - 330
    pv = pv.crop((0, 0, PW, ph))
    m = Image.new("L", pv.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, pv.size[0] - 1, pv.size[1] - 1), 22, fill=255)
    pi = Image.new("RGBA", pv.size, (0, 0, 0, 0)); pi.paste(pv, (0, 0), m)
    place(c, pi, PX, PY + slide, a, "tl")
    if dropped and t < T_DROP + 0.6:               # yeni blok vurgusu
        qy = PY + slide + int(530 * PW / SW); qh = int(250 * PW / SW)
        g, pd = glow_rect(PW - 20, qh, (255, 106, 26), 22, 16, int(220 * (1 - (t - T_DROP) / 0.6)))
        place(c, g, PX + 10 - pd, qy - pd, a, "tl")
    for k, x in enumerate(THEME_X()):              # tema kartları
        nm = ("Zephra", "Lumen", "Esnaf3D")[k]; th = THEMES[nm]; sel = theme_at(t) == nm and t >= T_TH[0]
        y = EY + 860 + slide
        put_card(c, x, y, 290, 250, th["acc"] if sel else (64, 74, 110), a, th["bg"], 0.7 if sel else 0, 26)
        thumb = site_img(nm, True).crop((0, 0, SW, 560)).resize((250, 226), Image.LANCZOS)
        place(c, thumb, x + 20, y + 14, a, "tl")
        place(c, pill(nm, font(IB, 26), WHITE, (20, 22, 34, 235), 16, 5), x + 145, y + 222, a, "c")
    # imleç
    blk_y = EY + 170 + 120 + 50 + slide
    if t < T_DROP:
        u = ease_io((t - T_DRAG - 0.1) / (T_DROP - T_DRAG - 0.15))
        cx_ = lerp(200, PX + PW / 2, u); cy_ = lerp(blk_y, PY + 420 + slide, u)
        if t >= T_DRAG + 0.1:
            ghost = pill("3D Fiyat Teklifi", font(DX, 34), WHITE, (255, 106, 26, 235), 26, 14)
            place(c, ghost, cx_ - 40, cy_ - 10, a * 0.95, "tl", 1.05)
        draw_cursor(c, cx_, cy_, a, (t - T_DRAG) / 0.25)
    elif t < T_TH[0] - 0.25:
        draw_cursor(c, PX + PW / 2, PY + 420 + slide, a, (t - T_DROP) / 0.3)
    else:
        k = 0 if t < T_TH[1] else (1 if t < T_TH[2] else 2)
        tx = THEME_X()[k] + 160; ty = EY + 860 + 140 + slide
        if k == 0:
            u = ease_io((t - (T_TH[0] - 0.25)) / 0.25); tx = lerp(PX + PW / 2, tx, u); ty = lerp(PY + 420 + slide, ty, u)
        else:
            u = ease_io((t - (T_TH[k] - 0.2)) / 0.2); tx = lerp(THEME_X()[k - 1] + 160, tx, u)
        draw_cursor(c, tx, ty, a, (t - T_TH[k]) / 0.25)
def THEME_X(): return [EX + 22, EX + 22 + 322, EX + 22 + 644]

# ------------- sahne 3: müşteri vitrini -------------
QW, QH = 640, 1130; QX, QY = (W - QW) // 2, 520
def quote_screen(t):
    th = THEMES["Esnaf3D"]
    im = Image.new("RGBA", (QW, QH), th["bg"] + (255,)); d = ImageDraw.Draw(im)
    nav(d, im, th, 20)
    d.text((36, 150), "3D Fiyat Teklifi", font=font(DX, 50), fill=th["ink"])
    zx0, zy0, zx1, zy1 = 36, 240, QW - 36, 640
    got = t >= T_FILE + 0.35
    if not got:
        if t >= T_FILE: pass
        dashed_rrect(d, (zx0, zy0, zx1, zy1), th["acc"] + (255,), 30, 20, 12, 4)
        if t < T_FILE - 0.2: d.text((QW / 2 - tlen("Model dosyanı buraya bırak", font(IB, 32)) / 2, 420), "Model dosyanı buraya bırak", font=font(IB, 32), fill=th["sub"])
    else:
        d.rounded_rectangle((zx0, zy0, zx1, zy1), 30, fill=th["soft"])
        prog = clamp((t - T_FILE - 0.35) / 0.55)
        if prog < 1:
            d.rounded_rectangle((90, 430, QW - 90, 456), 13, fill=(255, 255, 255))
            d.rounded_rectangle((90, 430, 90 + (QW - 180) * prog, 456), 13, fill=th["acc"])
            d.text((QW / 2 - 70, 476), f"Yükleniyor %{int(prog * 100)}", font=font(IS, 26), fill=th["sub"])
        else:
            ang = (t - T_FILE) * 2.4
            vs = vase(230, 340, th["acc"], ang); im.alpha_composite(vs, (int(QW / 2 - 115), 270))
            im.alpha_composite(pill("vazo.stl", font(IB, 26), th["ink"], (255, 255, 255, 255), 16, 6), (60, 262))
    # malzeme
    d.text((36, 670), "Malzeme", font=font(IB, 30), fill=th["sub"])
    x = 36
    for i, m in enumerate(("PLA", "PETG", "Reçine")):
        wv = tlen(m, font(IB, 30)) + 48; sel = i == 0
        d.rounded_rectangle((x, 716, x + wv, 770), 27, fill=th["acc"] if sel else None, outline=th["acc"], width=3)
        d.text((x + 24, 726), m, font=font(IB, 30), fill=(255, 255, 255) if sel else th["acc"]); x += wv + 16
    # fiyat
    d.rounded_rectangle((36, 810, QW - 36, 960), 28, fill=th["card"])
    d.text((66, 834), "Anında fiyat", font=font(IB, 30), fill=th["sub"])
    if t >= T_PRICE:
        u = ease_out((t - T_PRICE) / 0.6); v = 349.90 * u
        d.text((66, 876), tl(v), font=font(DX, 64), fill=th["ink"])
        im.alpha_composite(pill("ÖRNEK", font(IB, 22), WHITE, (120, 124, 140, 255), 12, 4), (QW - 160, 840))
    else:
        d.text((66, 876), "—", font=font(DX, 64), fill=th["sub"])
    paid = t >= T_PAY + 0.15
    d.rounded_rectangle((36, 990, QW - 36, 1090), 50, fill=GREEN if paid else th["acc"])
    bt = "Ödendi ✓".replace(" ✓", "") if paid else "Öde"
    bw = tlen(bt, font(DX, 44)); d.text((QW / 2 - bw / 2, 1012), bt, font=font(DX, 44), fill=(255, 255, 255))
    return im
def s3(c, t):
    a = clamp((t - T_UP) / 0.12) * (1 - clamp((t - T_PANEL) / 0.12))
    if a <= 0.01: return
    if t < T_PRICE - 0.05: lines = [("Müşterin dosyasını", WHITE), ("yükler,", AMBER)]
    elif t < T_PAY - 0.05: lines = [("fiyatını", WHITE), ("anında görür,", AMBER)]
    else: lines = [("öder.", GREEN)]
    s0 = T_UP if t < T_PRICE - 0.05 else (T_PRICE if t < T_PAY - 0.05 else T_PAY)
    caption(c, t, lines, 200, a, s0, size=92)
    phone(c, QX, QY, QW, QH, quote_screen(t), a)
    # dosya uçuşu
    if T_UP + 0.1 <= t < T_FILE + 0.4:
        u = ease_io((t - T_UP - 0.1) / (T_FILE + 0.35 - T_UP - 0.1))
        fx = lerp(W + 100, W / 2, u); fy = lerp(380, QY + 440, u)
        fc = tc("filecard", lambda: pill("📄 vazo.stl".replace("📄 ", ""), font(DX, 40), (24, 24, 32), (255, 255, 255, 255), 28, 14))
        place(c, emoji("📄", 90), fx - 150, fy, a, "c", 1 - 0.3 * u)
        place(c, fc, fx + 30, fy, a, "c", 1 - 0.3 * u)
    if t >= T_PAY - 0.1:
        draw_cursor(c, W / 2 + 40, QY + 1040, a, (t - T_PAY) / 0.25)
    if t >= T_PAY + 0.2:
        sa = clamp((t - T_PAY - 0.2) / 0.15) * a; yy = 1775 - 40 * (1 - ease_out((t - T_PAY - 0.2) / 0.25))
        put_card(c, 160, yy - 70, 760, 140, GREEN, sa, CARD2, 0.6, 34)
        place(c, icon_circle("check", 80, GREEN), 230, yy, sa, "c")
        place(c, text_img("Ödeme alındı", font(DX, 52)), 290, yy - 20, sa, "l")
        place(c, text_img("PayTR · iyzico ile güvenli ödeme", font(DS, 30), (200, 206, 228)), 290, yy + 34, sa, "l")

# ------------- sahne 4: panel -------------
ROWS = [("box", "Sipariş alındı", "vazo.stl · PLA", INDIGO), ("mail", "e-Fatura kesildi", "otomatik", TEAL), ("check", "Kargo etiketi hazır", "yazdırmaya hazır", AMBER)]
def s4(c, t):
    a = clamp((t - T_PANEL) / 0.12) * (1 - clamp((t - T_S1) / 0.1))
    if a <= 0.01: return
    caption(c, t, [("Sipariş, fatura,", WHITE), ("kargo etiketi:", AMBER)], 200, a, T_PANEL, size=92)
    put_card(c, 70, 470, 940, 960, (80, 92, 140), a, CARD, 0, 40)
    place(c, logo(60), 120, 540, a, "l")
    place(c, pill("Web siten", font(IB, 28), (30, 22, 4), GOLD + (255,), 18, 6), 940, 540, a, "r")
    # bildirim
    u = ease_out((t - T_PANEL) / 0.3)
    nx = lerp(W + 50, 110, u)
    put_card(c, nx, 620, 860, 150, (255, 106, 26), a, CARD2, 0.5, 32)
    place(c, cube_icon(80, (255, 106, 26, 255)), nx + 40, 695, a, "l")
    place(c, text_img("Web sitenden yeni sipariş", font(DX, 44)), nx + 150, 670, a, "l")
    place(c, text_img("Esnaf3D · vazo.stl", font(DS, 32), GREY), nx + 150, 722, a, "l")
    for i, (ic, s_, sub, col) in enumerate(ROWS):
        ti = T_R[i]
        if t < ti: continue
        ra = clamp((t - ti) / 0.12) * a; dx = 70 * (1 - ease_out((t - ti) / 0.22)); y = 830 + i * 190
        put_card(c, 110 + dx, y, 860, 160, col, ra, CARD2, 0.3, 32)
        place(c, icon_circle(ic, 96, col), 150 + dx, y + 80, ra, "l", back_out((t - ti) / 0.3))
        place(c, text_img(s_, font(DX, 52)), 270 + dx, y + 58, ra, "l")
        place(c, text_img(sub, font(DS, 32), GREY), 270 + dx, y + 112, ra, "l")
        place(c, icon_circle("check", 64, GREEN), 900 + dx, y + 80, ra * clamp((t - ti - 0.2) / 0.1), "c")
    if t >= T_READY:
        ra = clamp((t - T_READY) / 0.1) * a
        st = tc("stamp_hazir", lambda: native_text("Panelinde hazır.", 104, GREEN).rotate(-6, expand=True, resample=Image.BICUBIC))
        place(c, st, W / 2, 1640, ra, "c", lerp(1.8, 1, ease_out((t - T_READY) / 0.18)))

# ------------- sahne 5: slogan -------------
def s5(c, t):
    a = clamp((t - T_S1) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(236 * a))))
    # "</>" kodu çizilip üstü karalanıyor
    place(c, native_text("</>", 230, (120, 130, 170)), W / 2, 560, a, "c")
    u = ease_out((t - T_S1 - 0.25) / 0.25)
    if u > 0:
        ImageDraw.Draw(c).line((W / 2 - 200, 650, W / 2 - 200 + 400 * u, 470), fill=RED + (int(255 * a),), width=22)
    place(c, native_text("Siteni kodlama.", 132, WHITE), W / 2, 860, a, "c", lerp(1.5, 1, ease_out((t - T_S1) / 0.18)))
    if t >= T_S2:
        u = ease_out((t - T_S2) / 0.35); x = lerp(-300, W / 2, u)
        place(c, native_text("Sürükle.", 170, TEAL), x, 1060, a, "c")
        draw_cursor(c, x + 345, 1085, a, (t - T_S2 - 0.3) / 0.25)

PACKS = [("Pazaryeri Pro", "8 pazaryeri: stok, sipariş, e-fatura, kargo", (242, 122, 32)),
         ("Web + Mağaza", "Kendi siten: editör, tema, domain, online ödeme", GOLD),
         ("Full", "Web siten + pazaryerlerin, tek panelde", TEAL)]
def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(242 * a))))
    place(c, logo(120), W / 2, 400, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, native_text("Kendi siten, 0 satır kod.", 74, WHITE), W / 2, 560, la, "c")
    for i, (nm, sub, col) in enumerate(PACKS):
        ti = T_END + 0.45 + i * 0.18
        ia = clamp((t - ti) / 0.18) * a; dx = 90 * (1 - ease_out((t - ti) / 0.25))
        y = 670 + i * 200; hl = i == 1
        put_card(c, 90 + dx, y, 900, 170, col, ia * (1 if hl else 0.8), CARD2 if hl else CARD, 0.9 if hl else 0.2, 34)
        place(c, letter_badge(str(i + 1), col, 96), 130 + dx, y + 85, ia, "l")
        place(c, text_img(nm, font(DX, 56)), 260 + dx, y + 58, ia, "l")
        place(c, text_img(sub, font(DS, 32), (205, 210, 232)), 260 + dx, y + 118, ia, "l")
        if hl: place(c, pill("Bu video", font(IB, 26), (30, 22, 4), GOLD + (255,), 14, 5), 960 + dx, y + 10, ia, "r")
    fa = clamp((t - T_END - 1.1) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1330, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 76), GOLD), W / 2, 1440, fa, "c")

FLASH = (T_ZERO, T_ED, T_DROP, T_UP, T_PAY + 0.15, T_PANEL, T_READY, T_S1, T_END)
def frame(t):
    c = BG.copy().convert("RGBA")
    s1(c, t); s2(c, t); s3(c, t); s4(c, t); s5(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in (T_ZERO, T_DROP, T_PAY + 0.15, T_READY, T_S1, T_S2):
        if 0 <= t - x < 0.25: sh += 10 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.0), clamp((t - T_LOOP) / 0.25))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, vo_off=VO_OFF, a=T_A, b=T_B, c=T_C, zero=T_ZERO, ed=T_ED, drag=T_DRAG, drop=T_DROP, th=list(T_TH),
                              up=T_UP, file=T_FILE, price=T_PRICE, pay=T_PAY, panel=T_PANEL, rows=list(T_R), ready=T_READY,
                              s1=T_S1, s2=T_S2, end=T_END, loop=T_LOOP)))
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
