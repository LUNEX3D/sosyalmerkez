"""Dashtock "Bu videoda kaç bildirim var? Say." ~20,5 sn dikey kısa, sessiz izlemeye göre (müzik + yazı).
Konu: birleşik gelen kutusu + AI taslak yanıt (Trendyol, Hepsiburada, ÇiçekSepeti soruları + WhatsApp, Instagram, e-posta tek ekranda).
Akış: kanca "Kaç bildirim var? Say." -> 12 bildirim yağmuru -> "Kaç tane saydın?" A/B/C -> 12 -> "Ama hepsi aynı soruydu: Kargom nerede?"
-> "6 uygulama. 12 kez aynı cevap." -> Dashtock gelen kutusu, AI taslak, onayla -> "Mesaj 6 yerden gelir. Cevap tek yerden gider." -> logo, döngü.
Kullanım: python3 render_bildirim.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, random, subprocess
sys.path.insert(0, "/home/user/is")
from yardimci import *
from PIL import Image, ImageDraw

DUR = 20.6
T_STORM = 1.5; NSTEP = 0.36; NN = 12
T_Q = T_STORM + NSTEP * NN + 0.35      # 6.17
T_ANS = T_Q + 2.0
T_TW = T_ANS + 1.1
T_TW2 = T_TW + 1.3
T_TW3 = T_TW2 + 1.2
T_INB = T_TW3 + 1.2
T_CL1 = T_INB + 1.9; T_CL2 = T_CL1 + 0.55; T_CL3 = T_CL2 + 0.55
T_S6 = T_CL3 + 0.9; T_S6B = T_S6 + 0.9
T_END = T_S6 + 2.3
T_LOOP = DUR - 0.3

TY = (242, 122, 32); HB = (250, 85, 45); CS = (60, 140, 235); WA = (37, 200, 100); IG = (225, 60, 120); EM = GOLD
APPS = {"Trendyol": TY, "Hepsiburada": HB, "ÇiçekSepeti": CS, "WhatsApp": WA, "Instagram": IG, "E-posta": EM}
NOTIFS = [("Trendyol", "Kargom ne zaman gelir?"), ("WhatsApp", "Merhaba, kargom nerede?"), ("Hepsiburada", "Ürün ne zaman kargolanır?"),
          ("Instagram", "Siparişim ne durumda?"), ("ÇiçekSepeti", "Siparişim yola çıktı mı?"), ("E-posta", "Konu: Kargo durumu"),
          ("Trendyol", "Hâlâ kargoya verilmedi mi?"), ("WhatsApp", "Takip numarası var mı?"), ("Hepsiburada", "Kargo takip no alabilir miyim?"),
          ("E-posta", "Siparişim hâlâ gelmedi"), ("ÇiçekSepeti", "Kargo ne zaman?"), ("Trendyol", "Sipariş verdim, kargo nerede?")]
random.seed(11)
NPOS = [(random.uniform(-60, 60), random.uniform(-4, 4)) for _ in range(NN)]
def nt(k): return T_STORM + 0.1 + k * NSTEP

def app_badge(name, size=64):
    def mk():
        col = APPS[name]; s = 4; S = size * s
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, S - 1, S - 1), S // 4, fill=col + (255,))
        ch = "✉" if name == "E-posta" else name[0]
        f = font(DX, int(S * 0.55)) if ch != "✉" else font(DX, int(S * 0.5))
        if ch == "✉":
            w = int(S * .07); d.rounded_rectangle((S * .2, S * .3, S * .8, S * .7), 8, outline=(30, 22, 4), width=w)
            d.line([(S * .22, S * .33), (S * .5, S * .54), (S * .78, S * .33)], fill=(30, 22, 4), width=w)
        else:
            b = d.textbbox((0, 0), ch, font=f)
            d.text(((S - (b[2] - b[0])) / 2 - b[0], (S - (b[3] - b[1])) / 2 - b[1]), ch, font=f, fill=WHITE)
        return im.resize((size, size), Image.LANCZOS)
    return tc(("ab", name, size), mk)

def notif_card(k, hl=0.0):
    app, msg = NOTIFS[k]
    def mk():
        w, h = 900, 170
        im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
        put_card(im, 30, 30, w, h, None, 1.0, (34, 40, 62), 0, 36)
        place(im, app_badge(app, 84), 60, 30 + h / 2, 1, "l")
        place(im, text_img(app.upper(), font(IB, 30), (175, 182, 210)), 168, 30 + 48, 1, "l")
        place(im, text_img("şimdi", font(IM, 28), DIM), 30 + w - 24, 30 + 48, 1, "r")
        place(im, text_img(msg, font(DB, 50), WHITE), 168, 30 + 110, 1, "l")
        return im
    return tc(("nc", k), mk)

def s1(c, t):  # kanca
    a = 1 - clamp((t - T_Q + 0.1) / 0.15)
    if a <= 0.01: return
    top = clamp((t - T_STORM) / 0.35)
    y1 = lerp(820, 250, ease_io(top)); sz = lerp(1.0, 0.62, ease_io(top))
    place(c, native_text("Bu videoda kaç", 112, WHITE), W / 2, y1 - 70 * sz, a, "c", sz * lerp(1.25, 1, ease_out(t / 0.3)))
    place(c, native_text("bildirim var?", 112, WHITE), W / 2, y1 + 70 * sz, a, "c", sz * lerp(1.25, 1, ease_out(t / 0.3)))
    sa = clamp((t - 0.55) / 0.12) * a
    pulse = 1 + 0.06 * math.sin(t * 9)
    place(c, native_text("SAY. 👆" if False else "SAY.", 190 if top < 1 else 120, GOLD), W / 2, lerp(1130, 450, ease_io(top)), sa, "c",
          lerp(1.6, 1, ease_out((t - 0.55) / 0.2)) * pulse)

def storm(c, t):
    a = 1 - clamp((t - T_TW2) / 0.2)
    if a <= 0.01 or t < T_STORM: return
    dim = clamp((t - T_Q) / 0.2)
    for k in range(NN):
        if t < nt(k): continue
        u = (t - nt(k)) / 0.22
        # yeni gelen üstte, eskiler aşağı kayar
        newer = sum(1 for j in range(NN) if j > k and t >= nt(j))
        y = 600 + newer * 132 + NPOS[k][1]
        if newer > 8: continue
        drop = (1 - ease_out(u)) * -160
        x = W / 2 + NPOS[k][0] * 0.3
        hl = 0
        if t >= T_TW:   # hepsi aynı soru: karta sarı çerçeve
            hl = clamp((t - T_TW - 0.05 * newer) / 0.2)
        im = notif_card(k)
        sc = lerp(1.08, 1.0, ease_out(u)) * (1 - 0.035 * newer)
        place(c, im, x, y + drop, a * clamp(u * 2) * (1 - 0.25 * newer / 8) * (1 - 0.6 * dim * (1 - hl)), "c", sc)
        if hl > 0.01 and newer <= 8:
            d = ImageDraw.Draw(c); w2, h2 = 900 * sc / 2, 170 * sc / 2
            d.rounded_rectangle((x - w2, y - h2, x + w2, y + h2), 36, outline=GOLD + (int(255 * hl * a),), width=6)
    # sayaç gizli değil: sadece "saymaya devam" ipucu
    if T_STORM + 0.6 < t < T_Q:
        place(c, pill("saymaya devam…", font(IB, 34), (30, 22, 4), GOLD + (255,), 22, 8), W / 2, 1850, 0.9, "c")

def quiz(c, t):
    a = clamp((t - T_Q) / 0.12) * (1 - clamp((t - T_TW) / 0.15))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(190 * a))))
    place(c, native_text("Kaç tane saydın?", 104, WHITE), W / 2, 560, a, "c", back_out((t - T_Q) / 0.3))
    for i, (lt, v) in enumerate((("A", "10"), ("B", "12"), ("C", "14"))):
        ia = clamp((t - T_Q - 0.3 - i * 0.12) / 0.15) * a
        win = i == 1 and t >= T_ANS
        lose = i != 1 and t >= T_ANS
        y = 820 + i * 230
        col = GREEN if win else ((70, 76, 100) if lose else INDIGO)
        put_card(c, 170, y, 740, 190, col, ia * (0.45 if lose else 1), CARD, 0.6 if win else 0.2, 40)
        place(c, letter_badge(lt, col, 110), 210, y + 95, ia * (0.45 if lose else 1), "l")
        sc = (1 + 0.18 * math.exp(-(t - T_ANS) * 7)) if win else 1
        place(c, native_text(v, 120, WHITE), 600, y + 95, ia * (0.45 if lose else 1), "c", sc)
        if win:
            place(c, icon_circle("check", 90, GREEN), 830, y + 95, ia, "c", back_out((t - T_ANS) / 0.3))
    # geri sayım
    if T_Q + 0.7 < t < T_ANS:
        n = 3 - int((t - T_Q - 0.7) / ((T_ANS - T_Q - 0.7) / 3))
        place(c, native_text(str(max(1, n)), 90, GOLD), W / 2, 1600, a, "c")

def twist(c, t):
    if t < T_TW: return
    a = 1 - clamp((t - T_INB) / 0.15)
    if a <= 0.01: return
    # 1) "Ama hepsi aynı soruydu:" üstte, kartlar sarı çerçeveli altta
    ta = clamp((t - T_TW) / 0.12) * a
    place(c, native_text("Ama hepsi", 104, WHITE), W / 2, 300, ta * (1 - clamp((t - T_TW2) / 0.15)), "c")
    place(c, native_text("aynı soruydu.", 104, GOLD), W / 2, 430, ta * (1 - clamp((t - T_TW2) / 0.15)), "c")
    # 2) büyük alıntı
    if t >= T_TW2:
        b = clamp((t - T_TW2) / 0.1) * a
        c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(235 * b))))
        place(c, native_text("“Kargom", 170, WHITE), W / 2, 700, b, "c", lerp(1.5, 1, ease_out((t - T_TW2) / 0.2)))
        place(c, native_text("nerede?”", 170, WHITE), W / 2, 900, b, "c", lerp(1.5, 1, ease_out((t - T_TW2) / 0.2)))
        place(c, pill("× 12", font(DX, 90), (30, 22, 4), GOLD + (255,), 40, 12), W / 2, 1110, b * clamp((t - T_TW2 - 0.3) / 0.1), "c",
              back_out((t - T_TW2 - 0.3) / 0.3))
    if t >= T_TW3:
        b = clamp((t - T_TW3) / 0.12) * a
        place(c, native_text("6 uygulama.", 92, WHITE), W / 2, 1330, b, "c")
        place(c, native_text("12 kez aynı cevap.", 92, CORAL), W / 2, 1450, clamp((t - T_TW3 - 0.35) / 0.12) * a, "c")

ROWS = [("Trendyol", "3 soru"), ("Hepsiburada", "2 soru"), ("ÇiçekSepeti", "2 soru"), ("WhatsApp", "2 mesaj"), ("Instagram", "1 mesaj"), ("E-posta · web siten", "2 e-posta")]
def inbox(c, t):
    a = clamp((t - T_INB) / 0.15) * (1 - clamp((t - T_S6) / 0.1))
    if a <= 0.01: return
    place(c, native_text("Dashtock'ta hepsi", 84, WHITE), W / 2, 210, a, "c")
    place(c, native_text("tek kutuda.", 84, TEAL), W / 2, 315, a, "c")
    x0, y0, w = 90, 420, 900
    put_card(c, x0, y0, w, 1300, None, a, CARD, 0, 36)
    d = ImageDraw.Draw(c)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Gelen kutusu", font(DB, 46)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("12 bekliyor" if t < T_CL1 else ("11 bekliyor" if t < T_CL2 else ("10 bekliyor" if t < T_CL3 else "9 bekliyor")),
                  font(IB, 30), WHITE, (CORAL if t < T_CL1 else TEAL) + (255,), 16, 6), x0 + w - 30, y0 + 60, a, "r")
    for i, (nm, sub) in enumerate(ROWS):
        ra = clamp((t - T_INB - 0.15 - i * 0.07) / 0.15) * a
        y = y0 + 130 + i * 98
        key = nm.split(" ")[0]
        sel = i == 0
        if sel: d.rounded_rectangle((x0 + 16, y - 4, x0 + w - 16, y + 88), 20, fill=(45, 40, 90, int(255 * ra)))
        place(c, app_badge(key, 62), x0 + 36, y + 42, ra, "l")
        place(c, text_img(nm, font(DB, 40)), x0 + 120, y + 26, ra, "l")
        place(c, text_img("“Kargom nerede?” ve benzeri", font(IM, 28), GREY), x0 + 120, y + 66, ra, "l")
        if sel:
            nd = sum(1 for k in (T_CL1, T_CL2, T_CL3) if t >= k + 0.1)
            sub = ("3 soru", "2 soru", "1 soru", "✓ bitti")[nd]
            pc = GREEN if nd == 3 else (50, 58, 90)
            place(c, pill(sub, font(IB, 28), WHITE, pc + (255,), 14, 4), x0 + w - 36, y + 42, ra, "r", 1 + 0.2 * math.exp(-max(0, t - T_CL3 - 0.1) * 8) * (nd == 3))
        else:
            place(c, pill(sub, font(IB, 28), WHITE, (50, 58, 90, 255), 14, 4), x0 + w - 36, y + 42, ra, "r")
    # AI taslak kartı
    ya = y0 + 760
    ba = clamp((t - T_INB - 0.75) / 0.2) * a
    put_card(c, x0 + 30, ya, w - 60, 400, PURPLE, ba, CARD2, 0.4, 30)
    place(c, pill("AI taslak", font(IB, 32), WHITE, PURPLE + (255,), 18, 6), x0 + 60, ya + 50, ba, "l")
    qs = ("Kargom ne zaman gelir?", "Hâlâ kargoya verilmedi mi?", "Sipariş verdim, kargo nerede?", "Sipariş verdim, kargo nerede?")
    qi = sum(1 for k in (T_CL1, T_CL2, T_CL3) if t >= k + 0.2)
    place(c, text_img("Trendyol · " + qs[qi], font(IS, 30), GREY), x0 + 270, ya + 50, ba, "l")
    full = "Merhaba! Siparişin bugün kargoya verildi. Takip numaran: ÖRNEK-12345. İyi günler!"
    starts = (T_INB + 0.9, T_CL1 + 0.2, T_CL2 + 0.2)
    st = max(x for x in starts if t >= x) if t >= starts[0] else starts[0]
    n = int(len(full) * clamp((t - st) / (0.8 if st == starts[0] else 0.25)))
    if t >= T_CL3 + 0.2: n = len(full)
    lines = ["Merhaba! Siparişin bugün kargoya", "verildi. Takip numaran: ÖRNEK-12345.", "İyi günler!"]
    shown = full[:n]; pos = 0
    for li, ln in enumerate(lines):
        part = shown[pos:pos + len(ln)]; pos += len(ln) + 1
        if part: place(c, text_img(part, font(DS, 40), WHITE), x0 + 60, ya + 130 + li * 58, ba, "l")
    # buton
    clicks = (T_CL1, T_CL2, T_CL3)
    done = sum(1 for k in clicks if t >= k + 0.1)
    bcol = GREEN if (t >= T_CL1 and any(0 <= t - k < 0.25 for k in clicks)) else INDIGO
    lab = "Gönderildi ✓" if bcol == GREEN else "Onayla ve gönder"
    bx, by = x0 + w - 60, ya + 330
    place(c, pill(lab, font(DX, 40), WHITE, bcol + (255,), 34, 14), bx, by, ba, "r")
    # imleç
    ca = clamp((t - T_CL1 + 0.6) / 0.2) * a
    tcl = max([(t - k) / 0.35 for k in clicks if t >= k] or [-1])
    draw_cursor(c, bx - 70 + 6 * math.sin(t * 3), by + 22, ca, tcl if tcl <= 1 else -1)
    if done:
        place(c, pill(f"{done} cevap gönderildi · 0 yazı yazıldı" if False else f"{done} cevap gönderildi", font(IB, 32), (10, 30, 20), GREEN + (255,), 18, 6),
              W / 2, ya + 470, a, "c", back_out((t - T_CL1 - 0.1) / 0.3) if done == 1 else 1)

def s6(c, t):
    a = clamp((t - T_S6) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    for i, (w_, col, ti, y) in enumerate((("Mesaj 6 yerden", WHITE, T_S6, 700), ("gelir.", WHITE, T_S6, 840),
                                          ("Cevap tek", TEAL, T_S6B, 1060), ("yerden gider.", TEAL, T_S6B, 1200))):
        wa = clamp((t - ti) / 0.1) * a
        place(c, native_text(w_, 128, col), W / 2, y, wa, "c", lerp(1.5, 1, ease_out((t - ti) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 520, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Web siten + pazaryerlerin", font(DB, 54), WHITE), W / 2, 700, la, "c")
    place(c, text_img("tüm mesajlar tek panelde", font(DB, 54), (205, 210, 232)), W / 2, 772, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, rich(["Senin kaç tane çıktı?", ("emo", "👇")], 70, GOLD), W / 2, 960, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1180, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1290, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (TEAL, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.7, "c")

FLASH = (T_STORM, T_Q, T_ANS, T_TW2, T_INB, T_S6, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    storm(c, t); s1(c, t); quiz(c, t); twist(c, t); inbox(c, t); s6(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for k in range(NN):
        if 0 <= t - nt(k) < 0.2: sh += 4 * math.exp(-(t - nt(k)) * 18)
    for x in (T_ANS, T_TW2, T_S6, T_S6B):
        if 0 <= t - x < 0.25: sh += 10 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.0), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, storm=T_STORM, notifs=[nt(k) for k in range(NN)], q=T_Q, ans=T_ANS, tw=T_TW, tw2=T_TW2, tw3=T_TW3,
                              inb=T_INB, clicks=[T_CL1, T_CL2, T_CL3], s6=T_S6, s6b=T_S6B, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
