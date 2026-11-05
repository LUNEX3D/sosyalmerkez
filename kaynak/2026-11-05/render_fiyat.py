"""Dashtock "11.11 fiyat savaşı: nerede durmalıydın?" ~30 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: Fiyat Otopilotu / Buybox Guard: kâr tabanı, tuzak fiyat uyarısı, onaysız fiyat değişmez.
Akış: "11.11'e 6 gün." + Rakip/Sen fiyat ping-pongu (₺499 -> ₺419), merdiven grafik -> "Nerede durmalıydın?" A ₺469 / B ₺449 / C ₺429 + 3-2-1
-> "Doğru cevap: Bilemezsin." + grafikte "Kâr tabanı: ?" -> Dashtock Fiyat Otopilotu kartı: taban ₺440, rakip ₺429 tuzak uyarısı,
öneri ₺449, Onayla -> "Dibe inen kazanmaz." -> logo + yorum sorusu, döngü. Tüm tutarlar ÖRNEK.
Kullanım: python3 render_fiyat.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 29.8
T_D0 = 1.3     # ilk fiyat düşüşü
T_DSTEP = 0.6
T_Q = 6.6      # soru
T_CD = 8.6     # geri sayım
T_ANS = 10.8   # cevap
T_PAN = 14.9   # Dashtock paneli
T_TAB = 16.2   # kâr tabanı satırı
T_RIV = 17.8   # rakip ₺429
T_WARN = 18.4  # tuzak uyarısı
T_REC = 20.0   # öneri ₺449
T_CLK = 21.5   # onayla
T_S = 22.9; T_S2 = 23.5
T_END = 25.6
T_LOOP = DUR - 0.3

# (zaman, kim, yeni fiyat): 0 = rakip, 1 = sen
DROPS = []
p = 499
for k in range(8):
    p -= 10
    DROPS.append((T_D0 + k * T_DSTEP, k % 2, p))

def prices(t):
    r, s = 499, 499; last = [-9, -9]
    for tt, who, v in DROPS:
        if t >= tt:
            if who == 0: r = v
            else: s = v
            last[who] = tt
    return r, s, last

def pnum(v): return f"₺{v}"

def price_tag(c, x, y, label, col, v, a, pop):
    put_card(c, x - 220, y - 150, 440, 300, col, a, CARD, 0.35, 34)
    place(c, text_img(label, font(DB, 46), GREY), x, y - 85, a, "c")
    sc = 1 + 0.25 * math.exp(-max(0, pop) * 7) if pop >= 0 else 1
    place(c, native_text(pnum(v), 116, WHITE), x, y + 30, a, "c", sc)
    if 0 <= pop < 0.6:
        place(c, text_img("−10", font(DX, 56), CORAL), x + 170, y - 175 - 40 * pop, a * (1 - pop / 0.6), "c")

def chart(c, t, a, y0=1180, h=420):
    """merdiven grafik: her düşüş bir basamak"""
    if a <= 0.01: return
    x0, x1 = 110, 970
    put_card(c, 70, y0 - 40, 940, h + 110, None, a, CARD, 0, 30)
    place(c, text_img("Fiyat", font(IB, 30), GREY), x0, y0, a, "l")
    place(c, pill("ÖRNEK", font(IB, 26), (30, 22, 4), GOLD + (255,), 14, 4), 980, y0, a, "r")
    def Y(v): return y0 + 60 + (499 - v) / 90 * (h - 60)
    d = ImageDraw.Draw(c)
    pts = [(x0, Y(499))]
    n = len(DROPS)
    for i, (tt, who, v) in enumerate(DROPS):
        if t < tt: break
        u = clamp((t - tt) / 0.2)
        x = x0 + (i + 1) / n * (x1 - x0)
        prev = pts[-1]
        pts.append((x, prev[1]))
        pts.append((x, lerp(prev[1], Y(v), u)))
    if t >= DROPS[-1][0]: pts.append((x1 + 10, pts[-1][1]))
    else:
        nx = x0 + (sum(1 for d_ in DROPS if t >= d_[0]) + 0.6) / n * (x1 - x0)
        pts.append((min(x1, nx), pts[-1][1]))
    if len(pts) > 1:
        d.line(pts, fill=CORAL + (int(255 * a),), width=8, joint="curve")
        ex, ey = pts[-1]
        d.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), fill=CORAL + (int(255 * a),))
    # cevap aşamasında taban çizgisi "?"
    if t > T_ANS + 2.0:
        u = clamp((t - T_ANS - 2.0) / 0.3) * a
        yy = Y(440); x = x0
        while x < x0 + (x1 - x0) * clamp((t - T_ANS - 2.0) / 0.5):
            d.line((x, yy, x + 26, yy), fill=GOLD + (int(255 * u),), width=6); x += 44
        place(c, pill("Kâr tabanı: ?", font(DX, 40), (30, 22, 4), GOLD + (255,), 22, 8), x1, yy - 50, u, "r", back_out((t - T_ANS - 2.0) / 0.3))

def s_war(c, t):
    a = 1 - clamp((t - T_PAN) / 0.15)
    if a <= 0.01: return
    r, s, last = prices(t)
    # üst yazılar
    if t < T_Q:
        ha = 1 - clamp((t - T_Q + 0.12) / 0.12)
        place(c, native_text("11.11'e 6 gün.", 112, GOLD), W / 2, 200, ha, "c", lerp(1.35, 1, ease_out(t / 0.25)))
        if t > 0.9:
            place(c, native_text("Rakip kırdı.", 92, CORAL), W / 2, 335, clamp((t - 0.9) / 0.1) * ha, "c", back_out((t - 0.9) / 0.3))
        if t > 1.9:
            place(c, native_text("Sen kırdın.", 92, WHITE), W / 2, 450, clamp((t - 1.9) / 0.1) * ha, "c", back_out((t - 1.9) / 0.3))
        if t > 3.6:
            place(c, native_text("O yine. Sen yine.", 78, (205, 210, 232)), W / 2, 560, clamp((t - 3.6) / 0.1) * ha, "c", back_out((t - 3.6) / 0.3))
    elif t < T_ANS:
        qa = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_ANS + 0.1) / 0.1))
        place(c, native_text("Nerede", 120, WHITE), W / 2, 210, qa, "c", back_out((t - T_Q) / 0.3))
        place(c, native_text("durmalıydın?", 120, GOLD), W / 2, 350, qa, "c", back_out((t - T_Q - 0.15) / 0.3))
    else:
        b = clamp((t - T_ANS) / 0.1)
        place(c, native_text("Doğru cevap:", 84, WHITE), W / 2, 200, b, "c", back_out((t - T_ANS) / 0.3))
        if t > T_ANS + 0.6:
            u = t - T_ANS - 0.6
            place(c, native_text("Bilemezsin.", 140, GOLD), W / 2, 340, clamp(u / 0.1), "c", lerp(1.6, 1, ease_out(u / 0.2)))
        if t > T_ANS + 1.7:
            u = t - T_ANS - 1.7
            place(c, native_text("Kâr tabanını", 76, WHITE), W / 2, 485, clamp(u / 0.1), "c", back_out(u / 0.3))
            place(c, native_text("hiç hesaplamadın.", 76, CORAL), W / 2, 580, clamp((u - 0.2) / 0.1), "c", back_out((u - 0.2) / 0.3))
    # fiyat etiketleri / şıklar
    if t < T_Q + 0.3:
        ta = clamp(t / 0.12) * (1 - clamp((t - T_Q) / 0.25))
        yy = 860 if t < T_Q else 860
        price_tag(c, 290, yy, "Rakip", CORAL, r, ta, t - last[0] if last[0] > 0 else -1)
        price_tag(c, 790, yy, "Sen", INDIGO, s, ta, t - last[1] if last[1] > 0 else -1)
        place(c, native_text("VS", 70, GOLD), W / 2, yy + 20, ta, "c")
    if T_Q + 0.1 < t:
        opts = (("A", 469), ("B", 449), ("C", 429))
        dim = t >= T_ANS
        for i, (ch, v) in enumerate(opts):
            oa = clamp((t - T_Q - 0.3 - i * 0.15) / 0.15)
            if dim: oa *= 1 - 0.75 * clamp((t - T_ANS) / 0.3)
            if t > T_ANS + 1.5: oa *= 1 - clamp((t - T_ANS - 1.5) / 0.3)
            x = 190 + i * 350
            yy = 840 if t < T_ANS else 840
            put_card(c, x - 150, yy - 140, 300, 280, None, oa, CARD2, 0, 30)
            place(c, letter_badge(ch, (INDIGO, BLUE, PURPLE)[i], 80), x, yy - 60, oa, "c", back_out((t - T_Q - 0.3 - i * 0.15) / 0.3))
            place(c, native_text(pnum(v), 86, WHITE), x, yy + 55, oa, "c")
            if dim and t < T_ANS + 1.5:
                d = ImageDraw.Draw(c); ca = clamp((t - T_ANS) / 0.15)
                d.line((x - 110, yy - 100, x + 110, yy + 100), fill=CORAL + (int(230 * ca),), width=10)
        if T_CD <= t < T_ANS:
            seg = (T_ANS - T_CD) / 3
            n = 3 - int((t - T_CD) / seg)
            place(c, native_text(str(max(1, n)), 150, GOLD), W / 2, 1720, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))
    chart(c, t, clamp(t / 0.15) * (1 - clamp((t - T_PAN + 0.15) / 0.15)), 1180 if t < T_Q else 1120)

def s_panel(c, t):
    a = clamp((t - T_PAN) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_PAN
    place(c, native_text("Dashtock", 104, WHITE), W / 2, 200, a, "c", back_out(u / 0.3))
    place(c, native_text("tabanını bilir.", 92, TEAL), W / 2, 320, clamp((u - 0.25) / 0.1) * a, "c", back_out((u - 0.25) / 0.3))
    x0, y0, w = 50, 430, 980
    put_card(c, x0, y0, w, 1270, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Fiyat Otopilotu", font(DB, 46)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    # ürün satırı
    ia = clamp((u - 0.3) / 0.2) * a
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((x0 + 36, y0 + 130, x0 + 156, y0 + 250), 22, fill=(48, 56, 86, int(255 * ia)))
    place(c, icon_circle("box", 80, (70, 80, 120)), x0 + 96, y0 + 190, ia, "c")
    place(c, text_img("Seramik kupa seti (4'lü)", font(DB, 42)), x0 + 186, y0 + 168, ia, "l")
    place(c, text_img("Trendyol · Buybox takibi açık", font(IM, 32), GREY), x0 + 186, y0 + 216, ia, "l")
    # satırlar
    rows_y = y0 + 300
    def row(i, label, val, col, ra, sub=None, hl=None):
        y = rows_y + i * 150
        if ra <= 0.01: return
        if hl:
            d.rounded_rectangle((x0 + 24, y - 10, x0 + w - 24, y + 120), 22, fill=hl[0] + (int(200 * ra),), outline=hl[1] + (int(255 * ra),), width=4)
        place(c, text_img(label, font(DS, 38), GREY), x0 + 50, y + 40, ra, "l")
        if sub: place(c, text_img(sub, font(IM, 28), DIM if not hl else (220, 200, 200)), x0 + 50, y + 86, ra, "l")
        place(c, native_text(val, 72, col), x0 + w - 50, y + 52, ra, "r")
    row(0, "Senin fiyatın", "₺459", WHITE, clamp((u - 0.5) / 0.2) * a)
    ta = clamp((t - T_TAB) / 0.2) * a
    row(1, "Kâr tabanı", "₺440", TEAL, ta, "maliyet + komisyon + kargo dahil", ((18, 60, 58), TEAL) if t > T_TAB else None)
    ra_ = clamp((t - T_RIV) / 0.2) * a
    row(2, "Rakip yeni fiyat", "₺429", CORAL, ra_, None, ((90, 28, 30), CORAL) if t > T_WARN else None)
    # uyarı
    wa = clamp((t - T_WARN) / 0.2) * a
    wy = rows_y + 3 * 150 + 10
    put_card(c, x0 + 30, wy, w - 60, 140, CORAL, wa, CARD2, 0.25, 26)
    place(c, icon_circle("warn", 66, CORAL), x0 + 70, wy + 70, wa, "l")
    place(c, text_img("Tuzak fiyat: tabanın altında", font(DB, 40)), x0 + 160, wy + 48, wa, "l")
    place(c, text_img("Takip etme önerilir", font(IM, 32), GREY), x0 + 160, wy + 98, wa, "l")
    # öneri
    oa = clamp((t - T_REC) / 0.2) * a
    oy = wy + 180
    put_card(c, x0 + 30, oy, w - 60, 140, TEAL, oa, CARD2, 0.25, 26)
    place(c, icon_circle("shield", 66, TEAL), x0 + 70, oy + 70, oa, "l")
    place(c, text_img("Öneri: ₺449'da kal", font(DB, 42)), x0 + 160, oy + 48, oa, "l")
    place(c, text_img("Onayın olmadan fiyat değişmez", font(IM, 32), GREY), x0 + 160, oy + 98, oa, "l")
    by = oy + 230
    ba = clamp((t - T_CLK + 0.6) / 0.2) * a
    clicked = t >= T_CLK
    place(c, pill("Onaylandı ✓" if clicked else "Onayla", font(DX, 44), WHITE, (GREEN if clicked else INDIGO) + (255,), 44, 16),
          W / 2, by, ba, "c", 1 + 0.12 * math.exp(-max(0, t - T_CLK) * 8) * clicked)
    draw_cursor(c, W / 2 + 110 + 8 * math.sin(t * 3), by + 18, ba, (t - T_CLK) / 0.35 if 0 <= t - T_CLK <= 0.35 else -1)

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    place(c, native_text("Fiyat savaşında", 90, (205, 210, 232)), W / 2, 700, a, "c", back_out((t - T_S) / 0.3))
    place(c, native_text("dibe inen", 160, CORAL), W / 2, 870, clamp((t - T_S - 0.2) / 0.1) * a, "c", lerp(1.5, 1, ease_out((t - T_S - 0.2) / 0.18)))
    wa = clamp((t - T_S2) / 0.1) * a
    place(c, native_text("kazanmaz.", 160, TEAL), W / 2, 1050, wa, "c", lerp(1.5, 1, ease_out((t - T_S2) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Web siten + 8 pazaryeri", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("Fiyat · stok · sipariş tek panelde", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("11.11'de fiyatın", 76, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("nerede duracak?", GOLD), ("emo", "👇")], 76, GOLD), W / 2, 1020, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (CORAL if t < T_PAN else TEAL, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_Q, T_ANS, T_PAN, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_war(c, t); s_panel(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [d_[0] for d_ in DROPS] + [T_ANS + 0.6, T_WARN, T_S + 0.2, T_S2]:
        if 0 <= t - x < 0.25: sh += (5 if x < T_Q else 10) * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.6), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, drops=[d_[0] for d_ in DROPS], q=T_Q, cd=T_CD, ans=T_ANS, pan=T_PAN, tab=T_TAB, riv=T_RIV, warn=T_WARN,
                              rec=T_REC, clk=T_CLK, s=T_S, s2=T_S2, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
