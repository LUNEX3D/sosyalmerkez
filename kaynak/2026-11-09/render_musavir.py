"""Dashtock "Muhasebecin arıyor. Açar mısın?" ~28.9 sn dikey kısa (1080x1920), anlatım Sosyal Merkez'de eklenir.
Konu: Mali Müşavir Merkezi (müşaviri davet et, müşavir kendi portalında satış belgeleri, bekleyen satışlar,
alış/gider faturaları, dönem hazırlığı, Excel aktarımı). Web siten + pazaryerlerin tek yerde.
Akış: gelen arama "Muhasebecim" + A Meşgule at / B Aç + 3-2-1 -> "Meşgule attın." mesaj yağmuru -> dosya kaosu ->
Mali Müşavir Merkezi: davet -> Müşavir Portalı satırları -> "Muhasebecin aramıyorsa, işler yolunda." -> logo, döngü.
Arayüz çizim, veriler ÖRNEK.
Kullanım: python3 render_musavir.py <çıktı.mp4> | kare <sn> <png> | meta
"""
import sys, math, json, subprocess, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yardimci import *
from PIL import Image, ImageDraw

DUR = 28.9
T_CD = 2.8      # geri sayım
T_ANS = 5.0     # cevap + mesajlar
T_MSG = [5.9, 6.6, 7.3, 8.0]
T_KAOS = 9.9
T_INV = 13.0
T_CLICK = 14.9
T_POR = 16.4
T_ROWS = [16.8, 17.4, 18.0, 18.6, 19.4]
T_S = 21.0
T_END = 24.5
T_LOOP = DUR - 0.3

def handset(size, col=WHITE, rot=0):
    def mk():
        s = 4; S = size * s; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.arc((S * .18, S * .18, S * .82, S * .82), 200, 340, fill=col + (255,), width=int(S * .13))
        for ang in (200, 340):
            r = math.radians(ang); cx, cy = S / 2 + S * .29 * math.cos(r), S / 2 + S * .29 * math.sin(r)
            d.rounded_rectangle((cx - S * .1, cy - S * .03, cx + S * .1, cy + S * .14), S // 30, fill=col + (255,))
        im = im.rotate(rot, resample=Image.BICUBIC)
        return im.resize((size, size), Image.LANCZOS)
    return tc(("hs", size, col, rot), mk)

def phone(c, x0, y0, w, h, a):
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((x0 - 14, y0 - 14, x0 + w + 14, y0 + h + 14), 80, fill=(40, 44, 62, int(255 * a)))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 68, fill=(16, 20, 44, int(255 * a)))
    d.rounded_rectangle((x0 + w / 2 - 90, y0 + 22, x0 + w / 2 + 90, y0 + 62), 20, fill=(0, 0, 0, int(255 * a)))

def bubble(text, w=560):
    def mk():
        f = font(DB, 40); t = text_img(text, f)
        bw = min(w, t.size[0] + 56); im = Image.new("RGBA", (bw, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, bw - 1, 95), 30, fill=(44, 52, 84, 250))
        im.alpha_composite(t, (28, 22)); return im
    return tc(("bub", text, w), mk)

MSGS = ["Ay sonu yaklaşıyor", "11.11 faturaları nerede?", "Gider faturaların?", "Pazaryeri dökümleri?"]

