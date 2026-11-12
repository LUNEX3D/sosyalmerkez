"""Dashtock "11.11 bitti. 4 sipariş. Hangisini önce paketlersin?" ~29 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: 11.11 sonrası sipariş yığını + termin (SLA) uyarısı (10 saatten az kalan "acil", geçen "gecikmiş", e-posta),
otomatik sipariş işleme (Yeni -> seçilen kargoyla İşlemde) ve etiket. Web siten + pazaryerleri tek sipariş listesi.
Akış: "11.11 bitti." -> 4 sipariş kartı A-D (sipariş saatine göre) -> 3-2-1 -> açığa çıkar: en yenisi en acil (D, 4 sa)
-> Dashtock sipariş listesi termine göre sıralı, ACİL rozeti, e-posta, İşlemde + etiket -> "Sırayla değil, terminle paketle." -> logo.
Arayüz çizim, sayılar ÖRNEK.
Kullanım: python3 render_termin.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 29.0
T_Q = 1.6        # "Hangisini önce paketlersin?"
T_GRID = 5.3     # kartlar
T_CD = 6.4       # geri sayım
T_REV = 9.4      # açığa çıkar
T_FIX = 15.4     # Dashtock listesi
T_MAIL = 18.0    # e-posta + işlemde
T_S = 22.0       # slogan
T_END = 24.5
T_LOOP = DUR - 0.3

# harf, kanal, renk, ürün, sipariş zamanı, kalan termin, acil mi
ORD = [("A", "Web siten", INDIGO, "Termos 500 ml", "10 Kasım 21:05", "2 gün", False),
       ("B", "Trendyol", CORAL, "Isıtıcı yelek", "11 Kasım 09:40", "1 gün", False),
       ("C", "Hepsiburada", AMBER, "Telefon standı", "11 Kasım 16:20", "30 saat", False),
       ("D", "ÇiçekSepeti", TEAL, "Kupa seti", "11 Kasım 23:58", "4 saat", True)]

def s_hook(c, t):
    a = 1 - clamp((t - T_GRID + 0.1) / 0.12)
    if a <= 0.01: return
    place(c, native_text("11.11", 190, GOLD), W / 2, 300, a, "c", lerp(1.6, 1, ease_out(t / 0.2)))
    place(c, native_text("bitti.", 150, WHITE), W / 2, 500, clamp((t - 0.45) / 0.1) * a, "c", lerp(1.6, 1, ease_out((t - 0.45) / 0.2)))
    # koli yığını
    for i in range(6):
        v = t - 0.7 - i * 0.12
        if v < 0: continue
        bx = W / 2 + (i % 3 - 1) * 190 + (0 if i < 3 else 95) - (95 if i >= 3 else 0)
        by = 1000 - (i // 3) * 170
        place(c, icon_circle("box", 180, CARD2, (214, 170, 110)), bx, by - 300 * (1 - ease_out(v / 0.3)), clamp(v / 0.1) * a, "c")
    u = t - T_Q
    if u >= 0:
        place(c, native_text("Hangisini önce", 104, WHITE), W / 2, 1320, clamp(u / 0.1) * a, "c", lerp(1.5, 1, ease_out(u / 0.2)))
        place(c, native_text("paketlersin?", 120, GOLD), W / 2, 1460, clamp((u - 0.4) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.4) / 0.2)))
        place(c, rich([("4 sipariş", (205, 210, 232)), ("emo", "📦")], 64), W / 2, 1640, clamp((u - 1.2) / 0.3) * a, "c")

def ord_card(o, rv=0.0, w=980, h=270):
    L, nm, col, pr, ts, kal, urg = o
    def mk():
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        oc = mixc(DIM, RED, rv) if urg else DIM
        d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=CARD2 + (250,), outline=oc + (255,), width=3 + int(7 * rv * urg))
        # harf
        d.rounded_rectangle((26, 26, 130, 130), 30, fill=(255, 255, 255, 30))
        f = font(DX, 70); b = d.textbbox((0, 0), L, font=f)
        d.text((78 - (b[2] - b[0]) / 2 - b[0], 78 - (b[3] - b[1]) / 2 - b[1]), L, font=f, fill=GOLD)
        im.alpha_composite(letter_badge(nm[0] if nm != "Web siten" else "W", col, 60), (160, 36))
        im.alpha_composite(text_img(nm, font(DB, 46)), (240, 40))
        im.alpha_composite(text_img(pr, font(IM, 40), (205, 210, 232)), (160, 118))
        im.alpha_composite(text_img("Sipariş: " + ts, font(IM, 36), GREY), (160, 190))
        if rv > 0:
            if urg:
                p = pill("ACİL · " + kal, font(DB, 40), WHITE, RED + (255,), 22, 10)
            else:
                p = pill("kalan " + kal, font(DB, 36), (205, 210, 232), (50, 58, 84, 255), 20, 9)
            p = fade(p, rv)
            im.alpha_composite(p, (w - p.size[0] - 30, 40))
        return im
    return tc(("oc", L, round(rv, 2)), mk)

def s_grid(c, t):
    a = clamp((t - T_GRID) / 0.12) * (1 - clamp((t - T_FIX + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_GRID
    rv = ease_out((t - T_REV - 0.3) / 0.4) if t >= T_REV + 0.3 else 0
    if t < T_REV:
        place(c, native_text("Hangisi önce?", 110, WHITE), W / 2, 190, a, "c", lerp(1.5, 1, ease_out(u / 0.2)))
        place(c, native_text("A · B · C · D", 90, GOLD), W / 2, 330, clamp((u - 0.4) / 0.1) * a, "c")
    else:
        v = t - T_REV
        place(c, native_text("En yenisi,", 120, WHITE), W / 2, 190, a, "c", lerp(1.5, 1, ease_out(v / 0.2)))
        place(c, native_text("en acili.", 130, RED), W / 2, 335, clamp((v - 0.8) / 0.1) * a, "c", lerp(1.6, 1, ease_out((v - 0.8) / 0.2)))
    for i, o in enumerate(ORD):
        v = u - 0.25 - i * 0.14
        ca = clamp(v / 0.1) * a
        if rv > 0 and not o[6]: ca *= 1 - 0.55 * rv
        y = 590 + i * 300
        sc = 1 + (0.05 * rv if o[6] else 0)
        place(c, ord_card(o, rv), W / 2 - 700 * (1 - ease_out(v / 0.35)), y, ca, "c", sc)
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), W - 60, 432, a, "r")
    if T_CD <= t < T_REV:
        seg = (T_REV - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text(str(max(1, n)), 150, GOLD), W / 2, 1790, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))
    if t >= T_REV:
        v = t - T_REV
        place(c, text_img("Her kanalın, her ürünün kargo süresi farklı.", font(DB, 42), (205, 210, 232)), W / 2, 1790,
              clamp((v - 2.2) / 0.3) * a, "c")

ROWS = [("ÇiçekSepeti", TEAL, "Kupa seti", "3 sa 52 dk", "acil"), ("Hepsiburada", AMBER, "Telefon standı", "30 sa", "ok"),
        ("Trendyol", CORAL, "Isıtıcı yelek", "1 gün", "ok"), ("Web siten", INDIGO, "Termos 500 ml", "2 gün", "ok")]
def s_fix(c, t):
    a = clamp((t - T_FIX) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_FIX
    place(c, native_text("Dashtock'ta", 100, WHITE), W / 2, 170, a, "c", back_out(u / 0.3))
    place(c, native_text("termine göre sıralı.", 96, TEAL), W / 2, 290, clamp((u - 0.4) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.4) / 0.2)))
    x0, y0, w = 50, 410, 980
    put_card(c, x0, y0, w, 1060, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 64, a, "l")
    place(c, text_img("Siparişler · Termin", font(DB, 46)), x0 + 106, y0 + 62, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 64, a, "r")
    hy = y0 + 160
    d = ImageDraw.Draw(c)
    d.line((x0 + 40, hy, x0 + w - 40, hy), fill=DIM + (int(255 * a),), width=2)
    for i, (nm, col, pr, kal, st) in enumerate(ROWS):
        v = u - 0.5 - i * 0.2
        if v < 0: continue
        ra = clamp(v / 0.12) * a
        y = hy + 110 + i * 200 + (70 if i else 0)
        urg = st == "acil"
        if urg:
            k = clamp(v / 0.2)
            d.rounded_rectangle((x0 + 24, y - 80, x0 + w - 24, y + 150), 24, fill=(70, 24, 30, int(255 * k * a)), outline=RED + (int(255 * k * a),), width=4)
        place(c, letter_badge(nm[0] if nm != "Web siten" else "W", col, 72), x0 + 50, y, ra, "l")
        place(c, text_img(nm, font(DB, 42)), x0 + 140, y - 26, ra, "l")
        place(c, text_img(pr, font(IM, 36), GREY), x0 + 140, y + 28, ra, "l")
        if urg:
            place(c, pill("ACİL · " + kal, font(DB, 36), WHITE, RED + (255,), 20, 9), x0 + w - 50, y, ra, "r", back_out(v / 0.3))
        else:
            place(c, text_img(kal, font(DB, 40), (205, 210, 232)), x0 + w - 60, y, ra, "r")
    if t >= T_MAIL:
        v = t - T_MAIL
        # acil satırın durumu: Yeni -> İşlemde · Yurtiçi, etiket hazır
        y = hy + 110
        k = clamp((v - 0.6) / 0.2)
        place(c, pill("İşlemde · Yurtiçi Kargo", font(DB, 34), (8, 30, 18), GREEN + (255,), 18, 8), x0 + 140, y + 100, k * a, "l", back_out((v - 0.6) / 0.3))
        place(c, pill("Etiket hazır", font(DB, 34), WHITE, (50, 58, 84, 255), 18, 8), x0 + 570, y + 100, clamp((v - 1.2) / 0.2) * a, "l",
              back_out((v - 1.2) / 0.3))
        # e-posta bildirimi
        x1, y1, w1, h1 = 70, 1530, 940, 190
        yy = y1 + 140 * (1 - ease_out(v / 0.35))
        na = clamp(v / 0.15) * a
        put_card(c, x1, yy, w1, h1, None, na, (236, 238, 246), 0, 36)
        place(c, icon_circle("mail", 96, RED, WHITE), x1 + 40, yy + h1 / 2, na, "l")
        place(c, text_img("Dashtock · e-posta", font(IM, 34), (90, 96, 120)), x1 + 160, yy + 62, na, "l")
        place(c, text_img("1 acil sipariş: 10 saatten az kaldı", font(DB, 42), (20, 24, 40)), x1 + 160, yy + 122, na, "l")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    u = t - T_S
    place(c, native_text("Sırayla", 170, WHITE), W / 2, 720, a, "c", lerp(1.5, 1, ease_out(u / 0.18)))
    place(c, native_text("değil,", 130, (205, 210, 232)), W / 2, 890, clamp((u - 0.35) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.35) / 0.18)))
    place(c, native_text("terminle", 170, GOLD), W / 2, 1070, clamp((u - 0.8) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.8) / 0.18)))
    place(c, native_text("paketle.", 170, GOLD), W / 2, 1250, clamp((u - 1.2) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 1.2) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Kendi web siten + pazaryerlerin", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("tek sipariş listesi", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Sen hangisini", 84, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("seçtin?", GOLD), ("emo", "👇")], 84, GOLD), W / 2, 1030, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    alt = RED if T_REV <= t < T_FIX else (TEAL if t >= T_FIX else AMBER)
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (alt, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_Q, T_GRID, T_REV, T_FIX, T_MAIL, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_hook(c, t); s_grid(c, t); s_fix(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [T_Q, T_REV, T_REV + 0.8, T_FIX + 0.5, T_S, T_S + 0.8]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.7), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, q=T_Q, grid=T_GRID, cd=T_CD, rev=T_REV, fix=T_FIX, mail=T_MAIL,
                              s=T_S, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
