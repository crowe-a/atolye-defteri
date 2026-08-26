# Atölye Defteri

Karıncalar, hayvanlar ve endüstriyel yazılım üzerine kişisel günlük. Veritabanı
yok: her yazı `content/posts/` altında düz bir `.json` dosyası olarak durur.
Yerel bir yönetim panelinden yazı/görsel eklersiniz; panel bu kayıtlardan özel
tasarımlı statik bir HTML/CSS sitesi üretip GitHub'a gönderir. Site GitHub
Pages üzerinde herkese açık olarak yayınlanır; içerik ekleme yetkisi sadece bu
bilgisayara erişimi olan kişide (siz) kalır.

## Nasıl çalışır

```
content/posts/*.json   → yazı kayıtları (düz metin, elle de okunabilir)
content/images/        → yüklenen görsellerin orijinalleri
content/about.txt      → "Hakkımda" sayfası metni
theme/style.css        → sitenin tasarımı (istediğiniz gibi düzenleyin)
build.py                → content/ 'dan docs/ klasörüne statik siteyi üretir
docs/                    → GitHub Pages'in yayınladığı, üretilmiş statik site
admin/server.py          → yerel yönetim paneli (yazı ekle/düzenle/sil, yayınla)
```

## Yönetim panelini çalıştırma

```bash
python admin/server.py
```

Tarayıcıda otomatik olarak `http://127.0.0.1:8000` açılır. Bu sunucu sadece
kendi bilgisayarınızda (localhost) çalışır, dışarıdan erişilemez.

Panelden yapabilecekleriniz:

- **Yeni yazı**: başlık, kategori (Karıncalar & Hayvanlar / Endüstriyel
  Yazılım), tarih ve metin girin.
- **Görsel ekleme**: "Görsel Ekle" ile bir dosya seçip "Görseli Yükle ve
  İmlece Ekle" butonuna basın; imlecin bulunduğu yere
  `[gorsel:dosya.jpg|açıklama]` işareti eklenir. Bu işareti metnin öncesine
  yazarsanız görsel yazının üstünde, sonrasına yazarsanız altında görünür.
  Açıklama kısmını doğrudan düzenleyebilirsiniz.
- **Düzenle / Sil**: yazı listesinden.
- **Önizlemeyi Aç**: siteyi yayınlamadan önce yerel önizleme.
- **GitHub'a Gönder**: siteyi yeniden üretir, `git add/commit/push` yapıp
  canlı siteyi günceller.

## İlk kurulumda GitHub Pages ayarı

Bu depo artık statik dosyaları kökte değil `docs/` klasöründe üretiyor.
GitHub'da **Settings → Pages** kısmına gidip "Deploy from a branch" altında
branch olarak **main**, klasör olarak **/docs** seçip kaydedin. Kaydettikten
birkaç dakika sonra site şu adreste olur:

**https://crowe-a.github.io/atolye-defteri/**

## Yerelde site kodunu elle değiştirmek isterseniz

`theme/style.css` dosyasını düzenleyip panelden "Önizlemeyi Güncelle" veya
"GitHub'a Gönder" ile yeniden üretebilirsiniz. Sayfa yapısını (menü, sayfa
şablonları) değiştirmek isterseniz `build.py` içindeki `base_layout` ve ilgili
fonksiyonlara bakın.