def s_call(c, t):
    a = 1 - clamp((t - T_KAOS + 0.12) / 0.12)
    if a <= 0.01: return
    ans = t >= T_ANS
    if not ans:
        place(c, native_text("Muhasebecin arıyor.", 92, WHITE), W / 2, 160, a, "c", lerp(1.35, 1, ease_out(t / 0.25)))
        place(c, native_text("Açar mısın?", 130, GOLD), W / 2, 295, clamp((t - 0.6) / 0.1) * a, "c", lerp(1.5, 1, ease_out((t - 0.6) / 0.2)))
    else:
        v = t - T_ANS
        place(c, rich([("Meşgule attın.", CORAL), ("emo", "😅")], 100), W / 2, 165, a, "c", lerp(1.6, 1, ease_out(v / 0.2)))
        place(c, native_text("Soracağı belli:", 92, WHITE), W / 2, 295, clamp((v - 0.5) / 0.1) * a, "c", back_out((v - 0.5) / 0.3))
    # telefon (titreşim)
    x0, y0, w, h = 200, 400, 680, 1230
    shake = 0 if ans else 7 * math.sin(t * 70) * (0.5 + 0.5 * math.sin(t * 6) > 0.3)
    x0 += shake
    phone(c, x0, y0, w, h, a)
    if not ans:
        place(c, text_img("Gelen arama", font(DS, 36), (200, 205, 230)), x0 + w / 2, y0 + 140, a, "c")
        # avatar + halkalar
        cy = y0 + 380; d = ImageDraw.Draw(c)
        for k in range(3):
            ph = ((t * 0.9 + k / 3) % 1)
            r = 110 + 120 * ph
            d.ellipse((x0 + w / 2 - r, cy - r, x0 + w / 2 + r, cy + r), outline=TEAL + (int(140 * (1 - ph) * a),), width=4)
        d.ellipse((x0 + w / 2 - 110, cy - 110, x0 + w / 2 + 110, cy + 110), fill=INDIGO + (int(255 * a),))
        place(c, text_img("M", font(DX, 120)), x0 + w / 2, cy - 4, a, "c")
        place(c, text_img("Muhasebecim", font(DB, 64)), x0 + w / 2, y0 + 610, a, "c")
        dots = "." * (1 + int(t * 3) % 3)
        place(c, text_img("arıyor" + dots, font(IM, 40), GREY), x0 + w / 2 - tlen("arıyor", font(IM, 40)) / 2 - 4, y0 + 680, a, "l")
        # butonlar
        by = y0 + 960
        for i, (col, rot, lab, L, lc) in enumerate(((RED, 135, "Meşgule at", "A", PINK), (GREEN, 0, "Aç", "B", INDIGO))):
            bx = x0 + w / 2 + (-170 if i == 0 else 170)
            ba = clamp((t - 1.0 - i * 0.2) / 0.15) * a
            pul = 1 + 0.06 * math.sin(t * 8 + i * 3)
            d.ellipse((bx - 80 * pul, by - 80 * pul, bx + 80 * pul, by + 80 * pul), fill=col + (int(255 * ba),))
            place(c, handset(96, WHITE, rot), bx, by, ba, "c")
            place(c, letter_badge(L, lc, 60), bx - 70, by - 70, ba, "c", back_out((t - 1.0 - i * 0.2) / 0.3))
            place(c, text_img(lab, font(DB, 40)), bx, by + 125, ba, "c")
    else:
        v = t - T_ANS
        place(c, text_img("Muhasebecim", font(DB, 46)), x0 + 60, y0 + 140, a, "l")
        place(c, text_img("1 cevapsız arama", font(IM, 32), CORAL), x0 + 60, y0 + 192, a, "l")
        ImageDraw.Draw(c).line((x0 + 40, y0 + 240, x0 + w - 40, y0 + 240), fill=(60, 70, 110, int(255 * a)), width=2)
        for i, m in enumerate(MSGS):
            if t < T_MSG[i]: continue
            u = t - T_MSG[i]
            place(c, bubble(m), x0 + 40, y0 + 300 + i * 130 + 30 * (1 - ease_out(u / 0.25)), clamp(u / 0.12) * a, "tl", back_out(u / 0.3) if u < 0.3 else 1)
        place(c, pill("ÖRNEK", font(IB, 26), (30, 22, 4), GOLD + (255,), 14, 4), x0 + w - 40, y0 + h - 60, a, "r")
    if T_CD <= t < T_ANS:
        seg = (T_ANS - T_CD) / 3
        n = 3 - int((t - T_CD) / seg)
        place(c, native_text("Dürüst ol!", 76, WHITE), W / 2, 1720, 1, "c")
        place(c, native_text(str(max(1, n)), 140, GOLD), W / 2, 1840, 1, "c", 1 + 0.2 * math.exp(-((t - T_CD) % seg) * 8))
    elif ans:
        place(c, text_img("Ay sonu her seferinde aynı sorular.", font(DB, 44), (205, 210, 232)), W / 2, 1750, clamp((t - 8.3) / 0.3) * a, "c")

random.seed(11)
FILES = [("trendyol_rapor.xlsx", GREEN), ("hb_hakedis (2).xlsx", GREEN), ("fatura_SON_son.pdf", CORAL), ("IMG_4021.jpg", BLUE),
         ("n11_dokum.xlsx", GREEN), ("site_siparisler.csv", AMBER), ("gider_ekim.pdf", CORAL), ("IMG_4022.jpg", BLUE),
         ("cicek_ekstre.xlsx", GREEN), ("kargo_faturasi.pdf", CORAL), ("amazon_rapor.xlsx", GREEN), ("IMG_4023.jpg", BLUE)]
