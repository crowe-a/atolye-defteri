"""Ortak yardımcı fonksiyonlar: içerik okuma/yazma ve HTML üretimi.

Hem admin/server.py (yerel yönetim paneli) hem de build.py (statik site
üretici) burayı kullanır. Veritabanı yok; her yazı content/posts/ altında
tek bir .json dosyası (düz metin, insan tarafından okunabilir kayıt).
"""

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
POSTS_DIR = CONTENT_DIR / "posts"
IMAGES_DIR = CONTENT_DIR / "images"
ABOUT_FILE = CONTENT_DIR / "about.txt"
DOCS_DIR = BASE_DIR / "docs"
THEME_DIR = BASE_DIR / "theme"

CATEGORIES = {
    "hayvanlar": "Karıncalar & Hayvanlar",
    "muhendislik": "Endüstriyel Yazılım",
}

_TR_MAP = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "I": "i",
    "İ": "i", "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
})


def slugify(text: str) -> str:
    text = text.translate(_TR_MAP).lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "yazi"


def ensure_dirs():
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if not ABOUT_FILE.exists():
        ABOUT_FILE.write_text(
            "Elektrik-elektronik mühendisiyim. Endüstriyel alanda makinelere "
            "yazılım geliştiriyorum; boş zamanlarımda karıncaları ve diğer "
            "hayvanları gözlemlemeyi seviyorum.\n\n"
            "Bu site, bu iki ilgi alanımla ilgili notlarımı tuttuğum kişisel "
            "bir günlük.",
            encoding="utf-8",
        )


def load_posts():
    ensure_dirs()
    posts = []
    for path in POSTS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        data["slug"] = path.stem
        posts.append(data)
    posts.sort(key=lambda p: (p.get("date", ""), p.get("slug", "")), reverse=True)
    return posts


def load_post(slug: str):
    path = POSTS_DIR / f"{slug}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    data["slug"] = slug
    return data


def save_post(slug: str, title: str, category: str, post_date: str, body: str) -> str:
    ensure_dirs()
    if not slug:
        base = slugify(title)
        slug = base
        i = 2
        while (POSTS_DIR / f"{slug}.json").exists():
            slug = f"{base}-{i}"
            i += 1
    data = {
        "title": title.strip(),
        "category": category if category in CATEGORIES else "hayvanlar",
        "date": post_date or date.today().isoformat(),
        "body": body,
    }
    (POSTS_DIR / f"{slug}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return slug


def delete_post(slug: str) -> bool:
    path = POSTS_DIR / f"{slug}.json"
    if path.exists():
        path.unlink()
        return True
    return False


_IMG_MARKER = re.compile(r"^\[gorsel:([^\]|]+)(?:\|(.*))?\]$")


def render_body_html(body: str, image_prefix: str = "../../assets/images/") -> str:
    """Düz metni HTML'e çevirir.

    Boş satırla ayrılmış paragraflar <p> olur. Kendi satırında duran
    `[gorsel:dosya.jpg|Alt yazı]` işareti <figure> bloğuna dönüşür; bu
    işaretin metnin öncesine ya da sonrasına yazılması görseli metnin
    üstünde ya da altında gösterir. Üretilen yazı sayfaları her zaman
    docs/posts/<slug>/ altında (kök dizine göre 2 seviye derinlikte)
    olduğundan image_prefix varsayılan olarak buna göre ayarlıdır.
    """
    import html as _html

    blocks = re.split(r"\n\s*\n", body.strip())
    parts = []
    for block in blocks:
        line = block.strip()
        m = _IMG_MARKER.match(line)
        if m:
            filename = m.group(1).strip()
            caption = (m.group(2) or "").strip()
            fig = f'<figure class="post-figure"><img src="{image_prefix}{_html.escape(filename)}" alt="{_html.escape(caption or filename)}" loading="lazy">'
            if caption:
                fig += f'<figcaption>{_html.escape(caption)}</figcaption>'
            fig += "</figure>"
            parts.append(fig)
        else:
            escaped = _html.escape(block).replace("\n", "<br>")
            parts.append(f"<p>{escaped}</p>")
    return "\n".join(parts)


def excerpt(body: str, length: int = 160) -> str:
    text = re.sub(r"\[gorsel:[^\]]*\]", "", body)
    text = " ".join(text.split())
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "…"
