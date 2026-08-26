# Atölye Defteri

Karıncalar, hayvanlar ve endüstriyel yazılım üzerine kişisel günlük. Jekyll ile
statik olarak üretilir, GitHub Pages üzerinde barınır. Sadece bu repoya push
yetkisi olan (yani siz) içerik ekleyebilir; site herkese açık okunur.

## GitHub'a yükleme ve yayınlama

1. GitHub'da yeni, **public** bir repo oluşturun (örn. `atolye-defteri`).
2. Bu klasörde:

   ```bash
   git init
   git add .
   git commit -m "İlk kurulum"
   git branch -M main
   git remote add origin https://github.com/KULLANICI_ADIN/atolye-defteri.git
   git push -u origin main
   ```

3. GitHub'da repo → **Settings → Pages** → "Build and deployment" altında
   Source olarak **Deploy from a branch**, branch olarak **main / (root)**
   seçin ve kaydedin. Birkaç dakika içinde site
   `https://KULLANICI_ADIN.github.io/atolye-defteri/` adresinde yayında olur.
4. `_config.yml` içindeki `url` alanına
   `https://KULLANICI_ADIN.github.io` yazın, `baseurl` alanına da
   `/atolye-defteri` yazın (repo adınız farklıysa ona göre güncelleyin).
   Bunu değiştirdikten sonra tekrar commit + push yapmanız yeterli.

## Yeni yazı ekleme

`_posts/` klasörüne `YIL-AY-GUN-baslik.md` adında bir dosya ekleyin, örnek:

```
_posts/2026-08-27-yeni-gozlem.md
```

İçeriği şu şablonla başlatın:

```markdown
---
layout: post
title: "Yazının başlığı"
date: 2026-08-27 09:00:00 +0300
categories: hayvanlar   # veya: muhendislik
---

Metin buraya.

![Alt metin](/assets/images/DOSYA_ADI.jpg)
*Görselin altına çıkan açıklama metni (italik).*
```

- Görseli metnin **üstüne** koymak için resmi paragraftan önce, **altına**
  koymak için paragraftan sonra yazın.
- `categories` alanı `hayvanlar` ya da `muhendislik` olmalı; menüdeki
  ilgili sayfada otomatik listelenir.
- Görsel dosyalarını `assets/images/` klasörüne koyun, dosya adını
  markdown'daki yol ile eşleştirin.

Değişikliği `git add . && git commit -m "..." && git push` ile
gönderdiğinizde, GitHub Pages siteyi otomatik yeniden derler (1-2 dakika sürer).

## Yerelde önizleme (opsiyonel)

Ruby kuruluysa:

```bash
bundle install
bundle exec jekyll serve
```

`http://localhost:4000` adresinden önizleyebilirsiniz.

## Örnek yazılar

`_posts/` klasöründeki iki örnek yazıyı (`ORNEK-karinca.jpg`,
`ORNEK-panel.jpg` referansları) kendi görsel ve metinlerinizle
değiştirin veya silin.
