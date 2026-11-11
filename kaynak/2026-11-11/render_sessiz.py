"""Dashtock "11.11. Son ürünü sattın. Biri hâlâ satıyor. Bul." ~30 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: merkezi stok + otonom stok mutabakatı (pazaryeri stok güncellemesini sessizce reddettiyse yakalar; saatlik).
Akış: "11.11" + "Son ürünü sattın." STOK 1->0 -> 5 kanal kartı, biri hâlâ "Satışta" (bul, 3-2-1) -> açığa çıkar: "Gönderildi. Ama işlenmedi."
-> gece 02:14 sipariş bildirimi -> İPTAL + mağaza puanı düşer -> Dashtock stok mutabakatı tablosu: fark yakalandı
-> "Gönderildi demek güncellendi demek değil." -> logo, döngü.
Arayüz çizim, sayılar ÖRNEK.
Kullanım: python3 render_sessiz.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 30.0
T_STOK = 1.6     # stok 1 -> 0
T_GRID = 4.2     # kanal kartları
T_CD = 6.4       # geri sayım
T_REV = 9.3      # açığa çıkar
T_ORD = 14.4     # gece siparişi
T_IPT = 16.2     # iptal damgası
T_FIX = 19.2     # Dashtock mutabakat
T_CATCH = 21.4   # fark yakalandı
T_S = 24.1       # slogan
T_END = 26.8
T_LOOP = DUR - 0.3

CH = [("Web siten", INDIGO), ("Trendyol", CORAL), ("Hepsiburada", AMBER), ("N11", PURPLE), ("ÇiçekSepeti", TEAL)]
BAD = 3

def s_hook(c, t):
    a = 1 - clamp((t - T_GRID + 0.1) / 0.12)
    if a <= 0.01: return
    place(c, native_text("11.11", 190, GOLD), W / 2, 260, a, "c", lerp(1.6, 1, ease_out(t / 0.2)))
    place(c, native_text("Son ürünü sattın.", 104, WHITE), W / 2, 470, clamp((t - 0.5) / 0.1) * a, "c", lerp(1.5, 1, ease_out((t - 0.5) / 0.2)))
    # stok sayacı kartı
    x0, y0, w, h = 190, 720, 700, 640
    put_card(c, x0, y0, w, h, None, a, CARD, 0, 44)
    place(c, text_img("STOK", font(DB, 60), GREY), W / 2, y0 + 110, a, "c")
    u = t - T_STOK
    if u < 0:
        place(c, text_img("1", font(DX, 330), WHITE), W / 2, y0 + 360, a, "c")
    else:
        k = ease_out(u / 0.35)
        place(c, text_img("1", font(DX, 330), WHITE), W / 2, y0 + 360 - 260 * k, a * (1 - k), "c")
        place(c, text_img("0", font(DX, 330), GREEN), W / 2, y0 + 360 + 260 * (1 - k), a * k, "c", 1 + 0.15 * math.exp(-u * 6))
        place(c, pill("Tükendi · tüm kanallara gönderildi", font(DB, 36), (8, 30, 18), GREEN + (255,), 24, 10), W / 2, y0 + h - 80,
              clamp((u - 0.5) / 0.2) * a, "c")
    place(c, text_img("Rahatsın, değil mi?", font(DB, 58), (205, 210, 232)), W / 2, 1520, clamp((t - 2.8) / 0.3) * a, "c")

def ch_card(name, col, bad, reveal=0.0, w=900, h=210):
    """reveal 0..1: kötü kartın kırmızı vurgusu"""
    def mk():
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        oc = mixc(col, RED, reveal) if bad else col
        d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=CARD2 + (250,), outline=oc + (255,), width=4 + int(6 * reveal * bad))
        d.rounded_rectangle((30, 50, 140, 160), 28, fill=col + (255,))
        ini = name[0] if name != "Web siten" else "W"
        f = font(DX, 62); b = d.textbbox((0, 0), ini, font=f)
        d.text((85 - (b[2] - b[0]) / 2 - b[0], 105 - (b[3] - b[1]) / 2 - b[1]), ini, font=f, fill=WHITE)
        im.alpha_composite(text_img(name, font(DB, 56)), (170, 40))
        st = "Satışta" if bad else "Satışa kapalı"
        dc = GREEN if bad else DIM
        d.ellipse((172, 140, 196, 164), fill=dc + (255,))
        im.alpha_composite(text_img(st, font(IM, 36), GREY), (208, 130))
        n = "3" if bad else "0"
        im.alpha_composite(text_img("stok " + n, font(IM, 38), GREY), (w - 190, 82))
        return im
    return tc(("chc", name, bad, round(reveal, 2)), mk)

def s_grid(c, t):
    a = clamp((t - T_GRID) / 0.12) * (1 - clamp((t - T_ORD + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_GRID
    rv = ease_out((t - T_REV) / 0.4) if t >= T_REV else 0
    if t < T_REV:
        place(c, native_text("Biri hâlâ satıyor.", 100, WHITE), W / 2, 170, a, "c", lerp(1.5, 1, ease_out(u / 0.2)))
        place(c, native_text("Bul.", 130, GOLD), W / 2, 310, clamp((u - 0.5) / 0.1) * a, "c", lerp(1.7, 1, ease_out((u - 0.5) / 0.2)))
    else:
        v = t - T_REV
        place(c, native_text("Gönderildi.", 110, WHITE), W / 2, 170, a, "c", lerp(1.5, 1, ease_out(v / 0.2)))
        place(c, native_text("Ama işlenmedi.", 110, RED), W / 2, 310, clamp((v - 0.9) / 0.1) * a, "c", lerp(1.5, 1, ease_out((v - 0.9) / 0.2)))
    for i, (nm, col) in enumerate(CH):
        v = u - 0.3 - i * 0.14
        bad = i == BAD
        ca = clamp(v / 0.1) * a
        if rv > 0 and not bad: ca *= 1 - 0.65 * rv
        y = 560 + i * 245
        sc = 1 + (0.06 * rv if bad else 0)
        place(c, ch_card(nm, col, bad, rv if bad else 0), W / 2 + 700 * (1 - ease_out(v / 0.35)), y, ca, "c", sc)
    if rv > 0:
        v = t - T_REV
        place(c, pill("Güncelleme sessizce reddedildi", font(DB, 40), WHITE, RED + (255,), 26, 12), W / 2, 1690,
              clamp((v - 1.6) / 0.2) * a, "c", back_out((v - 1.6) / 0.3))
        place(c, text_img("Kimse sana haber vermedi.", font(DB, 52), (205, 210, 232)), W / 2, 1800, clamp((v - 2.6) / 0.3) * a, "c")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), W - 70, 440, a, "r")
    if T_CD <= t < T_REV:
        seg = (T_REV - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text(str(max(1, n)), 150, GOLD), W / 2, 1800, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))

def s_order(c, t):
    a = clamp((t - T_ORD) / 0.12) * (1 - clamp((t - T_FIX + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_ORD
    c.alpha_composite(Image.new("RGBA", (W, H), (3, 4, 10, int(150 * a))))
    place(c, text_img("02:14", font(DX, 230), (230, 234, 250)), W / 2, 330, a, "c")
    place(c, text_img("Çarşamba, 11 Kasım", font(DB, 46), GREY), W / 2, 480, a, "c")
    # bildirim
    v = u - 0.4
    if v >= 0:
        x0, y0, w, h = 70, 640, 940, 230
        yy = y0 - 160 * (1 - ease_out(v / 0.35))
        put_card(c, x0, yy, w, h, None, clamp(v / 0.1) * a, (236, 238, 246), 0, 40)
        na = clamp(v / 0.1) * a
        place(c, letter_badge("N", PURPLE, 96), x0 + 40, yy + h / 2, na, "l")
        place(c, text_img("N11 · şimdi", font(IM, 36), (90, 96, 120)), x0 + 160, yy + 70, na, "l")
        place(c, text_img("Yeni sipariş: 1 adet", font(DB, 54), (20, 24, 40)), x0 + 160, yy + 135, na, "l")
        place(c, text_img("Depoda ürün yok.", font(DB, 40), RED), x0 + 160, yy + 192, na, "l")
    w_ = t - T_IPT
    if w_ >= 0:
        k = clamp(w_ / 0.15)
        stamp = native_text("İPTAL", 210, RED)
        st = stamp.rotate(-10, expand=True, resample=Image.BICUBIC)
        place(c, st, W / 2, 1150, k * a, "c", lerp(2.2, 1, ease_out(w_ / 0.18)))
        ra = clamp((w_ - 0.8) / 0.2) * a
        place(c, rich([("Mağaza puanı", WHITE), ("emo", "📉")], 84), W / 2, 1460, ra, "c", back_out((w_ - 0.8) / 0.3))
        place(c, text_img("Müşteri bekledi. Sen bilmiyordun.", font(DB, 50), (205, 210, 232)), W / 2, 1600, clamp((w_ - 1.4) / 0.3) * a, "c")

ROWS = [("Web siten", INDIGO, "0"), ("Trendyol", CORAL, "0"), ("Hepsiburada", AMBER, "0"), ("N11", PURPLE, "3"), ("ÇiçekSepeti", TEAL, "0")]
def s_fix(c, t):
    a = clamp((t - T_FIX) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_FIX
    place(c, native_text("Dashtock'ta", 100, WHITE), W / 2, 170, a, "c", back_out(u / 0.3))
    place(c, native_text("her saat kontrol.", 100, TEAL), W / 2, 290, clamp((u - 0.4) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.4) / 0.2)))
    x0, y0, w = 50, 410, 980
    put_card(c, x0, y0, w, 1200, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 64, a, "l")
    place(c, text_img("Stok mutabakatı", font(DB, 48)), x0 + 106, y0 + 62, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 64, a, "r")
    hy = y0 + 170
    place(c, text_img("Kanal", font(DB, 36), GREY), x0 + 50, hy, a, "l")
    place(c, text_img("Panel", font(DB, 36), GREY), x0 + 520, hy, a, "c")
    place(c, text_img("Kanalda", font(DB, 36), GREY), x0 + 700, hy, a, "c")
    d = ImageDraw.Draw(c)
    d.line((x0 + 40, hy + 40, x0 + w - 40, hy + 40), fill=DIM + (int(255 * a),), width=2)
    for i, (nm, col, kv) in enumerate(ROWS):
        v = u - 0.5 - i * 0.22
        if v < 0: continue
        ra = clamp(v / 0.12) * a
        y = hy + 130 + i * 150
        bad = kv != "0"
        if bad and t >= T_CATCH:
            k = clamp((t - T_CATCH) / 0.2)
            d.rounded_rectangle((x0 + 24, y - 62, x0 + w - 24, y + 62), 24, fill=(70, 24, 30, int(255 * k * a)), outline=RED + (int(255 * k * a),), width=4)
        place(c, letter_badge(nm[0] if nm != "Web siten" else "W", col, 76), x0 + 50, y, ra, "l")
        place(c, text_img(nm, font(DB, 44)), x0 + 145, y, ra, "l")
        place(c, text_img("0", font(DX, 60)), x0 + 520, y, ra, "c")
        place(c, text_img(kv, font(DX, 60), RED if bad else WHITE), x0 + 700, y, ra, "c")
        if not bad:
            place(c, icon_circle("check", 58, GREEN, (8, 30, 18)), x0 + 860, y, ra, "c", back_out(v / 0.3))
        elif t >= T_CATCH:
            place(c, icon_circle("warn", 64, RED, WHITE), x0 + 860, y, a, "c", back_out((t - T_CATCH) / 0.3))
    if t >= T_CATCH:
        v = t - T_CATCH
        place(c, pill("Fark yakalandı: N11 güncellemeyi almadı", font(DB, 38), WHITE, RED + (255,), 26, 12), W / 2, y0 + 1030,
              clamp((v - 0.3) / 0.2) * a, "c", back_out((v - 0.3) / 0.3))
        place(c, text_img("Sipariş gelmeden önce görürsün.", font(DB, 46), (205, 210, 232)), W / 2, y0 + 1125, clamp((v - 1.0) / 0.3) * a, "c")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    u = t - T_S
    place(c, native_text("“Gönderildi”", 150, WHITE), W / 2, 720, a, "c", lerp(1.5, 1, ease_out(u / 0.18)))
    place(c, native_text("demek", 110, (205, 210, 232)), W / 2, 880, clamp((u - 0.4) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.4) / 0.18)))
    place(c, native_text("“güncellendi”", 150, GOLD), W / 2, 1040, clamp((u - 0.8) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.8) / 0.18)))
    place(c, native_text("demek değil.", 120, GOLD), W / 2, 1200, clamp((u - 1.2) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 1.2) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Kendi web siten + pazaryerlerin", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("tek stok, tek panel", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Sen kaç saniyede", 84, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("buldun?", GOLD), ("emo", "👇")], 84, GOLD), W / 2, 1030, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    alt = RED if T_ORD <= t < T_FIX else (TEAL if t >= T_FIX else CORAL)
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (alt, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_STOK, T_GRID, T_REV, T_ORD, T_IPT, T_FIX, T_CATCH, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_hook(c, t); s_grid(c, t); s_order(c, t); s_fix(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [T_STOK, T_REV, T_IPT, T_CATCH, T_S, T_S + 0.8]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.7), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, stok=T_STOK, grid=T_GRID, cd=T_CD, rev=T_REV, ord=T_ORD, ipt=T_IPT, fix=T_FIX, catch=T_CATCH,
                              s=T_S, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
