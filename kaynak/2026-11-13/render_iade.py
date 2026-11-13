"""Dashtock "Cuma 13. 11.11 iadeleri kapıda. İadeyi onayladın, sonra ne unutulur?" ~29 sn dikey kısa (1080x1920).
Konu: iade/talep takibi (Trendyol, Hepsiburada, N11, Ozon tek listede); iade onaylanınca e-Arşiv otomatik iptal + müşteriye bildirim.
Akış: CUMA 13 -> "asıl korkutan başka" -> İADE kolileri (11.11) -> quiz A/B/C + 3-2-1 -> "İkisi de." (fatura açık, müşteri bekliyor)
-> Dashtock İadeler ekranı, Onayla tıkı -> e-Arşiv iptal + bildirim -> "Onaylamak, kapatmak değildir." -> logo.
Arayüz çizim, veriler ÖRNEK. Anlatım Sosyal Merkez'de eklenir.
Kullanım: python3 render_iade.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 29.4
T_K = 1.7      # "asıl korkutan başka"
T_BOX = 3.8    # iade kolileri
T_Q = 7.0      # quiz
T_CD = 9.6     # geri sayım
T_REV = 12.6   # İkisi de
T_FIX = 16.8   # Dashtock iadeler
T_OK = 18.4    # Onayla tıkı
T_S = 23.0     # slogan
T_END = 25.2
T_LOOP = DUR - 0.3

def s_hook(c, t):
    a = 1 - clamp((t - T_BOX + 0.1) / 0.12)
    if a <= 0.01: return
    fl = 1.0
    if t < 1.2:  # ışık titremesi
        fl = 0.35 if int(t * 22) % 5 in (1, 3) and t > 0.25 else 1.0
    place(c, native_text("CUMA", 150, WHITE), W / 2, 380, a * fl, "c", lerp(1.6, 1, ease_out(t / 0.2)))
    place(c, native_text("13", 520, RED), W / 2, 760, clamp((t - 0.2) / 0.08) * a * fl, "c", lerp(1.8, 1, ease_out((t - 0.2) / 0.25)))
    place(c, text_img("13 Kasım", font(DB, 56), (205, 210, 232)), W / 2, 1060, clamp((t - 0.6) / 0.2) * a, "c")
    u = t - T_K
    if u >= 0:
        place(c, native_text("Satıcıyı korkutan", 96, WHITE), W / 2, 1300, clamp(u / 0.1) * a, "c", lerp(1.5, 1, ease_out(u / 0.2)))
        place(c, native_text("bu değil.", 130, GOLD), W / 2, 1450, clamp((u - 0.45) / 0.1) * a, "c", lerp(1.6, 1, ease_out((u - 0.45) / 0.2)))

CH = [("T", "Trendyol", CORAL), ("H", "Hepsiburada", AMBER), ("N", "N11", PURPLE), ("O", "Ozon", BLUE),
      ("T", "Trendyol", CORAL), ("H", "Hepsiburada", AMBER)]
def iade_box(ch, col, size=250):
    def mk():
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        b = icon_circle("box", size, CARD2, (214, 170, 110)); im.alpha_composite(b)
        d = ImageDraw.Draw(im)
        p = pill("İADE", font(DX, int(size * 0.16)), WHITE, RED + (255,), 14, 4)
        p = p.rotate(-12, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(p, ((size - p.size[0]) // 2, int(size * 0.55) - p.size[1] // 2))
        lb = letter_badge(ch, col, int(size * 0.28)); im.alpha_composite(lb, (size - lb.size[0] - 6, 6))
        return im
    return tc(("ib", ch, col, size), mk)

def s_boxes(c, t):
    a = clamp((t - T_BOX) / 0.1) * (1 - clamp((t - T_Q + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_BOX
    place(c, native_text("11.11'in", 120, GOLD), W / 2, 260, a, "c", lerp(1.5, 1, ease_out(u / 0.2)))
    place(c, native_text("iadeleri kapıda.", 112, WHITE), W / 2, 410, clamp((u - 0.35) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.35) / 0.2)))
    pos = [(250, 1450), (540, 1450), (830, 1450), (395, 1200), (685, 1200), (540, 950)]
    for i, ((ch, nm, col), (x, y)) in enumerate(zip(CH, pos)):
        v = u - 0.3 - i * 0.22
        if v < 0: continue
        yy = y - 900 * (1 - ease_out(v / 0.3))
        place(c, iade_box(ch, col), x, yy, clamp(v / 0.08) * a, "c", 1 + 0.08 * math.exp(-max(0, v - 0.3) * 12))
    place(c, text_img("Trendyol · Hepsiburada · N11 · Ozon", font(DB, 44), (205, 210, 232)), W / 2, 1700, clamp((u - 1.4) / 0.3) * a, "c")

OPTS = [("A", "e-Arşiv faturasını iptal etmek"), ("B", "Müşteriye haber vermek"), ("C", "İkisi de")]
def opt_card(L, s, st, w=960, h=190):
    def mk():
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        oc = GREEN if st == "win" else DIM
        d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=CARD2 + (250,), outline=oc + (255,), width=10 if st == "win" else 3)
        d.rounded_rectangle((26, 30, 156, 160), 30, fill=(GREEN + (255,)) if st == "win" else (255, 255, 255, 30))
        f = font(DX, 80); b = d.textbbox((0, 0), L, font=f)
        d.text((91 - (b[2] - b[0]) / 2 - b[0], 95 - (b[3] - b[1]) / 2 - b[1]), L, font=f, fill=(8, 30, 18) if st == "win" else GOLD)
        ti = text_img(s, font(DB, 54 if len(s) < 26 else 48))
        im.alpha_composite(ti, (190, (h - ti.size[1]) // 2))
        return im
    return tc(("opt", L, st), mk)

def s_quiz(c, t):
    a = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_FIX + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_Q
    if t < T_REV:
        place(c, native_text("İadeyi onayladın.", 100, WHITE), W / 2, 230, a, "c", lerp(1.5, 1, ease_out(u / 0.2)))
        place(c, native_text("Sonra ne unutulur?", 100, GOLD), W / 2, 370, clamp((u - 0.5) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.5) / 0.2)))
    else:
        v = t - T_REV
        place(c, native_text("İkisi de.", 170, GREEN), W / 2, 290, a, "c", lerp(1.7, 1, ease_out(v / 0.22)))
    rv = ease_out((t - T_REV) / 0.3) if t >= T_REV else 0
    for i, (L, s) in enumerate(OPTS):
        v = u - 0.9 - i * 0.18
        ca = clamp(v / 0.1) * a
        win = L == "C"
        if rv > 0 and not win: ca *= 1 - 0.55 * rv
        y = 640 + i * 240
        place(c, opt_card(L, s, "win" if (win and rv > 0) else "n"), W / 2 - 700 * (1 - ease_out(v / 0.35)), y, ca, "c",
              1 + (0.05 * rv if win else 0))
    if T_CD <= t < T_REV:
        seg = (T_REV - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text(str(max(1, n)), 170, GOLD), W / 2, 1520, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))
    if t >= T_REV:
        v = t - T_REV
        for j, (ic, col, s) in enumerate((("warn", RED, "Fatura hâlâ açık"), ("bell", AMBER, "Müşteri hâlâ cevap bekliyor"))):
            k = clamp((v - 0.9 - j * 0.7) / 0.15) * a
            y = 1450 + j * 150
            place(c, icon_circle(ic, 100, col), 110, y, k, "l", back_out((v - 0.9 - j * 0.7) / 0.3))
            place(c, text_img(s, font(DB, 56)), 240, y, k, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), W - 60, 500, a, "r")

ROWS = [("T", "Trendyol", CORAL, "Isıtıcı yelek", "Beden uymadı"), ("H", "Hepsiburada", AMBER, "Termos 500 ml", "Vazgeçti"),
        ("N", "N11", PURPLE, "Kupa seti", "Hasarlı geldi"), ("O", "Ozon", BLUE, "Telefon standı", "Vazgeçti")]
def s_fix(c, t):
    a = clamp((t - T_FIX) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_FIX
    place(c, native_text("Dashtock'ta", 100, WHITE), W / 2, 160, a, "c", back_out(u / 0.3))
    place(c, native_text("onayla, gerisi kendiliğinden.", 74, TEAL), W / 2, 275, clamp((u - 0.4) / 0.1) * a, "c",
          lerp(1.5, 1, ease_out((u - 0.4) / 0.2)))
    x0, y0, w = 50, 380, 980
    put_card(c, x0, y0, w, 1000, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 64, a, "l")
    place(c, text_img("İadeler · Talepler", font(DB, 46)), x0 + 106, y0 + 62, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 64, a, "r")
    hy = y0 + 140
    d = ImageDraw.Draw(c)
    d.line((x0 + 40, hy, x0 + w - 40, hy), fill=DIM + (int(255 * a),), width=2)
    ok = t >= T_OK
    for i, (ch, nm, col, pr, why) in enumerate(ROWS):
        v = u - 0.4 - i * 0.15
        if v < 0: continue
        ra = clamp(v / 0.12) * a
        y = hy + 110 + i * 205
        if i == 0:
            k = clamp((t - T_OK) / 0.2) if ok else 0
            d.rounded_rectangle((x0 + 24, y - 85, x0 + w - 24, y + 95), 24, fill=mixc(CARD2, (16, 52, 38), k) + (int(255 * ra),),
                                outline=mixc(DIM, GREEN, k) + (int(255 * ra),), width=3 + int(3 * k))
        place(c, letter_badge(ch, col, 72), x0 + 50, y, ra, "l")
        place(c, text_img(nm + " · " + pr, font(DB, 40)), x0 + 140, y - 26, ra, "l")
        place(c, text_img("Sebep: " + why, font(IM, 34), GREY), x0 + 140, y + 28, ra, "l")
        if i == 0 and ok:
            place(c, pill("Onaylandı", font(DB, 34), (8, 30, 18), GREEN + (255,), 18, 9), x0 + w - 50, y, ra, "r", back_out((t - T_OK) / 0.3))
        else:
            place(c, pill("Onayla", font(DB, 34), WHITE, INDIGO + (255,), 18, 9), x0 + w - 50, y, ra, "r")
    # imleç
    if T_FIX + 0.9 <= t < T_OK + 0.6:
        v = clamp((t - T_FIX - 0.9) / (T_OK - T_FIX - 1.0))
        cx = lerp(700, x0 + w - 120, ease_io(v)); cy = lerp(1300, hy + 120, ease_io(v))
        draw_cursor(c, cx, cy, a, (t - T_OK) / 0.4 if t >= T_OK else -1)
    if ok:
        v = t - T_OK
        for j, (ic, col, s1, s2) in enumerate((("check", GREEN, "e-Arşiv faturası", "otomatik iptal edildi"),
                                              ("mail", TEAL, "Müşteriye bildirim", "gönderildi"))):
            k = v - 0.5 - j * 0.9
            if k < 0: continue
            yy = 1440 + j * 210 + 120 * (1 - ease_out(k / 0.3))
            na = clamp(k / 0.15) * a
            put_card(c, 70, yy, 940, 180, None, na, (236, 238, 246), 0, 34)
            place(c, icon_circle(ic, 100, col, WHITE), 110, yy + 90, na, "l", back_out(k / 0.3))
            place(c, text_img(s1, font(DB, 46), (20, 24, 40)), 240, yy + 60, na, "l")
            place(c, text_img(s2, font(IM, 40), (70, 80, 110)), 240, yy + 122, na, "l")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    u = t - T_S
    place(c, native_text("İadeyi", 150, (205, 210, 232)), W / 2, 680, a, "c", lerp(1.5, 1, ease_out(u / 0.18)))
    place(c, native_text("onaylamak,", 150, WHITE), W / 2, 850, clamp((u - 0.3) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.3) / 0.18)))
    place(c, native_text("kapatmak", 170, GOLD), W / 2, 1040, clamp((u - 0.75) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.75) / 0.18)))
    place(c, native_text("değildir.", 170, GOLD), W / 2, 1220, clamp((u - 1.15) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 1.15) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Kendi web siten + pazaryerlerin", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("sipariş, iade, fatura tek panelde", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Sen hangisini", 84, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("seçtin?", GOLD), ("emo", "👇")], 84, GOLD), W / 2, 1030, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    alt = RED if t < T_BOX or T_REV <= t < T_FIX else (TEAL if t >= T_FIX else AMBER)
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (alt, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_K, T_BOX, T_Q, T_REV, T_FIX, T_OK, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_hook(c, t); s_boxes(c, t); s_quiz(c, t); s_fix(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [0.2, T_K + 0.45, T_BOX, T_REV, T_OK, T_S, T_S + 0.75]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.7), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, k=T_K, box=T_BOX, q=T_Q, cd=T_CD, rev=T_REV, fix=T_FIX, ok=T_OK,
                              s=T_S, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
