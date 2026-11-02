# Dashtock günlük video rutini

Her gün bulutta çalışan görevin talimatı. Bilgisayar açık olmak zorunda değil.
Sahibi: Emrullah (Dashtock, dashtock.com — okunuşu "Deştok", ekranda hep "Dashtock").

## Akış (İstanbul saati)
(Not: 3-9 Kasım arası Sosyal Merkez 19:00 dizisiyle çakışmasın diye günlük paylaşım 21:00.)
1. **Depo**: `LUNEX3D/sosyalmerkez` deposunu `medya` dalıyla klonla. Bu klasördeki dosyalar burada.
2. **Konu seç**: `rutin/KONU_GECMISI.md` dosyasına bak, son 10 günde kullanılmamış bir konu seç.
   Kaynak: `rutin/DASHTOCK_OZELLIKLER.md`. Varsa `/mnt/project-files/dashtock-bilgi/` (ayrıntılı program dokümanı) da oku.
   - Kâr/ciro ve "269,99 → 1,97 TL" açısını TEKRAR ETME (çok kullanıldı).
   - Sırayla dolaş: merkezi stok/overselling, e-Fatura, kargo/etiket/desi, AI Soru-Cevap, Buybox, Fiyat Otopilotu,
     Tedarik Zekâsı, Ozon/AliExpress/ÇiçekSepeti, kendi web sitesi (site editörü, tema, alan adı, online ödeme),
     Kategori Merkezi, hakediş, tek panel.
   - 3 paket var: Pazaryeri Pro, Web + Mağaza (sadece kendi web sitesi), Full (web + pazaryeri). Kendi web sitesi tarafını
     düzenli işle; "web siten + pazaryerlerin" dili.
   - Fiyat GÖSTERME. Uydurma rakam yok; örnek sayılarda "ÖRNEK" etiketi. Gerçek panel verisi yok, arayüz çizimi kullan.
   - O güne özel gerçek bir tarih/trend varsa (11.11, Black Friday, yılbaşı) onu kanca yap (WebSearch ile doğrula).
3. **Fikir (en önemli adım)**: Önce sor: "Bir satıcı olarak bunu akışımda görsem ne yapardım?" Reklam gibi durmasın.
   - İlk karede büyük yazıyla kanca (çoğu kişi sessiz izler), 15-22 sn, hızlı kesmeler, tam ekran büyük yazı.
   - Oyun/mantık: "test et kendini", A/B sorusu, hatayı bul, ters psikoloji, döngüsel son, yorum çağrısı.
   - Tek akılda kalan cümle + sonda logo ve dashtock.com.
   - Gizli/bilinçaltı kare YOK (Türkiye'de yasak). Genel optik illüzyon bulmacası YOK (beğenilmedi).
4. **Üret**: 1080x1920, 30 fps, H.264 + AAC, < 30 MB. Örnek kodlar `rutin/ornek/` (Python + Pillow + ffmpeg),
   logo `rutin/dashtock-logo.svg` ve `rutin/logo_mark.png`.
   - Ses: Pazartesi, Çarşamba, Cuma seslendirmeli (ElevenLabs, ses ID `L7EcC4y7BGM74ObLiXoF`, Türkçe, TEK çekim,
     metni önce `estimate_only` ile hesapla, ~1 kredi/karakter; kredi yetmezse sessiz yap). Diğer günler müzik + yazı.
     Seslendirme varsa transkriptle kelime zamanlamasını al, sahneleri sese oturt, müziği altında kıs.
   - Kalite kontrol: 6-8 kare çıkarıp kendin bak. Yazı taşması, okunmayan yazı, Türkçe karakter hatası olmasın.
   - Kapak karesi: kancanın en net okunduğu an (ms cinsinden not al).
5. **Yükle**: `videolar/YYYY-MM-DD.mp4` olarak `medya` dalına commit + push.
   URL: `https://raw.githubusercontent.com/LUNEX3D/sosyalmerkez/medya/videolar/YYYY-MM-DD.mp4`
6. **Planla (Metricool, blogId 7506325, saat dilimi Europe/Istanbul)**: aynı gün 21:00'a AYRI AYRI gönderiler:
   - Instagram REEL (isAiGenerated true), Facebook REEL, TikTok (title dolu, commercialContentOwnBrand true, isAigc true,
     PUBLIC_TO_EVERYONE), YouTube short (title, madeForKids false, isAiGeneratedContent true, public).
   - 21:01 Instagram STORY ve Facebook STORY (metinsiz, aynı video).
   - Her platforma ayrı açıklama: IG/FB kısa merak uyandıran metin + soru + 5-8 hashtag; TikTok kısa; YouTube başlık < 70
     karakter + kısa açıklama. Hitap "sen". Hashtag'lerde Türkçe karakter kullanma (#karzarar, #eticaret, #dashtock,
     #trendyol, #hepsiburada, #pazaryeri, #eticaretsitesi ...). videoCoverMilliseconds = kapak karesi.
   - Hata dönerse (ör. "account limit") tekrar deneme; durumu kayda ve bildirime yaz.
7. **Kaydet**: `rutin/KONU_GECMISI.md` dosyasına satır ekle (tarih | konu | kanca cümlesi | sesli/sessiz | Metricool id'leri | durum),
   commit + push. Varsa `/mnt/project-files/dashtock-otomatik/` klasörüne de video + notu kopyala.
8. **Bildir**: Son mesajında Türkçe, kısa: bugünkü konu, kanca, 21:00'da çıkacağı, beğenmezse Metricool uygulamasından
   silebileceği. Hata varsa açıkça yaz.

## Asla
- Giriş bilgisi/şifre yazma. Gerçek müşteri verisi gösterme. Rakip markaları kötüleme.
- Aynı gün iki kez paylaşma: önce KONU_GECMISI.md'de bugünün tarihi var mı bak; varsa dur.
