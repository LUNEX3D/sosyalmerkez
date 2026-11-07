"""Dashtock "11.11'e 4 gün. Bu ürün kaç vitrinde satışta? Say." ~29.6 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: Ürün Yükle / "Eksikleri Dağıt" + Kategori Merkezi (akıllı kategori eşleştirme), web sitesi + 8 pazaryeri.
Akış: kanca + ürün kartı + 8 vitrin kutusu (5 dolu, 3 boş) -> 3-2-1 -> "5 vitrin. 3'ü boş." -> "11.11'de o vitrine gelen
müşteri seni bulamaz." -> Eksikleri Dağıt paneli (eksik kanallar, kategori eşleşir, tek tuş, 8/8) ->
"Olmadığın vitrinde satamazsın." -> logo + yorum sorusu, döngü. Tüm veriler ÖRNEK, arayüz çizim.
Kullanım: python3 render_vitrin.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 29.6
T_CD = 5.6      # geri sayım
T_ANS = 8.4     # "5 vitrin. 3'ü boş."
T_MISS = 11.0   # müşteri seni bulamaz
T_PAN = 15.6    # panel
T_SEND = 21.3   # tek tuş
T_S = 23.4      # slogan
T_END = 25.6
T_LOOP = DUR - 0.3

CH = [("Web siten", TEAL, 1), ("Trendyol", CORAL, 1), ("Hepsiburada", AMBER, 1), ("ÇiçekSepeti", PINK, 0),
      ("N11", PURPLE, 1), ("Pazarama", GREEN, 0), ("Amazon", BLUE, 1), ("Ozon", INDIGO, 0)]
ORDER = [0, 5, 2, 7, 1, 3, 6, 4]   # görünme sırası (karışık)
MISS = [("ÇiçekSepeti", PINK, "Ayakkabı › Spor Ayakkabı"), ("Pazarama", GREEN, "Ayakkabı & Çanta › Sneaker"), ("Ozon", INDIGO, "Ayakkabı › Erkek › Spor")]

def tile(name, col, state, w=440, h=150):
    def mk():
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if state == "on":
            d.rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=CARD2 + (250,), outline=col + (255,), width=4)
            d.ellipse((26, h / 2 - 22, 70, h / 2 + 22), fill=col + (255,))
            d.text((88, h / 2 - 44), name, font=font(DB, 40), fill=WHITE)
            d.text((88, h / 2 + 6), "Satışta", font=font(IS, 30), fill=TEAL)
            ic = icon_circle("check", 54, TEAL, (8, 30, 26)); im.alpha_composite(ic, (w - 76, h // 2 - 27))
        else:
            oc = CORAL if state == "miss" else DIM
            for x in range(10, w - 10, 26): d.line((x, 2, x + 12, 2), fill=oc + (255,), width=4); d.line((x, h - 3, x + 12, h - 3), fill=oc + (255,), width=4)
            for y in range(12, h - 10, 26): d.line((2, y, 2, y + 12), fill=oc + (255,), width=4); d.line((w - 3, y, w - 3, y + 12), fill=oc + (255,), width=4)
            d.ellipse((26, h / 2 - 22, 70, h / 2 + 22), outline=DIM + (255,), width=4)
            d.text((88, h / 2 - 44), name, font=font(DB, 40), fill=GREY)
            d.text((88, h / 2 + 6), "Ürün yok" if state == "off" else "Boş vitrin", font=font(IS, 30), fill=oc)
        return im
    return tc(("tile", name, col, state, w, h), mk)

def shoe(size):
    def mk():
        s = 4; S = size * s; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, S - 1, S - 1), S // 5, fill=(44, 52, 82, 255))
        d.polygon([(S * .14, S * .62), (S * .2, S * .38), (S * .38, S * .36), (S * .52, S * .5), (S * .82, S * .56), (S * .88, S * .66), (S * .14, S * .68)], fill=CORAL + (255,))
        d.rounded_rectangle((S * .12, S * .66, S * .9, S * .74), S // 40, fill=WHITE)
        for k in range(3): d.line((S * (.3 + k * .07), S * .42, S * (.36 + k * .07), S * .5), fill=WHITE, width=S // 40)
        return im.resize((size, size), Image.LANCZOS)
    return tc(("shoe", size), mk)

GX = (80, 560); GY0 = 720; GDY = 190
def tile_pos(i): return GX[i % 2], GY0 + (i // 2) * GDY

def s_quiz(c, t):
    a = 1 - clamp((t - T_PAN + 0.15) / 0.15)
    if a <= 0.01: return
    if t < T_ANS:
        place(c, native_text("11.11'e 4 gün.", 108, GOLD), W / 2, 170, a, "c", lerp(1.35, 1, ease_out(t / 0.25)))
        place(c, native_text("Bu ürün kaç", 92, WHITE), W / 2, 300, clamp((t - 0.5) / 0.1) * a, "c", back_out((t - 0.5) / 0.3))
        place(c, native_text("vitrinde satışta?", 92, WHITE), W / 2, 405, clamp((t - 0.7) / 0.1) * a, "c", back_out((t - 0.7) / 0.3))
    elif t < T_MISS:
        v = t - T_ANS
        place(c, native_text("5 vitrin.", 130, TEAL), W / 2, 210, a, "c", lerp(1.6, 1, ease_out(v / 0.2)))
        place(c, native_text("3'ü bomboş.", 110, CORAL), W / 2, 360, clamp((v - 0.5) / 0.1) * a, "c", lerp(1.6, 1, ease_out((v - 0.5) / 0.2)))
    else:
        v = t - T_MISS
        place(c, native_text("11.11'de o vitrine", 86, WHITE), W / 2, 200, a, "c", back_out(v / 0.3))
        place(c, native_text("gelen müşteri", 86, WHITE), W / 2, 300, clamp((v - 0.2) / 0.1) * a, "c", back_out((v - 0.2) / 0.3))
        place(c, native_text("seni bulamaz.", 104, CORAL), W / 2, 415, clamp((v - 0.6) / 0.1) * a, "c", lerp(1.5, 1, ease_out((v - 0.6) / 0.2)))
    # ürün kartı (yalnız soru bölümünde)
    pa = clamp((t - 0.9) / 0.2) * a * (1 - clamp((t - T_ANS) / 0.2))
    if pa > 0.01:
        put_card(c, 140, 500, 800, 170, None, pa, CARD, 0, 34)
        place(c, shoe(120), 170, 585, pa, "l")
        place(c, text_img("Spor Ayakkabı", font(DB, 46)), 316, 560, pa, "l")
        place(c, text_img("Senin ürünün · 120 stok", font(IM, 32), GREY), 316, 614, pa, "l")
        place(c, pill("ÖRNEK", font(IB, 26), (30, 22, 4), GOLD + (255,), 14, 4), 915, 532, pa, "r")
    # vitrinler
    for k, i in enumerate(ORDER):
        nm, col, on = CH[i]
        t0 = 1.3 + k * 0.22
        ta = clamp((t - t0) / 0.12) * a
        if ta <= 0.01: continue
        state = "on" if on else ("miss" if t >= T_ANS else "off")
        x, y = tile_pos(i)
        sc = back_out((t - t0) / 0.3)
        if state == "miss" and t >= T_MISS: sc *= 1 + 0.04 * math.sin((t - T_MISS) * 9)
        dim = (t >= T_ANS and on)
        place(c, tile(nm, col, state), x + 220, y + 75, ta * (0.45 if dim else 1), "c", sc)
    if T_CD <= t < T_ANS:
        seg = (T_ANS - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text("Say!", 80, WHITE), W / 2, 1560, 1, "c")
        place(c, native_text(str(max(1, n)), 160, GOLD), W / 2, 1700, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))
    elif t < T_CD:
        place(c, text_img("Web siten + 7 pazaryeri: 8 vitrin. Kaçında?", font(DB, 44), (205, 210, 232)), W / 2, 1560, clamp((t - 3.4) / 0.3) * a, "c")
    if T_MISS <= t:
        v = t - T_MISS
        place(c, text_img("Ürün o pazaryerinde yoksa, aramada da yoksun.", font(DB, 40), (205, 210, 232)), W / 2, 1560, clamp((v - 1.2) / 0.3) * a, "c")
        place(c, text_img("Neden yok? Her pazaryerinin kategorisi farklı.", font(IM, 36), GREY), W / 2, 1625, clamp((v - 2.2) / 0.3) * a, "c")

def s_panel(c, t):
    a = clamp((t - T_PAN) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_PAN
    place(c, native_text("Eksiği bulur.", 92, WHITE), W / 2, 165, a, "c", back_out(u / 0.3))
    place(c, native_text("Kategoriyi eşler.", 92, TEAL), W / 2, 275, clamp((u - 0.3) / 0.1) * a, "c", back_out((u - 0.3) / 0.3))
    x0, y0, w = 50, 380, 980
    put_card(c, x0, y0, w, 1440, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Ürün Yükle · Eksikler", font(DB, 46)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    # ürün satırı + sayaç
    d = ImageDraw.Draw(c)
    place(c, shoe(96), x0 + 40, y0 + 190, a, "l")
    place(c, text_img("Spor Ayakkabı", font(DB, 42)), x0 + 160, y0 + 168, a, "l")
    done = [T_SEND + 0.5 + i * 0.35 for i in range(3)]
    n = 5 + sum(1 for x in done if t >= x)
    place(c, text_img(f"{n} / 8 vitrinde", font(DS, 34), TEAL if n == 8 else GREY), x0 + 160, y0 + 214, a, "l")
    place(c, native_text(f"{n}/8", 84, TEAL if n == 8 else CORAL), x0 + w - 40, y0 + 190, a, "r", 1 + 0.15 * max([math.exp(-(t - x) * 10) for x in done if t >= x] + [0]))
    # eksik satırları
    place(c, text_img("Bu üründe eksik vitrinler", font(DS, 36), GREY), x0 + 40, y0 + 320, clamp((u - 0.4) / 0.2) * a, "l")
    for i, (nm, col, cat) in enumerate(MISS):
        y = y0 + 380 + i * 250
        ra = clamp((u - 0.5 - i * 0.15) / 0.2) * a
        if ra <= 0.01: continue
        ok = t >= done[i]
        d.rounded_rectangle((x0 + 30, y, x0 + w - 30, y + 220), 24, fill=CARD2 + (int(235 * ra),), outline=(TEAL if ok else CORAL) + (int(170 * ra),), width=3)
        d.ellipse((x0 + 58, y + 40, x0 + 98, y + 80), fill=col + (int(255 * ra),))
        place(c, text_img(nm, font(DB, 42)), x0 + 120, y + 60, ra, "l")
        if ok:
            place(c, pill("Satışta ✓", font(DB, 34), (8, 30, 26), TEAL + (255,), 20, 8), x0 + w - 56, y + 60, ra, "r", back_out((t - done[i]) / 0.3))
        elif t >= T_SEND:
            k = clamp((t - T_SEND - i * 0.12) / (done[i] - T_SEND - i * 0.12))
            d.rounded_rectangle((x0 + w - 300, y + 50, x0 + w - 60, y + 70), 10, fill=(40, 48, 74, int(255 * ra)))
            d.rounded_rectangle((x0 + w - 300, y + 50, x0 + w - 300 + 240 * k, y + 70), 10, fill=TEAL + (int(255 * ra),))
        else:
            place(c, pill("Eksik", font(DB, 34), WHITE, CORAL + (255,), 20, 8), x0 + w - 56, y + 60, ra, "r")
        ct = T_PAN + 1.4 + i * 0.75
        if t >= ct:
            v = t - ct
            ca = clamp(v / 0.2) * ra
            place(c, text_img("Kategori", font(IM, 28), GREY), x0 + 120, y + 128, ca, "l")
            chip = pill(cat, font(DS, 32), WHITE, (48, 56, 90, 255), 18, 8)
            place(c, chip, x0 + 240, y + 128, ca, "l", back_out(v / 0.3))
            if v > 0.35:
                place(c, text_img("eşleşti ✓", font(DB, 32), TEAL), x0 + 240 + chip.size[0] + 18, y + 128, clamp((v - 0.35) / 0.15) * ra, "l")
            place(c, text_img("Özellikler, varyantlar tamam", font(IM, 28), GREY), x0 + 120, y + 186, clamp((v - 0.5) / 0.2) * ra, "l")
    # buton + imleç
    by = y0 + 1180
    ba = clamp((u - 2.0) / 0.25) * a
    pressed = T_SEND <= t < T_SEND + 0.18
    bw = 640
    d.rounded_rectangle((W / 2 - bw / 2, by, W / 2 + bw / 2, by + 130), 65, fill=(TEAL if t >= T_SEND else INDIGO) + (int(255 * ba),))
    place(c, native_text("Eksikleri Dağıt", 64, WHITE), W / 2, by + 65, ba, "c", 0.96 if pressed else 1)
    if T_SEND - 1.0 <= t < T_SEND + 0.8:
        k = ease_io((t - T_SEND + 1.0) / 0.9)
        draw_cursor(c, lerp(900, W / 2 + 120, k), lerp(1820, by + 80, k), a, t - T_SEND)
    place(c, text_img("Tek tuş: web siten + tüm pazaryerleri", font(DB, 38), (205, 210, 232)), W / 2, by + 200, ba, "c")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    place(c, native_text("Olmadığın", 150, WHITE), W / 2, 760, a, "c", lerp(1.5, 1, ease_out((t - T_S) / 0.18)))
    wa = clamp((t - T_S - 0.45) / 0.1) * a
    place(c, native_text("vitrinde", 150, WHITE), W / 2, 920, wa, "c", lerp(1.5, 1, ease_out((t - T_S - 0.45) / 0.18)))
    wb = clamp((t - T_S - 0.9) / 0.1) * a
    place(c, native_text("satamazsın.", 150, GOLD), W / 2, 1090, wb, "c", lerp(1.5, 1, ease_out((t - T_S - 0.9) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Web siten + 8 pazaryeri", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("Bir kez yükle, her vitrinde sat", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Senin ürünün", 80, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("kaç vitrinde?", GOLD), ("emo", "👇")], 80, GOLD), W / 2, 1025, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (CORAL if t < T_PAN else TEAL, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_ANS, T_MISS, T_PAN, T_SEND, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_quiz(c, t); s_panel(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [T_ANS, T_ANS + 0.5, T_MISS + 0.6, T_SEND, T_S, T_S + 0.45, T_S + 0.9]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.6), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, tiles=[1.3 + k * 0.22 for k in range(8)], cd=T_CD, ans=T_ANS, miss=T_MISS, pan=T_PAN,
                              cats=[T_PAN + 1.4 + i * 0.75 for i in range(3)], send=T_SEND, done=[T_SEND + 0.5 + i * 0.35 for i in range(3)],
                              s=T_S, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
