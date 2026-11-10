"""Dashtock "11.11 yarın. 12 Kasım'da ne satacaksın?" ~29.8 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: Fırsat Radarı (Google Trends, sosyal medya, Amazon, Trendyol sinyalleri; 7 boyutlu skor; 15 fırsat; neden önerildiği açıklamalı).
Akış: "11.11 YARIN." -> "12 Kasım'da ne satacaksın?" -> A/B/C ürün kartı + 3-2-1 -> "Seçtin. Neye göre?" (His / Rakip / Geçen yıl üstü çizilir)
-> Fırsat Radarı taraması (4 kaynak) -> fırsat kartı: 7 çubuk skor + "Neden?" -> "Tahminle stok alınmaz. Veriyle alınır." -> logo, döngü.
Arayüz çizim, ürünler ve skorlar ÖRNEK.
Kullanım: python3 render_radar.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 29.8
T_Q = 4.6       # A/B/C sorusu
T_CD = 5.9      # geri sayım
T_SEC = 8.6     # "Seçtin. Neye göre?"
T_STRIKE = [10.2, 11.2, 12.2]
T_RAD = 13.4    # radar
T_SRC = [14.0, 14.9, 15.8, 16.7]
T_CARD = 18.7   # fırsat kartı
T_WHY = [20.4, 20.9, 21.4]
T_S = 22.6      # slogan
T_END = 25.4
T_LOOP = DUR - 0.3

PRODUCTS = [("A", "Termos", PINK, "cup"), ("B", "Isıtıcı yelek", INDIGO, "vest"), ("C", "Telefon standı", TEAL, "phone")]

def prod_icon(kind, size, col):
    def mk():
        s = 4; S = size * s; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        c = col + (255,); hi = (255, 255, 255, 200)
        if kind == "cup":
            d.rounded_rectangle((S * .33, S * .18, S * .67, S * .88), S // 14, fill=c)
            d.rounded_rectangle((S * .30, S * .10, S * .70, S * .22), S // 30, fill=hi)
            d.rectangle((S * .40, S * .35, S * .45, S * .75), fill=(255, 255, 255, 90))
        elif kind == "vest":
            d.polygon([(S * .30, S * .14), (S * .42, S * .14), (S * .50, S * .30), (S * .58, S * .14), (S * .70, S * .14), (S * .80, S * .32),
                       (S * .76, S * .86), (S * .24, S * .86), (S * .20, S * .32)], fill=c)
            d.line([(S * .5, S * .32), (S * .5, S * .86)], fill=hi, width=S // 40)
            for y in (0.45, 0.6, 0.75): d.line([(S * .26, S * y), (S * .74, S * y)], fill=(255, 255, 255, 70), width=S // 60)
        elif kind == "phone":
            d.polygon([(S * .22, S * .86), (S * .78, S * .86), (S * .62, S * .62), (S * .38, S * .62)], fill=tuple(int(v * .7) for v in col) + (255,))
            d.rounded_rectangle((S * .34, S * .12, S * .66, S * .70), S // 20, fill=c)
            d.rounded_rectangle((S * .38, S * .17, S * .62, S * .64), S // 30, fill=(20, 26, 42, 255))
        return im.resize((size, size), Image.LANCZOS)
    return tc(("pi", kind, size, col), mk)

def s_hook(c, t):
    a = 1 - clamp((t - T_Q + 0.1) / 0.12)
    if a <= 0.01: return
    # takvim yaprağı
    d = ImageDraw.Draw(c)
    cx, cy, w, h = W / 2, 760, 560, 600
    sc = lerp(0.6, 1, back_out(t / 0.35))
    x0, y0 = cx - w / 2 * sc, cy - h / 2 * sc
    d.rounded_rectangle((x0, y0, x0 + w * sc, y0 + h * sc), int(50 * sc), fill=(245, 246, 252, int(255 * a)))
    d.rounded_rectangle((x0, y0, x0 + w * sc, y0 + 150 * sc), int(50 * sc), fill=RED + (int(255 * a),))
    d.rectangle((x0, y0 + 100 * sc, x0 + w * sc, y0 + 150 * sc), fill=RED + (int(255 * a),))
    flip = t >= 2.2
    place(c, text_img("KASIM", font(DX, int(70 * sc)), WHITE), cx, y0 + 78 * sc, a, "c")
    if not flip:
        place(c, text_img("11", font(DX, int(300 * sc)), (20, 24, 40)), cx, cy + 70 * sc, a, "c")
    else:
        u = t - 2.2
        place(c, text_img("12", font(DX, 300), (20, 24, 40)), cx, cy + 70, a, "c", lerp(1.3, 1, ease_out(u / 0.2)))
        # kopan yaprak
        if u < 0.6:
            leaf = text_img("11", font(DX, 300), (20, 24, 40))
            place(c, leaf, cx + 500 * ease_out(u / 0.6), cy + 70 - 300 * u + 900 * u * u, a * (1 - u / 0.6), "c")
    if not flip:
        place(c, native_text("11.11", 170, GOLD), W / 2, 210, a, "c", lerp(1.5, 1, ease_out(t / 0.2)))
        place(c, native_text("YARIN.", 150, WHITE), W / 2, 1300, clamp((t - 0.6) / 0.1) * a, "c", lerp(1.6, 1, ease_out((t - 0.6) / 0.2)))
        place(c, text_img("Herkes kampanyayı konuşuyor.", font(DB, 50), (205, 210, 232)), W / 2, 1460, clamp((t - 1.1) / 0.3) * a, "c")
    else:
        u = t - 2.2
        place(c, native_text("Peki 12 Kasım'da", 110, WHITE), W / 2, 200, a, "c", back_out(u / 0.3))
        place(c, native_text("ne satacaksın?", 130, GOLD), W / 2, 1300, clamp((u - 0.35) / 0.1) * a, "c", lerp(1.6, 1, ease_out((u - 0.35) / 0.2)))

def pcard(L, name, col, kind, w=900, h=300, sel=False):
    def mk():
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 36, fill=CARD2 + (250,), outline=col + (255,), width=4)
        im.alpha_composite(letter_badge(L, col, 96), (36, 36))
        im.alpha_composite(prod_icon(kind, 200, col), (170, 50))
        im.alpha_composite(text_img(name, font(DB, 64)), (410, 70))
        im.alpha_composite(text_img("önümüzdeki ay yükselir mi?", font(IM, 34), GREY), (414, 165))
        return im
    return tc(("pc", L, name, w, h), mk)

def s_quiz(c, t):
    a = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_SEC + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_Q
    place(c, native_text("Seç.", 120, WHITE), W / 2, 170, a, "c", lerp(1.5, 1, ease_out(u / 0.2)))
    place(c, native_text("Hangisi yükselecek?", 96, GOLD), W / 2, 300, clamp((u - 0.3) / 0.1) * a, "c", back_out((u - 0.3) / 0.3))
    for i, (L, nm, col, kind) in enumerate(PRODUCTS):
        v = u - 0.2 - i * 0.18
        place(c, pcard(L, nm, col, kind), W / 2 + 700 * (1 - ease_out(v / 0.35)), 610 + i * 350, clamp(v / 0.1) * a, "c")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), W - 70, 1610, a, "r")
    if T_CD <= t < T_SEC:
        seg = (T_SEC - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text("Yoruma yaz!", 72, WHITE), W / 2, 1720, 1, "c")
        place(c, native_text(str(max(1, n)), 130, GOLD), W / 2, 1840, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))

def s_sec(c, t):
    a = clamp((t - T_SEC) / 0.12) * (1 - clamp((t - T_RAD + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_SEC
    place(c, native_text("Seçtin.", 130, WHITE), W / 2, 260, a, "c", lerp(1.6, 1, ease_out(u / 0.2)))
    place(c, native_text("Peki neye göre?", 110, CORAL), W / 2, 420, clamp((u - 0.5) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.5) / 0.2)))
    for i, (lab, emo) in enumerate((("His", "🤔"), ("Rakibe bakarak", "👀"), ("Geçen yıla göre", "⏪"))):
        ts = T_STRIKE[i]
        v = t - (ts - 0.6)
        if v < 0: continue
        y = 760 + i * 300
        im = rich([(lab, WHITE), ("emo", emo)], 84)
        place(c, im, W / 2, y, clamp(v / 0.1) * a, "c", back_out(v / 0.3))
        if t >= ts:
            k = ease_out((t - ts) / 0.25)
            d = ImageDraw.Draw(c)
            hw = im.size[0] / 2 + 30
            d.line((W / 2 - hw, y + 6, W / 2 - hw + 2 * hw * k, y - 6), fill=RED + (int(255 * a),), width=16)
    ka = clamp((t - T_STRIKE[2] - 0.4) / 0.2) * a
    place(c, text_img("Üçü de tahmin.", font(DB, 58), GOLD), W / 2, 1700, ka, "c")

SRC = [("Google Trends", BLUE), ("Sosyal medya", PINK), ("Amazon", AMBER), ("Trendyol", CORAL)]
SRC_POS = [(230, 640), (850, 640), (230, 1380), (850, 1380)]
random.seed(4)
DOTS = [(random.uniform(0, 6.28), random.uniform(60, 330), random.choice([TEAL, GOLD, PINK, BLUE])) for _ in range(15)]
def s_radar(c, t):
    a = clamp((t - T_RAD) / 0.15) * (1 - clamp((t - T_CARD + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_RAD
    place(c, native_text("Fırsat Radarı", 120, TEAL), W / 2, 200, a, "c", back_out(u / 0.3))
    place(c, text_img("Dashtock", font(DB, 46), (205, 210, 232)), W / 2, 315, clamp((u - 0.2) / 0.2) * a, "c")
    cx, cy, R = W / 2, 1010, 360
    d = ImageDraw.Draw(c)
    for k in range(4):
        r = R * (k + 1) / 4
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=TEAL + (int(110 * a),), width=3)
    d.line((cx - R, cy, cx + R, cy), fill=TEAL + (int(70 * a),), width=2); d.line((cx, cy - R, cx, cy + R), fill=TEAL + (int(70 * a),), width=2)
    ang = (t - T_RAD) * 3.2
    for k in range(18):
        aa = ang - k * 0.035
        d.line((cx, cy, cx + R * math.cos(aa), cy + R * math.sin(aa)), fill=TEAL + (int(200 * (1 - k / 18) * a),), width=10)
    # kaynaklar
    for i, ((lab, col), (sx, sy)) in enumerate(zip(SRC, SRC_POS)):
        v = t - T_SRC[i]
        if v < 0: continue
        ca = clamp(v / 0.12) * a
        p = pill(lab, font(DB, 40), WHITE, col + (255,), 26, 12)
        place(c, p, sx, sy, ca, "c", back_out(v / 0.3))
        # akan sinyal noktaları
        for j in range(3):
            q = ((t - T_SRC[i]) * 1.4 + j / 3) % 1
            px, py = lerp(sx, cx, q), lerp(sy, cy, q)
            d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=col + (int(220 * ca * (1 - q)),))
    # fırsat noktaları
    nd = int(clamp((u - 0.8) / 4.0) * len(DOTS))
    for i in range(nd):
        th, rr, col = DOTS[i]
        px, py = cx + rr * math.cos(th), cy + rr * math.sin(th)
        pu = 1 + 0.25 * math.sin(t * 6 + i)
        d.ellipse((px - 14 * pu, py - 14 * pu, px + 14 * pu, py + 14 * pu), fill=col + (int(240 * a),))
    place(c, rich([(f"{nd} fırsat", GOLD)], 76), W / 2, 1610, clamp((u - 1.0) / 0.2) * a, "c")
    place(c, text_img("sinyal taraması · ÖRNEK", font(DS, 34), GREY), W / 2, 1700, clamp((u - 1.0) / 0.2) * a, "c")

def s_card(c, t):
    a = clamp((t - T_CARD) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_CARD
    place(c, native_text("7 ölçüyle puan.", 104, WHITE), W / 2, 175, a, "c", back_out(u / 0.3))
    place(c, native_text("Nedeniyle.", 110, TEAL), W / 2, 300, clamp((u - 1.5) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 1.5) / 0.2)))
    x0, y0, w = 60, 420, 960
    put_card(c, x0, y0, w, 1300, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Fırsat Radarı · 1 / 15", font(DB, 44)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    place(c, prod_icon("vest", 150, INDIGO), x0 + 50, y0 + 230, a, "l")
    place(c, text_img("Isıtıcı yelek", font(DB, 60)), x0 + 230, y0 + 195, a, "l")
    place(c, text_img("Fırsat skoru", font(IM, 34), GREY), x0 + 232, y0 + 265, a, "l")
    sc = int(86 * ease_out((u - 0.3) / 1.0))
    place(c, text_img(str(sc), font(DX, 120), GOLD), x0 + w - 50, y0 + 235, a, "r")
    d = ImageDraw.Draw(c)
    vals = [0.92, 0.78, 0.85, 0.66, 0.9, 0.72, 0.81]
    bx0, by0, bh, gap = x0 + 70, y0 + 640, 260, 118
    for i, v in enumerate(vals):
        k = ease_out((u - 0.3 - i * 0.12) / 0.5)
        bx = bx0 + i * gap
        d.rounded_rectangle((bx, by0 - bh, bx + 70, by0), 14, fill=CARD2 + (int(255 * a),))
        hh = bh * v * k
        if hh > 4: d.rounded_rectangle((bx, by0 - hh, bx + 70, by0), 14, fill=mixc(INDIGO, TEAL, v) + (int(255 * a),))
        place(c, text_img(str(i + 1), font(DB, 34), GREY), bx + 35, by0 + 36, a, "c")
    place(c, text_img("Neden önerildi?", font(DB, 46)), x0 + 50, y0 + 790, clamp((t - T_WHY[0] + 0.3) / 0.2) * a, "l")
    for i, s in enumerate(("Aramalar hızla artıyor", "Sosyal medyada konuşuluyor", "Pazaryerinde rekabet düşük")):
        v = t - T_WHY[i]
        if v < 0: continue
        yy = y0 + 900 + i * 120
        ra = clamp(v / 0.12) * a
        place(c, icon_circle("check", 64, TEAL, (8, 30, 26)), x0 + 50, yy, ra, "l", back_out(v / 0.3))
        place(c, text_img(s, font(DB, 44)), x0 + 140, yy, ra, "l")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    u = t - T_S
    place(c, native_text("Tahminle", 150, WHITE), W / 2, 700, a, "c", lerp(1.5, 1, ease_out(u / 0.18)))
    place(c, native_text("stok alınmaz.", 140, WHITE), W / 2, 870, clamp((u - 0.3) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.3) / 0.18)))
    place(c, native_text("Veriyle alınır.", 140, GOLD), W / 2, 1100, clamp((u - 1.2) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 1.2) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Kendi web siten + pazaryerlerin", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("ve Fırsat Radarı, tek panelde", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Sen hangisini", 84, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("seçtin?", GOLD), ("emo", "👇")], 84, GOLD), W / 2, 1030, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (CORAL if t < T_RAD else TEAL, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, 2.2, T_Q, T_SEC, T_RAD, T_CARD, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_hook(c, t); s_quiz(c, t); s_sec(c, t); s_radar(c, t); s_card(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [2.2, T_SEC] + T_STRIKE + [T_S, T_S + 0.3, T_S + 1.2]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.7), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, flip=2.2, q=T_Q, cd=T_CD, sec=T_SEC, strike=T_STRIKE, rad=T_RAD, src=T_SRC, card=T_CARD,
                              why=T_WHY, s=T_S, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
