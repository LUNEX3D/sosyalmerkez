"""Dashtock "11.11 gecesi 300 sipariş. Faturaları kim kesecek?" ~27 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: otomatik e-Fatura / e-Arşiv (alıcıya göre tür seçimi, pazaryerine yükleme, iadede otomatik iptal), web sitesi + pazaryerleri.
Akış: "11.11'e 5 gün." + sipariş yağmuru, sayaç 300 -> "Hepsine fatura lazım." -> "Fatura başına 1 dk. Ne zaman biter?"
A 2 saat / B 5 saat / C Hiç kesmem + 3-2-1 -> "Elle: 5 saat." -> "Doğru cevap: C" -> Otomatik Fatura paneli (satırlar
Bekliyor -> e-Arşiv/e-Fatura ✓ + Yüklendi ✓, sayaç 0->300, iade -> e-Arşiv iptal) -> "Sen sat. Faturayı Dashtock kessin."
-> logo + yorum sorusu, döngü. Tüm sayılar ÖRNEK.
Kullanım: python3 render_fatura.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 27.0
T_RAIN = 0.5    # siparişler düşmeye başlar
T_NEED = 2.9    # "Hepsine fatura lazım."
T_Q = 4.6       # soru
T_CD = 6.8      # geri sayım
T_ANS = 9.4     # "Elle: 5 saat."
T_C = 11.0      # "Doğru cevap: C"
T_PAN = 13.4    # panel
T_IADE = 17.6   # iade satırı
T_S = 19.9; T_S2 = 20.6
T_END = 22.4
T_LOOP = DUR - 0.3

CH = [("Web siten", TEAL), ("Trendyol", CORAL), ("Hepsiburada", AMBER), ("N11", PURPLE), ("ÇiçekSepeti", PINK), ("Amazon", BLUE), ("Pazarama", GREEN)]
random.seed(11)
RAIN = [(T_RAIN + i * 0.075, random.choice(CH), random.uniform(110, 970), 10000 + random.randint(100, 999) * 7) for i in range(30)]

def order_chip(name, col, no):
    def mk():
        f1 = font(DB, 34); f2 = font(IM, 28)
        w = int(max(tlen(name, f1), tlen(f"Sipariş #{no}", f2))) + 120
        im = Image.new("RGBA", (w, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, 109), 24, fill=CARD2 + (245,), outline=col + (255,), width=3)
        d.ellipse((22, 33, 66, 77), fill=col + (255,))
        d.text((84, 14), name, font=f1, fill=WHITE); d.text((84, 60), f"Sipariş #{no}", font=f2, fill=GREY)
        return im
    return tc(("oc", name, no), mk)

def count_at(t):
    if t < T_RAIN: return 0
    return int(300 * ease_out((t - T_RAIN) / 2.3))

def s_intro(c, t):
    a = 1 - clamp((t - T_Q) / 0.12)
    if a <= 0.01: return
    # sipariş yağmuru
    for (t0, (nm, col), x, no) in RAIN:
        u = t - t0
        if u < 0: continue
        y = -80 + u * 1500
        if y > 2000: continue
        place(c, order_chip(nm, col, no), x, y, a * 0.92, "c")
    place(c, native_text("11.11'e 5 gün.", 112, GOLD), W / 2, 190, a, "c", lerp(1.35, 1, ease_out(t / 0.25)))
    # sayaç
    ca = clamp((t - T_RAIN) / 0.15) * a
    n = count_at(t)
    put_card(c, 140, 330, 800, 300, None, ca, CARD, 0, 40)
    place(c, text_img("Gece gelen sipariş", font(DB, 44), GREY), W / 2, 395, ca, "c")
    place(c, native_text(str(n), 170, WHITE), W / 2, 530, ca, "c", 1 + 0.08 * math.sin(t * 30) * (n < 300))
    place(c, pill("ÖRNEK", font(IB, 26), (30, 22, 4), GOLD + (255,), 14, 4), 920, 360, ca, "r")
    if t > T_NEED:
        u = t - T_NEED
        put_card(c, 90, 1280, 900, 330, CORAL, clamp(u / 0.12) * a, CARD, 0.35, 40)
        place(c, native_text("Hepsine", 96, WHITE), W / 2, 1380, clamp(u / 0.1) * a, "c", back_out(u / 0.3))
        place(c, native_text("fatura lazım.", 106, CORAL), W / 2, 1500, clamp((u - 0.2) / 0.1) * a, "c", back_out((u - 0.2) / 0.3))

def s_quiz(c, t):
    if t < T_Q or t > T_PAN: return
    a = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_PAN + 0.15) / 0.15))
    u = t - T_Q
    if t < T_ANS:
        place(c, native_text("Fatura başına 1 dk.", 92, WHITE), W / 2, 220, a, "c", back_out(u / 0.3))
        place(c, native_text("Ne zaman biter?", 110, GOLD), W / 2, 350, clamp((u - 0.25) / 0.1) * a, "c", back_out((u - 0.25) / 0.3))
        place(c, text_img("300 sipariş · 300 fatura · ÖRNEK", font(DB, 40), GREY), W / 2, 460, clamp((u - 0.4) / 0.2) * a, "c")
    elif t < T_C:
        v = t - T_ANS
        place(c, native_text("Elle:", 96, WHITE), W / 2, 220, a, "c", back_out(v / 0.3))
        place(c, native_text("5 saat.", 150, CORAL), W / 2, 370, clamp((v - 0.3) / 0.1) * a, "c", lerp(1.6, 1, ease_out((v - 0.3) / 0.2)))
    else:
        v = t - T_C
        place(c, native_text("Doğru cevap: C", 104, TEAL), W / 2, 220, a, "c", lerp(1.5, 1, ease_out(v / 0.2)))
        place(c, native_text("Faturayı sen kesmezsin.", 76, WHITE), W / 2, 350, clamp((v - 0.4) / 0.1) * a, "c", back_out((v - 0.4) / 0.3))
    opts = (("A", "2 saat"), ("B", "5 saat"), ("C", "Hiç kesmem"))
    for i, (ch, txt) in enumerate(opts):
        oa = clamp((u - 0.5 - i * 0.15) / 0.15) * a
        y = 640 + i * 270
        hl = None
        if t >= T_ANS and i == 1 and t < T_C: hl = CORAL
        if t >= T_C and i == 2: hl = TEAL
        dim = (t >= T_ANS and hl is None)
        oa2 = oa * (0.35 if dim else 1)
        put_card(c, 110, y, 860, 220, hl, oa2, CARD2, 0.4 if hl else 0, 34)
        place(c, letter_badge(ch, (INDIGO, BLUE, PURPLE)[i], 120), 200, y + 110, oa2, "c", back_out((u - 0.5 - i * 0.15) / 0.3))
        place(c, native_text(txt, 80, WHITE), 290, y + 110, oa2, "l")
        if hl and t >= T_ANS:
            ic = icon_circle("check" if hl == TEAL else "warn", 80, hl)
            ts = T_C if hl == TEAL else T_ANS
            place(c, ic, 910, y + 110, oa, "c", back_out((t - ts) / 0.3))
    if T_ANS <= t < T_C:
        # saat: 21:00 -> 02:00
        v = clamp((t - T_ANS - 0.3) / 1.2)
        hh = 21 + int(5 * ease_io(v)); mm = int((5 * ease_io(v) * 60) % 60)
        place(c, text_img(f"21:00  →  {hh % 24:02d}:{mm:02d}", font(DX, 70), CORAL), W / 2, 1520, a, "c")
        place(c, text_img("300 dakika elle fatura", font(DB, 40), GREY), W / 2, 1610, a, "c")
    if T_CD <= t < T_ANS:
        seg = (T_ANS - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text(str(max(1, n)), 160, GOLD), W / 2, 1560, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))
    if t >= T_C:
        v = t - T_C
        place(c, text_img("Sipariş gelir, fatura kendi kesilir.", font(DB, 44), (205, 210, 232)), W / 2, 1560, clamp((v - 0.8) / 0.2) * a, "c")

ROWS = [("Web siten", TEAL, "e-Arşiv"), ("Trendyol", CORAL, "e-Arşiv"), ("Hepsiburada", AMBER, "e-Fatura"),
        ("N11", PURPLE, "e-Arşiv"), ("ÇiçekSepeti", PINK, "e-Arşiv"), ("Amazon", BLUE, "e-Fatura")]

def s_panel(c, t):
    a = clamp((t - T_PAN) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_PAN
    place(c, native_text("Sipariş gelir.", 96, WHITE), W / 2, 170, a, "c", back_out(u / 0.3))
    place(c, native_text("Fatura kesilir.", 96, TEAL), W / 2, 285, clamp((u - 0.25) / 0.1) * a, "c", back_out((u - 0.25) / 0.3))
    x0, y0, w = 50, 390, 980
    put_card(c, x0, y0, w, 1400, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Otomatik Fatura", font(DB, 46)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    # sayaç
    k = clamp((u - 0.4) / 3.4)
    n = int(300 * ease_io(k))
    place(c, text_img("Kesilen fatura", font(DS, 38), GREY), x0 + 40, y0 + 160, a, "l")
    place(c, native_text(f"{n} / 300", 80, TEAL if n == 300 else WHITE), x0 + w - 40, y0 + 160, a, "r")
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((x0 + 40, y0 + 220, x0 + w - 40, y0 + 240), 10, fill=(40, 48, 74, int(255 * a)))
    if n > 0:
        d.rounded_rectangle((x0 + 40, y0 + 220, x0 + 40 + (w - 80) * n / 300, y0 + 240), 10, fill=TEAL + (int(255 * a),))
    # satırlar
    for i, (nm, col, typ) in enumerate(ROWS):
        y = y0 + 290 + i * 150
        ra = clamp((u - 0.3 - i * 0.12) / 0.2) * a
        if ra <= 0.01: continue
        done_t = T_PAN + 0.9 + i * 0.45
        iade = (i == 1 and t >= T_IADE)
        fill = (90, 28, 30) if iade else CARD2
        d.rounded_rectangle((x0 + 30, y, x0 + w - 30, y + 128), 22, fill=fill + (int(235 * ra),), outline=(CORAL if iade else col) + (int(160 * ra),), width=3)
        d.ellipse((x0 + 58, y + 44, x0 + 98, y + 84), fill=col + (int(255 * ra),))
        place(c, text_img(nm, font(DB, 38)), x0 + 120, y + 42, ra, "l")
        place(c, text_img(f"Sipariş #{10482 + i * 37}", font(IM, 28), GREY), x0 + 120, y + 88, ra, "l")
        if iade:
            v = t - T_IADE
            place(c, pill("İade → e-Arşiv iptal ✓", font(DB, 34), WHITE, CORAL + (255,), 20, 8), x0 + w - 50, y + 64, ra, "r", back_out(v / 0.3))
        elif t < done_t:
            place(c, pill("Bekliyor", font(DB, 34), GREY, (40, 48, 74, 255), 20, 8), x0 + w - 50, y + 64, ra, "r")
        else:
            v = t - done_t
            place(c, pill(f"{typ} ✓", font(DB, 34), (8, 30, 26), TEAL + (255,), 20, 8), x0 + w - 270, y + 64, ra, "r", back_out(v / 0.3))
            if v > 0.25:
                place(c, pill("Yüklendi ✓" if nm != "Web siten" else "Gönderildi ✓", font(DB, 30), WHITE, (48, 56, 90, 255), 16, 8),
                      x0 + w - 50, y + 64, ra * clamp((v - 0.25) / 0.15), "r")
    # alt not
    na = clamp((u - 2.5) / 0.3) * a
    place(c, text_img("Alıcı mükellefse e-Fatura, değilse e-Arşiv", font(DB, 38), (205, 210, 232)), W / 2, y0 + 1275, na, "c")
    place(c, text_img("Pazaryerine otomatik yüklenir", font(IM, 34), GREY), W / 2, y0 + 1330, na, "c")
    if t >= T_IADE:
        place(c, text_img("İade onaylanınca fatura iptali de otomatik", font(DB, 36), CORAL), W / 2, y0 + 1215, clamp((t - T_IADE - 0.3) / 0.2) * a, "c")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    place(c, native_text("Sen sat.", 170, WHITE), W / 2, 760, a, "c", lerp(1.5, 1, ease_out((t - T_S) / 0.18)))
    wa = clamp((t - T_S2) / 0.1) * a
    place(c, native_text("Faturayı", 120, TEAL), W / 2, 960, wa, "c", lerp(1.5, 1, ease_out((t - T_S2) / 0.18)))
    place(c, native_text("Dashtock kessin.", 120, TEAL), W / 2, 1100, clamp((t - T_S2 - 0.15) / 0.1) * a, "c", lerp(1.5, 1, ease_out((t - T_S2 - 0.15) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Web siten + 8 pazaryeri", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("Sipariş · fatura · kargo tek panelde", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("11.11'de faturaları", 76, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("kim kesecek?", GOLD), ("emo", "👇")], 76, GOLD), W / 2, 1020, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (CORAL if t < T_C else TEAL, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_Q, T_ANS, T_C, T_PAN, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_intro(c, t); s_quiz(c, t); s_panel(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [T_NEED, T_NEED + 0.2, T_ANS + 0.3, T_C, T_IADE, T_S, T_S2]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.6), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, rain=[r[0] for r in RAIN], need=T_NEED, q=T_Q, cd=T_CD, ans=T_ANS, c=T_C, pan=T_PAN,
                              rows=[T_PAN + 0.9 + i * 0.45 for i in range(len(ROWS))], iade=T_IADE, s=T_S, s2=T_S2, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
