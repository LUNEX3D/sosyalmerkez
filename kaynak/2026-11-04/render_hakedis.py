"""Dashtock "Pazaryeri sana eksik ödedi. Bulabilir misin?" ~28 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: hakediş mutabakatı (beklenen / yatan / fark), desi farkı kesintisi ve itiraz takibi.
Akış: hakediş tablosu + kanca -> "Solda beklenen, sağda yatan" + 3-2-1 -> 3. satır: −₺38,20 desi farkı
-> yüzlerce sipariş hızla akar "gözle bulamazsın" -> Dashtock hakediş ekranı: Beklenen/Ödenen/Fark, fark işaretli, itiraz takibi
-> "Satış, para yatınca biter." -> logo + yorum sorusu, döngü. Tüm tutarlar ÖRNEK.
Kullanım: python3 render_hakedis.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, random
sys.path.insert(0, "/tmp/claude-0/-home-user-sosyalmerkez/4499d60f-753d-5efb-9ad2-6db01160c7c0/scratchpad/is")
from yardimci import *
from PIL import Image, ImageDraw, ImageFilter

DUR = 28.2
T_Q = 4.7      # "Solda beklenen, sağda yatan" + geri sayım
T_ANS = 8.8    # cevap: 3. satır
T_SCR = 14.3   # yüzlerce sipariş akışı
T_PAN = 16.8   # Dashtock hakediş ekranı
T_CLK = 19.6   # itiraz takibine al
T_S = 21.2     # slogan
T_S2 = 21.9
T_S3 = 22.6
T_END = 23.8
T_LOOP = DUR - 0.3

TY = (242, 122, 32); HB = (250, 85, 45); N11 = (120, 90, 230); CS = (60, 170, 90)
ROWS = [("#1041", "T", TY, "Trendyol", 412.60, 412.60),
        ("#1042", "H", HB, "Hepsiburada", 289.90, 289.90),
        ("#1043", "T", TY, "Trendyol", 655.30, 617.10),
        ("#1044", "N", N11, "N11", 198.45, 198.45),
        ("#1045", "Ç", CS, "ÇiçekSepeti", 344.00, 344.00)]
BAD = 2

def num(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def table(c, t, a, x0=70, y0=640, w=940):
    """Basit hakediş ekstresi: Sipariş | Beklenen | Yatan"""
    if a <= 0.01: return
    rh = 132
    hgt = 150 + rh * len(ROWS) + 30
    reveal = t >= T_ANS
    put_card(c, x0, y0, w, hgt, CORAL if reveal else None, a, CARD, 0.35 if reveal else 0, 34)
    place(c, text_img("Hakediş ekstresi", font(DB, 44)), x0 + 36, y0 + 52, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 52, a, "r")
    hy = y0 + 118
    for txt, xx, anc in (("Sipariş", x0 + 36, "l"), ("Beklenen", x0 + 610, "r"), ("Yatan", x0 + w - 36, "r")):
        place(c, text_img(txt, font(IB, 30), GREY), xx, hy, a, anc)
    d = ImageDraw.Draw(c)
    d.line((x0 + 30, hy + 30, x0 + w - 30, hy + 30), fill=(60, 68, 96, int(255 * a)), width=2)
    for i, (no, ch, col, nm, bek, yat) in enumerate(ROWS):
        y = y0 + 160 + i * rh
        ra = clamp((t - 0.15 - i * 0.07) / 0.2) * a
        bad = i == BAD
        k = 1.0
        if reveal and not bad: k = 0.35
        if reveal and bad:
            hl = clamp((t - T_ANS) / 0.2)
            d.rounded_rectangle((x0 + 18, y - 8, x0 + w - 18, y + rh - 22), 22, fill=(90, 28, 30, int(230 * ra * hl)),
                                outline=CORAL + (int(255 * ra * hl),), width=4)
        place(c, letter_badge(ch, col, 62), x0 + 36, y + 52, ra * k, "l")
        place(c, text_img(nm, font(DB, 38)), x0 + 116, y + 30, ra * k, "l")
        place(c, text_img(no, font(IM, 28), GREY), x0 + 116, y + 74, ra * k, "l")
        place(c, text_img(num(bek), font(DB, 44)), x0 + 610, y + 52, ra * k, "r")
        ycol = CORAL if (reveal and bad) else WHITE
        sc = (1 + 0.22 * math.exp(-(t - T_ANS) * 6)) if (reveal and bad) else 1
        place(c, text_img(num(yat), font(DB, 44), ycol), x0 + w - 36, y + 52, ra * k, "r", sc)

def s_quiz(c, t):
    """0 -> T_SCR: kanca, soru, cevap"""
    a = 1 - clamp((t - T_SCR) / 0.15)
    if a <= 0.01: return
    if t < T_Q:
        ha = 1 - clamp((t - T_Q + 0.15) / 0.15)
        place(c, native_text("Pazaryeri sana", 104, WHITE), W / 2, 230, ha, "c", lerp(1.3, 1, ease_out(t / 0.25)))
        place(c, native_text("eksik ödedi.", 120, CORAL), W / 2, 365, clamp((t - 0.25) / 0.1) * ha, "c", lerp(1.4, 1, ease_out((t - 0.25) / 0.25)))
        if t > 1.1:
            place(c, rich([("Bulabilir misin?", GOLD), ("emo", "👀")], 84, GOLD), W / 2, 505, clamp((t - 1.1) / 0.12) * ha, "c", back_out((t - 1.1) / 0.3))
    elif t < T_ANS:
        qa = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_ANS + 0.1) / 0.1))
        place(c, native_text("Solda beklenen,", 96, WHITE), W / 2, 250, qa, "c", back_out((t - T_Q) / 0.3))
        place(c, native_text("sağda yatan.", 96, TEAL), W / 2, 375, qa, "c", back_out((t - T_Q - 0.15) / 0.3))
        place(c, text_img("Farkı bul", font(DB, 54), GOLD), W / 2, 500, qa, "c")
        t0 = T_Q + 0.9; seg = (T_ANS - t0) / 3
        if t > t0:
            n = 3 - int((t - t0) / seg)
            place(c, native_text(str(max(1, n)), 150, GOLD), W / 2, 1650, qa, "c", 1 + 0.2 * math.exp(-((t - t0) % seg) * 8))
    else:
        b = clamp((t - T_ANS) / 0.1)
        place(c, native_text("Buldun mu?", 92, WHITE), W / 2, 230, b * (1 - clamp((t - T_ANS - 1.4) / 0.15)), "c", back_out((t - T_ANS) / 0.3))
        if t > T_ANS + 1.4:
            u = (t - T_ANS - 1.4)
            place(c, native_text("−₺38,20", 170, CORAL), W / 2, 330, clamp(u / 0.1), "c", lerp(1.6, 1, ease_out(u / 0.2)))
        if t > T_ANS + 2.2:
            u = t - T_ANS - 2.2
            place(c, pill("Desi farkı diye kesilmiş", font(DX, 46), WHITE, (150, 40, 44, 255), 30, 12), W / 2, 1650, clamp(u / 0.12), "c", back_out(u / 0.3))
    table(c, t, clamp(t / 0.12) * a)

def s_scroll(c, t):
    a = clamp((t - T_SCR) / 0.12) * (1 - clamp((t - T_PAN) / 0.15))
    if a <= 0.01: return
    u = t - T_SCR
    rg = random.Random(11)
    d = ImageDraw.Draw(c)
    speed = 900 + 1800 * clamp(u / 1.2)
    off = (u * speed) % 120
    for k in range(-1, 16):
        y = 560 + k * 120 + off - 120
        r = random.Random(k + int(u * speed // 120) * 7)
        nm = r.choice(("Trendyol", "Hepsiburada", "N11", "ÇiçekSepeti", "Pazarama"))
        v = r.uniform(120, 900)
        d.rounded_rectangle((70, y, 1010, y + 100), 20, fill=(20, 26, 42, int(235 * a)))
        place(c, text_img(nm, font(DB, 36), GREY), 110, y + 50, a * 0.8, "l")
        place(c, text_img(num(v), font(DB, 38), WHITE), 640, y + 50, a * 0.8, "r")
        place(c, text_img(num(v), font(DB, 38), WHITE), 970, y + 50, a * 0.8, "r")
    # üst ve alt karartma
    c.alpha_composite(tc("scrfade", lambda: _scrfade()), (0, 0)) if a > 0.5 else None
    place(c, native_text("Yüzlerce siparişte", 96, WHITE), W / 2, 230, a, "c", back_out(u / 0.3))
    place(c, native_text("gözle bulamazsın.", 96, CORAL), W / 2, 355, clamp((u - 0.3) / 0.1) * a, "c", back_out((u - 0.3) / 0.3))
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), W / 2, 1780, a, "c")

def _scrfade():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y in range(0, 560):
        d.line((0, y, W, y), fill=(7, 10, 24, int(255 * clamp((560 - y) / 160))))
    for y in range(1600, H):
        d.line((0, y, W, y), fill=(7, 10, 24, int(255 * clamp((y - 1600) / 160))))
    return im

PROWS = [("Trendyol", "T", TY, 412.60, 412.60), ("Hepsiburada", "H", HB, 289.90, 289.90), ("Trendyol", "T", TY, 655.30, 617.10),
         ("N11", "N", N11, 198.45, 198.45), ("ÇiçekSepeti", "Ç", CS, 344.00, 344.00), ("Pazarama", "P", BLUE, 152.80, 152.80)]
def s_panel(c, t):
    a = clamp((t - T_PAN) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_PAN
    place(c, native_text("Dashtock", 100, WHITE), W / 2, 220, a, "c", back_out(u / 0.3))
    place(c, native_text("farkı önüne koyar.", 90, TEAL), W / 2, 340, clamp((u - 0.25) / 0.1) * a, "c", back_out((u - 0.25) / 0.3))
    x0, y0, w = 50, 450, 980
    put_card(c, x0, y0, w, 1210, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Hakediş mutabakatı", font(DB, 44)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    hy = y0 + 140
    cols = ((x0 + 36, "Pazaryeri", "l"), (x0 + 560, "Beklenen", "r"), (x0 + 760, "Ödenen", "r"), (x0 + w - 36, "Fark", "r"))
    for xx, txt, anc in cols: place(c, text_img(txt, font(IB, 28), GREY), xx, hy, a, anc)
    d = ImageDraw.Draw(c)
    d.line((x0 + 30, hy + 28, x0 + w - 30, hy + 28), fill=(60, 68, 96, int(255 * a)), width=2)
    mark_t = T_PAN + 1.2
    for i, (nm, ch, col, bek, od) in enumerate(PROWS):
        y = y0 + 180 + i * 108
        ra = clamp((u - 0.2 - i * 0.08) / 0.18) * a
        bad = abs(bek - od) > 0.001
        if bad and t > mark_t:
            hl = clamp((t - mark_t) / 0.2)
            d.rounded_rectangle((x0 + 16, y - 6, x0 + w - 16, y + 94), 20, fill=(90, 28, 30, int(220 * ra * hl)), outline=CORAL + (int(255 * ra * hl),), width=4)
        place(c, letter_badge(ch, col, 56), x0 + 36, y + 44, ra, "l")
        place(c, text_img(nm, font(DB, 34)), x0 + 106, y + 44, ra, "l")
        place(c, text_img(num(bek), font(DS, 36)), x0 + 560, y + 44, ra, "r")
        place(c, text_img(num(od), font(DS, 36), CORAL if bad and t > mark_t else WHITE), x0 + 760, y + 44, ra, "r")
        if bad:
            fa = ra * clamp((t - mark_t) / 0.15)
            place(c, text_img("−" + num(bek - od), font(DB, 36), CORAL), x0 + w - 36, y + 44, fa, "r", 1 + 0.25 * math.exp(-max(0, t - mark_t) * 7))
            place(c, icon_circle("warn", 44, CORAL), x0 + w - 36, y + 44, ra * (1 - clamp((t - mark_t) / 0.1)), "r")
        else:
            place(c, icon_circle("check", 44, GREEN), x0 + w - 36, y + 44, ra, "r")
    # özet + buton
    sy = y0 + 180 + len(PROWS) * 108 + 20
    sa = clamp((t - mark_t - 0.2) / 0.2) * a
    put_card(c, x0 + 30, sy, w - 60, 130, CORAL, sa, CARD2, 0.25, 26)
    place(c, icon_circle("warn", 64, CORAL), x0 + 70, sy + 65, sa, "l")
    place(c, text_img("1 farklı ödeme bulundu", font(DB, 40)), x0 + 156, sy + 45, sa, "l")
    place(c, text_img("Sebep: desi farkı · itiraz edilebilir", font(IM, 30), GREY), x0 + 156, sy + 92, sa, "l")
    by = sy + 220
    ba = clamp((t - T_CLK + 0.6) / 0.2) * a
    clicked = t >= T_CLK
    place(c, pill("İtiraz takibinde ✓" if clicked else "İtiraz takibine al", font(DX, 42), WHITE, (GREEN if clicked else INDIGO) + (255,), 36, 16),
          W / 2, by, ba, "c", 1 + 0.12 * math.exp(-max(0, t - T_CLK) * 8) * clicked)
    draw_cursor(c, W / 2 + 150 + 8 * math.sin(t * 3), by + 18, ba, (t - T_CLK) / 0.35 if 0 <= t - T_CLK <= 0.35 else -1)

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    for w_, col, ti, y, sz in (("Satış,", WHITE, T_S, 760, 150), ("para yatınca", TEAL, T_S2, 930, 130), ("biter.", TEAL, T_S3, 1090, 150)):
        wa = clamp((t - ti) / 0.1) * a
        place(c, native_text(w_, sz, col), W / 2, y, wa, "c", lerp(1.5, 1, ease_out((t - ti) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Web siten + 8 pazaryeri", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("Hakediş · fatura · stok tek panelde", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Son hakedişini", 76, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("kontrol ettin mi?", GOLD), ("emo", "👇")], 76, GOLD), W / 2, 1020, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (CORAL if t < T_PAN else BLUE, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_Q, T_ANS, T_SCR, T_PAN, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_quiz(c, t); s_scroll(c, t); s_panel(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in (T_ANS, T_ANS + 1.4, T_PAN + 1.2, T_S, T_S3):
        if 0 <= t - x < 0.25: sh += 10 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.6), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, q=T_Q, ans=T_ANS, scr=T_SCR, pan=T_PAN, clk=T_CLK, s=T_S, s2=T_S2, s3=T_S3, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