FPOS = [(random.uniform(250, 830), 520 + (i * 92) % 1150 + random.uniform(-20, 20), random.uniform(-14, 14)) for i in range(len(FILES))]
def fchip(name, col):
    def mk():
        f = font(DB, 38); t = text_img(name, f)
        w = t.size[0] + 120; im = Image.new("RGBA", (w, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, 95), 22, fill=CARD2 + (250,), outline=col + (255,), width=3)
        d.rounded_rectangle((20, 18, 70, 78), 8, fill=col + (255,))
        ext = name.split(".")[-1].upper()[:3]
        e = text_img(ext, font(IB, 16), (10, 12, 20)); im.alpha_composite(e, (45 - e.size[0] // 2 + 2, 36))
        im.alpha_composite(t, (90, 24)); return im
    return tc(("fc", name, col), mk)
def s_kaos(c, t):
    a = clamp((t - T_KAOS) / 0.12) * (1 - clamp((t - T_INV + 0.1) / 0.12))
    if a <= 0.01: return
    u = t - T_KAOS
    for i, (nm, col) in enumerate(FILES):
        t0 = 0.15 + i * 0.17
        if u < t0: continue
        v = u - t0
        x, y, r = FPOS[i]
        im = fchip(nm, col).rotate(r + 4 * math.sin(t * 3 + i), expand=True, resample=Image.BICUBIC)
        place(c, im, x, y - 260 * (1 - ease_out(v / 0.3)), clamp(v / 0.1) * a, "c", lerp(1.4, 1, ease_out(v / 0.25)))
    c.alpha_composite(Image.new("RGBA", (W, 420), (6, 6, 14, int(200 * a))), (0, 0))
    place(c, native_text("Her panelden", 100, WHITE), W / 2, 150, a, "c", back_out(u / 0.3))
    place(c, native_text("ayrı Excel.", 120, CORAL), W / 2, 285, clamp((u - 0.3) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.3) / 0.2)))
    ka = clamp((u - 1.8) / 0.2) * a
    c.alpha_composite(Image.new("RGBA", (W, 200), (6, 6, 14, int(200 * ka))), (0, 1720))
    place(c, native_text("Ay sonu böyle geçer.", 70, GOLD), W / 2, 1810, ka, "c", back_out((u - 1.8) / 0.3))

