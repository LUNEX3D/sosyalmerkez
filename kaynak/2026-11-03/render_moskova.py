"""Dashtock "Bu etiketi okuyabilir misin?" ~18 sn dikey kısa, sessiz izlemeye göre (müzik + yazı).
Konu: yurt dışı pazaryeri (Ozon) + merkezi stok + paket etiketi, web siten + pazaryerlerin tek panelde.
Akış: Kiril etiket + kanca -> "Bu sipariş nereden geldi?" A İzmir / B Bakü / C Moskova -> Moskova -> panelde Trendyol,
web siten, Hepsiburada siparişlerinin altında Ozon siparişi, stok tek havuzdan düşer, paket etiketi yazdırılır
-> "Dükkânın İstanbul'da. Vitrinin dünyada." -> logo + yorum sorusu, döngü.
Kullanım: python3 render_moskova.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess
sys.path.insert(0, "/home/user/is")
from yardimci import *
from PIL import Image, ImageDraw

DUR = 18.2
T_Q = 2.7
T_ANS = T_Q + 2.6          # 5.3
T_PAN = T_ANS + 1.9        # 7.2
T_ROW = T_PAN + 0.9        # Ozon satırı kayar
T_STK = T_ROW + 1.0        # stok düşer
T_CLK = T_STK + 1.0        # etiket yazdır
T_S = T_CLK + 1.5          # slogan
T_S2 = T_S + 0.9
T_END = T_S + 2.6
T_LOOP = DUR - 0.3

TY = (242, 122, 32); HB = (250, 85, 45); OZ = (40, 110, 245); WEB = TEAL
INK = (24, 26, 34)

def shipping_label(w=760, h=520, stamp=True):
    def mk():
        s = 2; S = (w * s, h * s)
        im = Image.new("RGBA", S, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, S[0] - 1, S[1] - 1), 18 * s, fill=(250, 248, 240, 255))
        d.rectangle((0, 0, S[0], 86 * s), fill=(30, 32, 44, 255))
        d.rounded_rectangle((0, 0, S[0] - 1, 40 * s), 18 * s, fill=(30, 32, 44, 255))
        d.text((32 * s, 18 * s), "ОТПРАВЛЕНИЕ FBS", font=font(DX, 46 * s), fill=(255, 255, 255))
        y = 116
        for txt, f, col in (("ПОЛУЧАТЕЛЬ:", font(IB, 28 * s), (110, 112, 125)),
                            ("г. Москва", font(DX, 64 * s), INK),
                            ("Россия · 101000", font(DS, 34 * s), INK),
                            ("ЗАКАЗ № 0001-ÖRNEK", font(IB, 30 * s), (90, 92, 105))):
            d.text((32 * s, y * s), txt, font=f, fill=col)
            y += {28: 44, 64: 86, 34: 56, 30: 50}[f.size // s]
        # barkod
        import random as _r
        rg = _r.Random(3); x = 32
        while x < w - 40:
            bw = rg.choice((3, 4, 6, 8)); d.rectangle((x * s, 372 * s, (x + bw) * s, 470 * s), fill=INK); x += bw + rg.choice((3, 5, 7))
        if stamp:
            st = Image.new("RGBA", (300 * s, 90 * s), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((4, 4, 300 * s - 5, 90 * s - 5), 12 * s, outline=(220, 50, 50, 220), width=6 * s)
            b = sd.textbbox((0, 0), "ÖRNEK", font=font(DX, 54 * s))
            sd.text(((300 * s - b[2]) / 2, (90 * s - b[3]) / 2 - 4), "ÖRNEK", font=font(DX, 54 * s), fill=(220, 50, 50, 220))
            st = st.rotate(14, expand=True, resample=Image.BICUBIC)
            im.alpha_composite(st, (S[0] - st.size[0] - 24 * s, 110 * s))
        im = im.resize((w, h), Image.LANCZOS)
        # gölge
        pd = 40; out = Image.new("RGBA", (w + pd * 2, h + pd * 2), (0, 0, 0, 0))
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((pd, pd + 16, pd + w, pd + h + 16), 18, fill=(0, 0, 0, 170))
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); out.alpha_composite(im, (pd, pd))
        return out
    return tc(("label", w, h, stamp), mk)

from PIL import ImageFilter

def badge(ch, col, size=64):
    return letter_badge(ch, col, size)

def s1(c, t):  # kanca: etiket + soru
    a = 1 - clamp((t - T_Q) / 0.2)
    if a <= 0.01: return
    place(c, native_text("Bu etiketi", 128, WHITE), W / 2, 330, a, "c", lerp(1.3, 1, ease_out(t / 0.25)))
    place(c, native_text("okuyabilir misin?", 112, GOLD), W / 2, 480, clamp((t - 0.25) / 0.1) * a, "c", lerp(1.3, 1, ease_out((t - 0.25) / 0.25)))
    lb = shipping_label().rotate(-6 + 2 * math.sin(t * 1.4), expand=True, resample=Image.BICUBIC)
    sc = lerp(1.25, 1.0, ease_out((t - 0.1) / 0.5)) * (1 + 0.012 * math.sin(t * 3))
    place(c, lb, W / 2, 1120, clamp(t / 0.15) * a, "c", sc)
    if t > 1.2:
        place(c, pill("3 saniye…", font(IB, 36), (30, 22, 4), GOLD + (255,), 24, 8), W / 2, 1640, clamp((t - 1.2) / 0.15) * a, "c")

def quiz(c, t):
    a = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_PAN) / 0.15))
    if a <= 0.01: return
    # küçük etiket üstte
    place(c, shipping_label().rotate(-4, expand=True, resample=Image.BICUBIC), W / 2, 360, a, "c", 0.52)
    qa = a * (1 - clamp((t - T_ANS - 0.6) / 0.2))
    place(c, native_text("Bu sipariş", 104, WHITE), W / 2, 640, qa, "c", back_out((t - T_Q) / 0.3))
    place(c, native_text("nereden geldi?", 104, WHITE), W / 2, 765, qa, "c", back_out((t - T_Q) / 0.3))
    for i, (lt, v) in enumerate((("A", "İzmir"), ("B", "Bakü"), ("C", "Moskova"))):
        ia = clamp((t - T_Q - 0.3 - i * 0.12) / 0.15) * a
        win = i == 2 and t >= T_ANS; lose = i != 2 and t >= T_ANS
        y = 900 + i * 220
        col = GREEN if win else ((70, 76, 100) if lose else INDIGO)
        k = 0.4 if lose else 1
        put_card(c, 150, y, 780, 180, col, ia * k, CARD, 0.6 if win else 0.2, 40)
        place(c, letter_badge(lt, col, 104), 190, y + 90, ia * k, "l")
        sc = (1 + 0.16 * math.exp(-(t - T_ANS) * 7)) if win else 1
        place(c, native_text(v, 104, WHITE), 555, y + 90, ia * k, "c", sc)
        if win: place(c, icon_circle("check", 80, GREEN), 880, y + 90, ia, "c", back_out((t - T_ANS) / 0.3))
    if T_Q + 0.6 < t < T_ANS:
        n = 3 - int((t - T_Q - 0.6) / ((T_ANS - T_Q - 0.6) / 3))
        place(c, native_text(str(max(1, n)), 96, GOLD), W / 2, 1640, a, "c", 1 + 0.15 * math.exp(-((t - T_Q - 0.6) % ((T_ANS - T_Q - 0.6) / 3)) * 8))
    if t >= T_ANS + 0.5:
        b = clamp((t - T_ANS - 0.5) / 0.12) * a
        place(c, native_text("Ozon'dan geldi.", 96, WHITE), W / 2, 680, b, "c", back_out((t - T_ANS - 0.5) / 0.3))
        place(c, text_img("Rusya'nın büyük pazaryerlerinden biri", font(DS, 44), (200, 205, 230)), W / 2, 1640, b, "c")

ROWS = [("T", TY, "Trendyol", "İstanbul"), ("W", WEB, "Web siten", "Ankara"), ("H", HB, "Hepsiburada", "İzmir"), ("O", OZ, "Ozon", "Moskova")]
def panel(c, t):
    a = clamp((t - T_PAN) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    top = native_text("Trendyol siparişinin", 84, WHITE) if t < T_STK else native_text("Stok tek havuzdan", 84, WHITE)
    bot = native_text("hemen altında.", 84, TEAL) if t < T_STK else native_text("düştü.", 84, TEAL)
    if t >= T_CLK + 0.2:
        top = native_text("Etiket de", 84, WHITE); bot = native_text("aynı panelden.", 84, TEAL)
    place(c, top, W / 2, 220, a, "c"); place(c, bot, W / 2, 325, a, "c")
    x0, y0, w = 90, 430, 900
    put_card(c, x0, y0, w, 1080, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Siparişler", font(DB, 46)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    d = ImageDraw.Draw(c)
    for i, (ch, col, nm, city) in enumerate(ROWS):
        y = y0 + 130 + i * 112
        if i < 3:
            ra = clamp((t - T_PAN - 0.1 - i * 0.07) / 0.15) * a; dx = 0
        else:
            u = (t - T_ROW) / 0.35; ra = clamp(u * 2) * a; dx = (1 - ease_out(u)) * 500
            hl = clamp((t - T_ROW) / 0.2)
            d.rounded_rectangle((x0 + 16 + dx, y - 6, x0 + w - 16 + dx, y + 96), 22, fill=(30, 50, 110, int(255 * ra * hl)),
                                outline=OZ + (int(255 * ra * hl),), width=4)
        place(c, badge(ch, col, 64), x0 + 36 + dx, y + 45, ra, "l")
        place(c, text_img(nm, font(DB, 42)), x0 + 124 + dx, y + 26, ra, "l")
        place(c, text_img("Seramik kupa · 1 adet", font(IM, 28), GREY), x0 + 124 + dx, y + 68, ra, "l")
        place(c, pill(city, font(IB, 32), WHITE, ((50, 58, 90) if i < 3 else OZ) + (255,), 18, 6), x0 + w - 36 + dx, y + 45, ra, "r",
              (1 + 0.2 * math.exp(-max(0, t - T_ROW - 0.3) * 8)) if i == 3 else 1)
    # stok kutusu
    sy = y0 + 600
    sa = clamp((t - T_STK + 0.3) / 0.2) * a
    put_card(c, x0 + 30, sy, w - 60, 180, TEAL if t >= T_STK else None, sa, CARD2, 0.3 if t >= T_STK else 0, 28)
    place(c, text_img("Merkezi stok · Seramik kupa", font(IS, 32), GREY), x0 + 70, sy + 50, sa, "l")
    n = "8" if t < T_STK else "7"
    place(c, native_text(n, 92, TEAL if t >= T_STK else WHITE), x0 + 70, sy + 122, sa, "l", 1 + 0.25 * math.exp(-max(0, t - T_STK) * 7) * (t >= T_STK))
    chans = "Web siten · Trendyol · Hepsiburada · Ozon · AliExpress"
    place(c, text_img("adet → tüm kanallarda", font(DB, 36), WHITE), x0 + 160, sy + 112, sa, "l")
    place(c, text_img(chans, font(IM, 26), DIM), x0 + 160, sy + 152, sa, "l")
    # etiket butonu
    by = y0 + 900
    ba = clamp((t - T_CLK + 0.6) / 0.2) * a
    clicked = t >= T_CLK
    place(c, pill("Etiket hazır ✓" if clicked else "Paket etiketi yazdır", font(DX, 42), WHITE, (GREEN if clicked else INDIGO) + (255,), 36, 16),
          W / 2, by, ba, "c", 1 + 0.12 * math.exp(-max(0, t - T_CLK) * 8) * clicked)
    draw_cursor(c, W / 2 + 120 + 8 * math.sin(t * 3), by + 18, ba, (t - T_CLK) / 0.35 if 0 <= t - T_CLK <= 0.35 else -1)
    if clicked:
        u = (t - T_CLK - 0.15) / 0.5
        place(c, shipping_label().rotate(5, expand=True, resample=Image.BICUBIC), W / 2 + 180, lerp(1900, 1500, ease_out(u)), clamp(u * 3) * a, "c", 0.5)

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    for w_, col, ti, y in (("Dükkânın", WHITE, T_S, 720), ("İstanbul'da.", WHITE, T_S, 860), ("Vitrinin", TEAL, T_S2, 1080), ("dünyada.", TEAL, T_S2, 1220)):
        wa = clamp((t - ti) / 0.1) * a
        place(c, native_text(w_, 140, col), W / 2, y, wa, "c", lerp(1.5, 1, ease_out((t - ti) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 480, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Web siten + 8 pazaryeri", font(DB, 56), WHITE), W / 2, 660, la, "c")
    place(c, text_img("Türkiye'den Moskova'ya, tek panel", font(DB, 50), (205, 210, 232)), W / 2, 735, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("En uzak siparişin", 76, GOLD), W / 2, 930, ra, "c")
    place(c, rich([("nereden geldi?", GOLD), ("emo", "👇")], 76, GOLD), W / 2, 1030, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (BLUE, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.7, "c")

FLASH = (0.0, T_Q, T_ANS, T_PAN, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s1(c, t); quiz(c, t); panel(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in (T_ANS, T_ROW, T_STK, T_S, T_S2):
        if 0 <= t - x < 0.25: sh += 10 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.4), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, q=T_Q, ans=T_ANS, pan=T_PAN, row=T_ROW, stk=T_STK, clk=T_CLK, s=T_S, s2=T_S2, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
