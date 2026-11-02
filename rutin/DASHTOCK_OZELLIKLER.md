# Dashtock: tüm özellikler (dashtock.com taraması, 26 Ekim 2026)

Kaynak: sitemap'teki 31 sayfa Playwright ile okundu (ana sayfa, fiyatlandırma ve "Tüm özellikleri incele" listeleri, 8 entegrasyon sayfası, Amazon Marka Analitiği, SP-API güvenlik, künye, 15 blog yazısı). Ham metinler `site_metinleri/` içinde. Panel taraması (17 Ekim) `/mnt/project-files/dashtock-panel/NOTLAR.md` dosyasında. Burada yazan her şey sitede ya da panelde görüldü; uydurma özellik yok.

**Slogan:** "Ticaretin tüm akışı tek panelde." Pazaryeri, web mağaza, domain, stok, sipariş, kargo ve e-fatura tek operasyon merkezinde; AI destekli analiz ve otomasyon.

## 1. Pazaryeri entegrasyonları (8 kanal)
| Pazaryeri | Sitede yazan yetenekler |
|---|---|
| Trendyol | Ürün listeleme + toplu güncelleme, merkezi stok havuzuyla stok/fiyat senkronu, sipariş çekme, kargo etiketi, iade (claim) takibi, hakediş + komisyonla kâr takibi, **Buybox fiyat koruması**. Bağlantı: Satıcı ID + API Key + API Secret. |
| Hepsiburada | Merchant API ile ürün aktarımı, kategori eşleme, XML ürün yükleme, stok/fiyat, sipariş + kargo, iade, finans mutabakatı, kampanya dönemi zamanlanmış senkron. |
| N11 | Ürün + varyant (renk/beden SKU) yönetimi, stok/fiyat, sipariş, kargo etiketi, fatura yükleme, iade, hakediş mutabakatı. |
| Amazon TR | SP-API bağlantısı, sipariş senkronu, envanter merkezi stokla, FBA/FBM maliyet ayrımı, **Amazon Marka Analitiği** (marka/ASIN/katalog performansı, satış-stok analitiği, karar destek; Pazaryeri Pro ve Full'a dahil). |
| ÇiçekSepeti | Ürün oluşturma, toplu stok/fiyat, sipariş, kargo kodu + etiket, fatura gönderimi, **müşteri soruları**, iade, sezonluk (özel gün) stok planlama. |
| Pazarama | Sipariş çekme + kalem durumu, stok/fiyat, satışa kapatma, kategori/özellik okuyarak ürün aktarımı, fatura linki, ödeme mutabakatı. |
| Ozon (Rusya) | FBS gönderileri çekme, ürün listesi + stok, paket etiketi, kategori ağacıyla ürün aktarımı. |
| AliExpress | SKU bazında stok güncelleme, merkezi stok havuzundan besleme (şimdilik sadece stok). |

Ortak: **merkezi stok havuzu** (bir kanalda satılan ürün diğer kanallardaki stoğa yansır), overselling önleme (sipariş anında stok düşümü, güvenlik stoğu, dakikalık senkron, barkod/SKU denetimi). Panelde 20 pazaryeri listesi görünüyor; sitede 8'i resmî olarak sayılıyor.

## 2. Ürün, stok, fiyat
Katalog, varyant, barkod, **Ürün Yükle** (tek yüklemeyle web sitesi + pazaryerleri), **Kategori Merkezi + akıllı kategori eşleştirme**, **Kanal Fiyatları** (web/master fiyat + her pazaryeri satırı, tek tuşla gönder), fiyat listesi, toplu ürün düzenleme, satın alma, transfer, stok sayımı, barkod etiketi, ürün kişiselleştirme fiyatı.

## 3. Sipariş ve kargo
Web + tüm pazaryeri siparişleri tek listede; iade, iptal, yeniden gönderim, terk edilmiş sepetler; kargo etiketi basımı (A4/termal), kargo takibi.

## 4. Fatura ve finans
E-fatura / e-arşiv / e-irsaliye, **otomatik faturalama** (QNB eSolutions, Sovos, Odeal akışları), hakediş ve mutabakat, gelir-gider, tahsilat görünürlüğü, pazaryeri finans özeti, finans dashboard, gelişmiş kâr/zarar analizi (Full).

## 5. Fiyat ve Buybox zekâsı (Commerce Intelligence)
Buybox Zekâsı (sıra, kazanan teklif, rakip satıcılar, maliyet kırılımı, koruma uyarısı), **Fiyat Otopilotu** (kâr sınırını koruyarak fiyat önerisi), Ürün Kokpiti, Rakip Analizi, Sipariş Zekâsı, **Tedarik Zekâsı** (satış hızına göre alım planı), **Commerce Autopilot** (Full).

## 6. AI ve araştırma
**LysiaBrain AI asistan** / Yapay Zekâ Asistanı (Agent Operasyon Merkezi, "zarar ediyorsun" gibi uyarı kartları; Full'da VIP), **Soru & Cevap AI yanıt taslağı** + hazır yanıtlar, **Fırsat Radarı** (Pazaryeri Pro'da var), **Dashtock Radar / Roketfy pazar araştırması**.

## 7. Kendi web mağazan (Website Builder)
Site editörü, tema + premium temalar, **özel domain bağlama (Domain Center)**, SSL, online ödeme / checkout (Full'da özel checkout), blog modülü, ürün değerlendirmeleri, site analytics, **çoklu dil**, popup/banner, yönlendirme yönetimi.

## 8. Pazarlama
E-posta ve SMS kampanyaları, otomasyon (terk edilmiş sepet e-postası), segmentler, popup, affiliate.

## 9. Raporlar
Satış raporları, canlı takip, dönüşüm hunisi, sipariş özeti, pazaryeri raporları, gelişmiş analitik/raporlar.

## 10. Geliştirici ve güvenlik
API anahtarı yönetimi ve webhook (Full), 256-bit SSL, KVKK uyumlu, 2FA, Google ile giriş, "Beni hatırla" 30 gün. Amazon verisi reklam/profil için kullanılmaz, yetki her an geri alınabilir.

## Paketler (fiyatlandırma sayfası, aylık)
| Paket | Fiyat | Limitler | Öne çıkan |
|---|---|---|---|
| Web + Mağaza Başlangıç | 1.000 TL/ay | 3.000 ürün, 25.000 sipariş, 8 kullanıcı | Web mağaza, domain, online ödeme, pazarlama, site editörü, blog, değerlendirmeler, çoklu dil, premium tema, popup, yönlendirme |
| Pazaryeri Pro | 1.000 TL/ay | 3.500 ürün, 2.000 sipariş, 1 kullanıcı, 10 pazaryeri bağlantısı | Sipariş/ürün/stok, finans özeti, Fırsat Radarı, e-fatura + otomatik fatura, kargo takibi, raporlar, toplu düzenleme, kategori merkezi, akıllı eşleştirme, Roketfy |
| Full: Pazaryeri + Mağaza | 9.765 TL/ay | pratikte sınırsız (999.999 ürün/sipariş, 999 kullanıcı/bağlantı) | Hepsi + gelişmiş kâr/zarar, LysiaBrain AI, Commerce Autopilot, finans dashboard, özel checkout, API + webhook |
14 gün ücretsiz deneme, kredi kartı gerekmez; paket panelden yükseltilebilir. Ödeme, SMS, domain, kargo ve e-belge sağlayıcı ücretleri ayrıdır.

## Şirket
Dashtock, Emrullah SERÇE şahıs işletmesi (İstanbul/Ümraniye), info@dashtock.com, hafta içi 08:00-18:00. Ana sayfada "1.284 aktif kullanıcı" canlı sayacı ve referans olarak Trendyol, Hepsiburada, Amazon, N11, Çiçeksepeti, Sovos, QNB eSolutions logoları var (videoda sayı kullanmadan önce Emrullah'a teyit ettir).

## Şimdiye kadar videolarda kullanılan / hiç kullanılmayanlar
Çok kullanıldı: kâr/ciro (1,97 TL örneği), Buybox, kanal fiyatı, kiracı/kendi site.
Hiç kullanılmadı: merkezi stok + overselling, otomatik e-fatura, toplu kargo etiketi, AI soru-cevap, terk edilmiş sepet e-postası, Tedarik Zekâsı, Fırsat Radarı / Roketfy, Ozon ve AliExpress (yurt dışı), Amazon Marka Analitiği, çoklu dil site, iade takibi, ekip kullanıcıları.

## Kâr dışı video fikirleri
1. **"Son ürün iki kere satıldı"** (overselling): depoda 1 ürün, aynı saniyede Trendyol ve Hepsiburada'dan sipariş, biri iptal, mağaza puanı düşer. Dashtock'ta biri satınca diğerlerinde stok anında 0. Kanca: "Stokta 1 tane vardı. 2 kişi aldı."
2. **"Rusya'dan sipariş geldi"** (Ozon + AliExpress): aynı panelden yurt dışına satış, FBS gönderisi, paket etiketi. Kanca: "Ürünün Moskova'da satılıyor olabilirdi."
3. **"Gece 03:00, 120 fatura"** (otomatik e-fatura + toplu kargo etiketi): sabah satıcı uyanır, faturalar kesilmiş, etiketler hazır. "Uyurken kesilen fatura" ASMR tarzı.
4. **"Müşteri aynı soruyu 40 kez sordu"** (AI Soru & Cevap): bildirim yağmuru, AI taslak cevaplar tek tıkla gider.
5. **"Sepette unutulan 3 ürün"** (terk edilmiş sepet otomasyonu, kendi site): müşteri sepeti bırakır, otomatik e-posta, geri gelir.
6. **"Stok bitmeden haber veren panel"** (Tedarik Zekâsı): en çok satan ürün kampanya ortasında bitiyor; Dashtock satış hızına göre "şu kadar al" der. 11.11 öncesi için uygun.
7. **"Ne satacağını bilmiyorsan"** (Fırsat Radarı + Roketfy): pazar araştırması, fırsat ürünleri.
8. **"Sitem 3 dilde"** (Website Builder çoklu dil + domain): kendi markan yurt dışı müşteriye.
9. **"5 panel, 5 şifre, 5 sekme"** (tek panel): sekme kalabalığından tek ekrana; fiyatı da gösterebilir: 1.000 TL/ay'dan başlayan paketler.