def s_inv(c, t):
    a = clamp((t - T_INV) / 0.15) * (1 - clamp((t - T_S) / 0.1))
    if a <= 0.01: return
    u = t - T_INV
    por = t >= T_POR
    if not por:
        place(c, native_text("Bir kez davet et.", 96, WHITE), W / 2, 170, a, "c", back_out(u / 0.3))
        place(c, native_text("Gerisi onda.", 100, TEAL), W / 2, 290, clamp((u - 0.4) / 0.1) * a, "c", back_out((u - 0.4) / 0.3))
    else:
        v = t - T_POR
        place(c, native_text("Muhasebecin", 96, WHITE), W / 2, 170, a, "c", back_out(v / 0.3))
        place(c, native_text("kendisi görür.", 104, TEAL), W / 2, 290, clamp((v - 0.2) / 0.1) * a, "c", back_out((v - 0.2) / 0.3))
    x0, y0, w = 50, 400, 980
    put_card(c, x0, y0, w, 1320, None, a, CARD, 0, 36)
    place(c, mark(52), x0 + 36, y0 + 60, a, "l")
    place(c, text_img("Mali Müşavir Merkezi" if not por else "Müşavir Portalı", font(DB, 46)), x0 + 104, y0 + 58, a, "l")
    place(c, pill("ÖRNEK", font(IB, 28), (30, 22, 4), GOLD + (255,), 16, 5), x0 + w - 30, y0 + 60, a, "r")
    d = ImageDraw.Draw(c)
    if not por:
        fa = clamp((u - 0.3) / 0.2) * a
        place(c, text_img("Müşavirini davet et", font(DB, 54)), x0 + 50, y0 + 190, fa, "l")
        place(c, text_img("SMMM / YMM, ayrı portal, adım adım yetki", font(IM, 32), GREY), x0 + 50, y0 + 255, fa, "l")
        place(c, text_img("E-posta", font(DS, 32), GREY), x0 + 50, y0 + 350, fa, "l")
        d.rounded_rectangle((x0 + 40, y0 + 390, x0 + w - 40, y0 + 500), 22, fill=CARD2 + (int(250 * fa),), outline=(INDIGO if u < 1.9 else (70, 80, 120)) + (int(255 * fa),), width=3)
        full = "muhasebecim@ornek.com"; k = int(clamp((u - 0.6) / 1.1) * len(full))
        typed = full[:k] + ("|" if u < 1.9 and int(t * 4) % 2 == 0 else "")
        place(c, text_img(typed, font(DB, 44)), x0 + 70, y0 + 445, fa, "l")
        place(c, text_img("Yetkiler", font(DS, 32), GREY), x0 + 50, y0 + 580, fa, "l")
        for i, lab in enumerate(["Satış belgeleri", "Gider faturaları", "Dönem hazırlığı"]):
            ra = clamp((u - 0.8 - i * 0.2) / 0.15) * a
            yy = y0 + 650 + i * 100
            d.rounded_rectangle((x0 + 50, yy - 26, x0 + 102, yy + 26), 10, fill=TEAL + (int(255 * ra),))
            place(c, icon_circle("check", 40, TEAL, (8, 30, 26)), x0 + 56, yy, ra, "l")
            place(c, text_img(lab, font(DB, 42)), x0 + 130, yy, ra, "l")
        bt = t >= T_CLICK
        bx0, by0 = x0 + 40, y0 + 1000
        gl = math.exp(-(t - T_CLICK) * 4) if bt else 0
        d.rounded_rectangle((bx0, by0, x0 + w - 40, by0 + 130), 30, fill=mixc(INDIGO, TEAL, 1 if bt else 0) + (int(255 * fa),))
        place(c, text_img("Davet gönderildi ✓" if bt else "Davet gönder", font(DB, 50), (8, 30, 26) if bt else WHITE), W / 2, by0 + 65, fa, "c", 1 + 0.08 * gl)
        if T_CLICK - 0.9 <= t < T_CLICK + 0.8:
            kk = ease_io((t - T_CLICK + 0.9) / 0.8)
            draw_cursor(c, lerp(880, 620, kk), lerp(1780, by0 + 70, kk), a, t - T_CLICK)
    else:
        v = t - T_POR
        place(c, text_img("Kaynak: web siten + pazaryerlerin", font(DS, 34), GREY), x0 + 50, y0 + 150, a, "l")
        rows = [("Satış belgeleri", "e-Fatura · e-Arşiv", "312", TEAL),
                ("Bekleyen satışlar", "faturası kesilecek", "4", AMBER),
                ("Alış / gider faturaları", "dönem içi", "27", INDIGO),
                ("Dönem hazırlığı", "Kasım 2026", "hazır", TEAL)]
        for i, (ttl, sub, val, col) in enumerate(rows):
            ra = clamp((t - T_ROWS[i]) / 0.15) * a
            if ra <= 0.01: continue
            yy = y0 + 230 + i * 190
            d.rounded_rectangle((x0 + 30, yy, x0 + w - 30, yy + 160), 24, fill=CARD2 + (int(240 * ra),), outline=col + (int(170 * ra),), width=3)
            place(c, icon_circle("check", 76, col, (8, 30, 26)), x0 + 60, yy + 80, ra, "l", back_out((t - T_ROWS[i]) / 0.3))
            place(c, text_img(ttl, font(DB, 44)), x0 + 160, yy + 58, ra, "l")
            place(c, text_img(sub, font(IM, 32), GREY), x0 + 160, yy + 110, ra, "l")
            place(c, text_img(val, font(DX, 54), col), x0 + w - 60, yy + 80, ra, "r")
        ea = clamp((t - T_ROWS[4]) / 0.15) * a
        by0 = y0 + 1030
        d.rounded_rectangle((x0 + 40, by0, x0 + w - 40, by0 + 130), 30, fill=CARD2 + (int(250 * ea),), outline=GREEN + (int(255 * ea),), width=4)
        place(c, text_img("Muhasebe programına Excel  ↓", font(DB, 46), GREEN), W / 2, by0 + 65, ea, "c", back_out((t - T_ROWS[4]) / 0.3))
        place(c, text_img("Sen bir şey göndermezsin.", font(DB, 40), (205, 210, 232)), W / 2, y0 + 1240, clamp((t - T_ROWS[4] - 0.4) / 0.3) * a, "c")

