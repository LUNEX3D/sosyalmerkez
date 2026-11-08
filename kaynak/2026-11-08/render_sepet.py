"""Dashtock "11.11'e 3 gün. 10 kişi sepete ekledi. Kaçı ödedi?" ~29.8 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: kendi web siten + terk edilmiş sepet otomasyonu (Pazarlama > Otomasyon: terk edilmiş sepet e-postası).
Akış: kanca + 10 sepet + A/B/C -> 3-2-1 -> "3 ödedi. 7 sepet terk edildi." -> "Sepet hâlâ dolu." telefon kilit ekranına
hatırlatma e-postası -> panel: sepet terk edildi -> e-posta -> müşteri döndü, siparişler listesine düşer ->
"Sepet bırakıldı. Satış bitmedi." -> logo + yorum sorusu, döngü. Tüm veriler ÖRNEK, arayüz çizim.
Kullanım: python3 render_sepet.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 29.8
T_OPT = 3.0     # şıklar
T_CD = 6.2      # geri sayım
T_ANS = 8.8     # cevap
T_BACK = 13.0   # telefon + e-posta
T_TAP = 15.6
T_PAN = 17.9    # panel
T_S = 22.4      # slogan
T_END = 24.9
T_LOOP = DUR - 0.3

PAID = {1, 4, 8}            # ödeyen 3 sepet
BACK = [2, 6]               # e-postayla geri dönen 2 sepet (panel sahnesinde)
ORD_T = [T_PAN + 2.2, T_PAN + 3.0]

def cart(size, col, full=True):
    def mk():
        s = 4; S = size * s; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        w = int(S * 0.07)
        if full:
            d.rounded_rectangle((S * .32, S * .22, S * .52, S * .44), S // 30, fill=CORAL + (255,))
            d.rounded_rectangle((S * .48, S * .28, S * .7, S * .44), S // 30, fill=AMBER + (255,))
            d.ellipse((S * .4, S * .3, S * .56, S * .44), fill=TEAL + (255,))
        d.line([(S * .08, S * .2), (S * .2, S * .2), (S * .3, S * .62), (S * .78, S * .62), (S * .86, S * .32), (S * .24, S * .32)], fill=col + (255,), width=w, joint="curve")
        for x in (.36, .72):
            d.ellipse((S * x - S * .06, S * .72, S * x + S * .06, S * .84), fill=col + (255,))
        return im.resize((size, size), Image.LANCZOS)
    return tc(("cart", size, col, full), mk)

def cust_card(i, state, w=176, h=200):
    """state: wait / paid / gone"""
    def mk():
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        oc = {"wait": (70, 80, 120), "paid": TEAL, "gone": CORAL}[state]
        d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=CARD2 + (250,), outline=oc + (255,), width=4)
        im.alpha_composite(cart(110, WHITE if state != "gone" else DIM, True), ((w - 110) // 2, 14))
        lab, col = {"wait": (f"Müşteri {i + 1}", GREY), "paid": ("Ödedi", TEAL), "gone": ("Gitti", CORAL)}[state]
        t = text_img(lab, font(DB, 32), col); im.alpha_composite(t, ((w - t.size[0]) // 2, 140))
        return im
    return tc(("cc", i, state, w, h), mk)

def cpos(i): return 108 + (i % 5) * 216, 760 + (i // 5) * 236

def opt(letter, val, col, hl=0):
    def mk():
        w, h = 270, 120
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=CARD + (245,), outline=(TEAL if hl else (60, 70, 110)) + (255,), width=5 if hl else 3)
        im.alpha_composite(letter_badge(letter, col, 76), (20, 22))
        t = native_text(val, 72, TEAL if hl else WHITE); im.alpha_composite(t, (128, (h - t.size[1]) // 2))
        return im
    return tc(("opt", letter, val, col, hl), mk)
OPTS = [("A", "9", INDIGO), ("B", "6", AMBER), ("C", "3", PINK)]

def s_quiz(c, t):
    a = 1 - clamp((t - T_BACK + 0.15) / 0.15)
    if a <= 0.01: return
    if t < T_ANS:
        place(c, native_text("11.11'e 3 gün.", 108, GOLD), W / 2, 170, a, "c", lerp(1.35, 1, ease_out(t / 0.25)))
        place(c, native_text("Sitende 10 kişi", 86, WHITE), W / 2, 300, clamp((t - 0.4) / 0.1) * a, "c", back_out((t - 0.4) / 0.3))
        place(c, native_text("sepete ürün attı.", 86, WHITE), W / 2, 400, clamp((t - 0.6) / 0.1) * a, "c", back_out((t - 0.6) / 0.3))
        place(c, native_text("Kaçı ödedi?", 120, CORAL), W / 2, 545, clamp((t - 1.0) / 0.1) * a, "c", lerp(1.5, 1, ease_out((t - 1.0) / 0.2)))
    else:
        v = t - T_ANS
        place(c, native_text("3 kişi ödedi.", 120, TEAL), W / 2, 230, a, "c", lerp(1.6, 1, ease_out(v / 0.2)))
        place(c, native_text("7 sepet", 110, CORAL), W / 2, 385, clamp((v - 0.6) / 0.1) * a, "c", lerp(1.6, 1, ease_out((v - 0.6) / 0.2)))
        place(c, native_text("terk edildi.", 110, CORAL), W / 2, 515, clamp((v - 0.8) / 0.1) * a, "c", lerp(1.6, 1, ease_out((v - 0.8) / 0.2)))
    place(c, pill("ÖRNEK", font(IB, 26), (30, 22, 4), GOLD + (255,), 14, 4), 1030, 650, clamp((t - 1.2) / 0.2) * a, "r")
    for k in range(10):
        t0 = 1.2 + k * 0.12
        ta = clamp((t - t0) / 0.1) * a
        if ta <= 0.01: continue
        st = "wait"
        if t >= T_ANS: st = "paid" if k in PAID else "gone"
        x, y = cpos(k)
        sc = back_out((t - t0) / 0.3)
        if st == "gone":
            g = clamp((t - T_ANS - 0.6) / 0.4)
            ta *= 1 - 0.4 * g; y += 14 * g
        if st == "paid": sc *= 1 + 0.12 * math.exp(-(t - T_ANS) * 8)
        place(c, cust_card(k, st), x, y + 100, ta, "c", sc)
    # şıklar
    for i, (L, val, col) in enumerate(OPTS):
        t0 = T_OPT + i * 0.2
        oa = clamp((t - t0) / 0.12) * a
        if oa <= 0.01: continue
        hl = 1 if (t >= T_ANS and L == "C") else 0
        dim = 0.35 if (t >= T_ANS and not hl) else 1
        place(c, opt(L, val, col, hl), 200 + i * 340, 1330, oa * dim, "c", back_out((t - t0) / 0.3) * (1 + 0.1 * hl * math.exp(-(t - T_ANS) * 6)))
    if T_CD <= t < T_ANS:
        seg = (T_ANS - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text("Tahmin et!", 80, WHITE), W / 2, 1560, 1, "c")
        place(c, native_text(str(max(1, n)), 160, GOLD), W / 2, 1720, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))
    elif t < T_CD:
        place(c, text_img("Kendi web sitende, 11.11 haftası.", font(DB, 44), (205, 210, 232)), W / 2, 1560, clamp((t - 3.6) / 0.3) * a, "c")
    else:
        v = t - T_ANS
        place(c, text_img("Ürünü sepete attı, ödemeden çıktı.", font(DB, 44), (205, 210, 232)), W / 2, 1560, clamp((v - 1.3) / 0.3) * a, "c")
        place(c, text_img("Sepet hâlâ dolu duruyor.", font(DB, 44), CORAL), W / 2, 1630, clamp((v - 2.2) / 0.3) * a, "c")

def phone(c, x0, y0, w, h, a):
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((x0 - 14, y0 - 14, x0 + w + 14, y0 + h + 14), 80, fill=(40, 44, 62, int(255 * a)))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 68, fill=(16, 20, 44, int(255 * a)))
    d.rounded_rectangle((x0 + w / 2 - 90, y0 + 22, x0 + w / 2 + 90, y0 + 62), 20, fill=(0, 0, 0, int(255 * a)))

def s_back(c, t):
    a = clamp((t - T_BACK) / 0.15) * (1 - clamp((t - T_PAN + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_BACK
    place(c, native_text("Ama sepet", 96, WHITE), W / 2, 160, a, "c", back_out(u / 0.3))
    place(c, native_text("hâlâ dolu.", 110, GOLD), W / 2, 280, clamp((u - 0.25) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.25) / 0.2)))
    x0, y0, w, h = 210, 420, 660, 1260
    phone(c, x0, y0, w, h, a)
    place(c, text_img("Pazar, 8 Kasım", font(DS, 34), (200, 205, 230)), W / 2, y0 + 140, a, "c")
    place(c, text_img("21:14", font(DX, 150), WHITE), W / 2, y0 + 260, a, "c")
    # bildirim
    na = clamp((u - 0.9) / 0.2) * a
    if na > 0.01:
        ny = lerp(y0 + 300, y0 + 470, ease_out((u - 0.9) / 0.35))
        tap = T_TAP <= t
        d = ImageDraw.Draw(c)
        nx0, nx1 = x0 + 26, x0 + w - 26
        gl = math.exp(-(t - T_TAP) * 3) if tap else 0
        d.rounded_rectangle((nx0, ny, nx1, ny + 380), 34, fill=mixc((44, 50, 80), (60, 70, 110), gl) + (int(250 * na),), outline=(TEAL if tap else (80, 90, 130)) + (int(255 * na),), width=4 if tap else 2)
        place(c, icon_circle("mail", 76, INDIGO), nx0 + 28, ny + 66, na, "l")
        place(c, text_img("Mağazan", font(DB, 38)), nx0 + 122, ny + 48, na, "l")
        place(c, text_img("şimdi", font(IM, 30), GREY), nx1 - 28, ny + 48, na, "r")
        place(c, text_img("e-posta", font(IM, 30), GREY), nx0 + 122, ny + 90, na, "l")
        place(c, text_img("Sepetinde bir şey", font(DB, 46)), nx0 + 28, ny + 170, na, "l")
        place(c, text_img("unuttun", font(DB, 46)), nx0 + 28, ny + 228, na, "l")
        place(c, emoji("🛒", 50), nx0 + 28 + tlen("unuttun", font(DB, 46)) + 22, ny + 228, na, "l")
        place(c, text_img("Spor Ayakkabı seni bekliyor.", font(IM, 34), (210, 215, 238)), nx0 + 28, ny + 288, na, "l")
        place(c, text_img("Kaldığın yerden devam et ›", font(DB, 34), TEAL), nx0 + 28, ny + 338, na, "l")
    place(c, pill("ÖRNEK", font(IB, 26), (30, 22, 4), GOLD + (255,), 14, 4), x0 + w - 40, y0 + 1180, a, "r")
    if T_TAP - 1.0 <= t < T_TAP + 0.9:
        k = ease_io((t - T_TAP + 1.0) / 0.9)
        draw_cursor(c, lerp(900, 700, k), lerp(1760, 1250, k), a, t - T_TAP)
    place(c, text_img("Hatırlatma kendiliğinden gider.", font(DB, 46), (205, 210, 232)), W / 2, 1780, clamp((u - 1.6) / 0.3) * a, "c")

def s_panel(c, t):
    a = clamp((t - T_PAN) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_PAN
    place(c, native_text("Sen bir şey yapmazsın.", 84, WHITE), W / 2, 160, a, "c", back_out(u / 0.3))
    place(c, native_text("Sipariş geri gelir.", 92, TEAL), W / 2, 270, clamp((u - 0.3) / 0.1) * a, "c", back_out((u - 0.3) / 0.3))
    x0, y0, w = 50, 370, 980
    put_card(c, x0, y0, w, 1450, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Pazarlama · Otomasyon", font(DB, 46)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    place(c, text_img("Terk edilmiş sepet", font(DS, 36), GREY), x0 + 40, y0 + 140, a, "l")
    place(c, pill("Açık", font(DB, 30), (8, 30, 26), TEAL + (255,), 18, 6), x0 + w - 40, y0 + 140, a, "r")
    d = ImageDraw.Draw(c)
    steps = [("cart", "Sepet terk edildi", "Müşteri ödemeden çıktı", CORAL),
             ("mail", "Hatırlatma e-postası", "Kendiliğinden gönderilir", INDIGO),
             ("check", "Müşteri geri döndü", "Ödeme tamamlandı", TEAL)]
    for i, (ic, ttl, sub, col) in enumerate(steps):
        y = y0 + 210 + i * 190
        ra = clamp((u - 0.3 - i * 0.35) / 0.2) * a
        if ra <= 0.01: continue
        d.rounded_rectangle((x0 + 30, y, x0 + w - 30, y + 150), 24, fill=CARD2 + (int(235 * ra),), outline=col + (int(170 * ra),), width=3)
        if ic == "cart":
            d.ellipse((x0 + 60, y + 35, x0 + 140, y + 115), fill=col + (int(255 * ra),))
            place(c, cart(60, WHITE, False), x0 + 70, y + 75, ra, "l")
        else:
            place(c, icon_circle(ic, 80, col, (8, 30, 26) if ic == "check" else WHITE), x0 + 60, y + 75, ra, "l")
        place(c, text_img(ttl, font(DB, 42)), x0 + 170, y + 55, ra, "l", back_out((u - 0.3 - i * 0.35) / 0.3))
        place(c, text_img(sub, font(IM, 30), GREY), x0 + 170, y + 105, ra, "l")
        if i < 2:
            ay = y + 150
            d.line((W / 2, ay + 6, W / 2, ay + 34), fill=GREY + (int(200 * ra),), width=4)
            d.polygon([(W / 2 - 10, ay + 30), (W / 2 + 10, ay + 30), (W / 2, ay + 40)], fill=GREY + (int(200 * ra),))
    # sipariş listesi
    ly = y0 + 830
    la = clamp((u - 1.6) / 0.2) * a
    place(c, text_img("Siparişler", font(DB, 40)), x0 + 40, ly, la, "l")
    n = sum(1 for x in ORD_T if t >= x)
    place(c, native_text(f"+{n}", 70, TEAL if n else GREY), x0 + w - 40, ly, la, "r", 1 + 0.2 * max([math.exp(-(t - x) * 9) for x in ORD_T if t >= x] + [0]))
    rows = [("Web siten", "Spor Ayakkabı", "Müşteri 3"), ("Web siten", "Spor Ayakkabı", "Müşteri 7")]
    for i, (ch, pr, cu) in enumerate(rows):
        if t < ORD_T[i]:
            y = ly + 70 + i * 150
            d.rounded_rectangle((x0 + 30, y, x0 + w - 30, y + 130), 22, outline=(60, 70, 110, int(200 * la)), width=2)
            continue
        v = t - ORD_T[i]
        ra = clamp(v / 0.15) * a
        y = ly + 70 + i * 150 + 40 * (1 - ease_out(v / 0.3))
        d.rounded_rectangle((x0 + 30, y, x0 + w - 30, y + 130), 22, fill=CARD2 + (int(240 * ra),), outline=TEAL + (int(200 * ra),), width=3)
        d.ellipse((x0 + 60, y + 45, x0 + 100, y + 85), fill=TEAL + (int(255 * ra),))
        place(c, text_img(f"{ch} · {pr}", font(DB, 38)), x0 + 120, y + 45, ra, "l")
        place(c, text_img(f"{cu} · sepetten döndü", font(IM, 30), GREY), x0 + 120, y + 92, ra, "l")
        place(c, pill("Yeni", font(DB, 30), (8, 30, 26), TEAL + (255,), 18, 6), x0 + w - 60, y + 65, ra, "r", back_out(v / 0.3))
    place(c, text_img("Web siten ve pazaryeri siparişlerin aynı listede.", font(DB, 36), (205, 210, 232)), W / 2, y0 + 1380, clamp((u - 3.4) / 0.3) * a, "c")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    place(c, native_text("Sepet", 160, WHITE), W / 2, 700, a, "c", lerp(1.5, 1, ease_out((t - T_S) / 0.18)))
    place(c, native_text("bırakıldı.", 160, WHITE), W / 2, 870, clamp((t - T_S - 0.3) / 0.1) * a, "c", lerp(1.5, 1, ease_out((t - T_S - 0.3) / 0.18)))
    wb = clamp((t - T_S - 0.9) / 0.1) * a
    place(c, native_text("Satış bitmedi.", 150, GOLD), W / 2, 1090, wb, "c", lerp(1.5, 1, ease_out((t - T_S - 0.9) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Kendi web siten + pazaryerlerin", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("tek panelde", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Senin sitende", 80, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("kaç sepet bekliyor?", GOLD), ("emo", "👇")], 80, GOLD), W / 2, 1025, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (CORAL if t < T_BACK else TEAL, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_ANS, T_BACK, T_PAN, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_quiz(c, t); s_back(c, t); s_panel(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [T_ANS, T_ANS + 0.6, T_BACK + 0.25, T_TAP, T_S, T_S + 0.3, T_S + 0.9]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.6), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, carts=[1.2 + k * 0.12 for k in range(10)], opts=[T_OPT + i * 0.2 for i in range(3)], cd=T_CD, ans=T_ANS,
                              back=T_BACK, notif=T_BACK + 0.9, tap=T_TAP, pan=T_PAN, steps=[T_PAN + 0.3 + i * 0.35 for i in range(3)],
                              orders=ORD_T, s=T_S, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