def slogan(c, t):
    a = clamp((t - T_S) / 0.08) * (1 - clamp((t - T_END) / 0.1))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(240 * a))))
    u = t - T_S
    # küçük bildirim
    na = clamp((u - 1.7) / 0.2) * a
    if na > 0.01:
        d = ImageDraw.Draw(c); ny = 300 - 40 * (1 - ease_out((u - 1.7) / 0.3))
        d.rounded_rectangle((120, ny, 960, ny + 150), 34, fill=(44, 50, 80, int(250 * na)))
        place(c, icon_circle("check", 76, TEAL, (8, 30, 26)), 150, ny + 75, na, "l")
        place(c, text_img("Muhasebecim", font(DB, 38)), 250, ny + 50, na, "l")
        place(c, rich([("Bu ay her şey tamam", WHITE), ("emo", "👍")], 40), 250, ny + 105, na, "l")
    place(c, native_text("Muhasebecin", 130, WHITE), W / 2, 760, a, "c", lerp(1.5, 1, ease_out(u / 0.18)))
    place(c, native_text("aramıyorsa,", 130, WHITE), W / 2, 910, clamp((u - 0.3) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.3) / 0.18)))
    place(c, native_text("işler yolunda.", 140, GOLD), W / 2, 1110, clamp((u - 0.9) / 0.1) * a, "c", lerp(1.5, 1, ease_out((u - 0.9) / 0.18)))

def end_scene(c, t):
    a = clamp((t - T_END) / 0.15) * (1 - clamp((t - T_LOOP) / 0.12))
    if a <= 0.01: return
    c.alpha_composite(Image.new("RGBA", (W, H), (6, 6, 14, int(244 * a))))
    place(c, logo(120), W / 2, 470, a, "c", back_out((t - T_END) / 0.4))
    la = clamp((t - T_END - 0.25) / 0.25) * a
    place(c, text_img("Kendi web siten + pazaryerlerin", font(DB, 56), WHITE), W / 2, 650, la, "c")
    place(c, text_img("ve muhasebecin, tek panelde", font(DB, 46), (205, 210, 232)), W / 2, 725, la, "c")
    ra = clamp((t - T_END - 0.55) / 0.2) * a
    place(c, native_text("Sen açar", 84, GOLD), W / 2, 920, ra, "c")
    place(c, rich([("mıydın?", GOLD), ("emo", "👇")], 84, GOLD), W / 2, 1030, ra, "c")
    fa = clamp((t - T_END - 0.9) / 0.25) * a
    place(c, text_img("14 gün ücretsiz · kredi kartı gerekmez", font(DB, 42), (200, 196, 232)), W / 2, 1230, fa, "c")
    place(c, text_img("dashtock.com", font(DX, 84), GOLD), W / 2, 1340, fa, "c")

def bgfx(c, t):
    for i, (col, cx, cy) in enumerate(((INDIGO, 200, 400), (CORAL if t < T_INV else TEAL, 900, 1500))):
        b, r = blob(col, 380)
        place(c, b, cx + 60 * math.sin(t * 0.6 + i * 2), cy + 50 * math.cos(t * 0.5 + i), 0.6, "c")

FLASH = (0.0, T_ANS, T_KAOS, T_INV, T_S, T_END)
def frame(t):
    c = BG.copy()
    bgfx(c, t)
    s_call(c, t); s_kaos(c, t); s_inv(c, t); slogan(c, t); end_scene(c, t)
    for tc_ in FLASH:
        if 0 <= t - tc_ < 0.15: c.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - tc_) / 0.15) * 0.14))))
    out = c.convert("RGB")
    sh = 0
    for x in [T_ANS, T_KAOS + 0.3, T_CLICK, T_S, T_S + 0.3, T_S + 0.9]:
        if 0 <= t - x < 0.25: sh += 9 * math.exp(-(t - x) * 14)
    if sh > 0.5:
        s = 1 + sh / 300; nw, nh = int(W * s), int(H * s)
        out = out.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    if t >= T_LOOP:
        out = Image.blend(out, frame(0.7), clamp((t - T_LOOP) / 0.3))
    return out

if __name__ == "__main__":
    if sys.argv[1] == "meta":
        print(json.dumps(dict(dur=DUR, cd=T_CD, ans=T_ANS, msgs=T_MSG, kaos=T_KAOS, files=[T_KAOS + 0.15 + i * 0.17 for i in range(len(FILES))],
                              inv=T_INV, click=T_CLICK, por=T_POR, rows=T_ROWS, s=T_S, end=T_END, loop=T_LOOP))); sys.exit()
    if sys.argv[1] == "kare":
        frame(float(sys.argv[2])).save(sys.argv[3]); sys.exit()
    outp = sys.argv[1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
    for n in range(int(round(DUR * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); p.wait()
