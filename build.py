"""content/ altındaki kayıtlardan docs/ klasörüne statik siteyi üretir.

GitHub Pages, main dalındaki docs/ klasörünü doğrudan sunacak şekilde
ayarlanır. Bu betik her çalıştığında docs/ tamamen yeniden üretilir.
"""

import html
import shutil

from sitelib import (
    ABOUT_FILE,
    BASE_DIR,
    CATEGORIES,
    DOCS_DIR,
    IMAGES_DIR,
    THEME_DIR,
    ensure_dirs,
    excerpt,
    load_posts,
    render_body_html,
)

SITE_TITLE = "Atölye Defteri"
SITE_DESCRIPTION = "Karıncalar, hayvanlar ve endüstriyel yazılım üzerine kişisel bir günlük."

NAV_ITEMS = [
    ("/", "Ana Sayfa"),
    ("/hayvanlar/", "Karıncalar & Hayvanlar"),
    ("/muhendislik/", "Endüstriyel Yazılım"),
    ("/hakkimda/", "Hakkımda"),
]


def relative_url(href: str, depth: int) -> str:
    rel = ("../" * depth) + href.lstrip("/")
    return rel if rel else "./"


def base_layout(title: str, content: str, active: str, depth: int = 0) -> str:
    prefix = "../" * depth
    nav_html = "\n".join(
        f'<a href="{relative_url(href, depth)}"'
        + (' class="active"' if href == active else "")
        + f">{label}</a>"
        for href, label in NAV_ITEMS
    )
    full_title = f"{title} — {SITE_TITLE}" if title else SITE_TITLE
    home_url = relative_url("/", depth)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <h1 class="site-title"><a href="{home_url}">{SITE_TITLE}</a></h1>
    <p class="site-description">{SITE_DESCRIPTION}</p>
    <nav class="site-nav">{nav_html}</nav>
  </div>
</header>
<main>
{content}
</main>
<footer class="site-footer">{SITE_TITLE}</footer>
</body>
</html>
"""


def post_card_html(post: dict, depth: int) -> str:
    prefix = "../" * depth
    cat_label = CATEGORIES.get(post["category"], post["category"])
    return f"""<li class="post-card">
  <div class="post-meta">
    <span>{html.escape(post["date"])}</span>
    <span class="tag {post["category"]}">{html.escape(cat_label)}</span>
  </div>
  <h2><a href="{prefix}posts/{post["slug"]}/">{html.escape(post["title"])}</a></h2>
  <p class="post-excerpt">{html.escape(excerpt(post["body"]))}</p>
</li>"""


def render_post_list(posts: list, depth: int) -> str:
    if not posts:
        return '<p class="empty-state">Henüz yazı yok.</p>'
    items = "\n".join(post_card_html(p, depth) for p in posts)
    return f'<ul class="post-list">\n{items}\n</ul>'


def write(path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_site():
    ensure_dirs()
    posts = load_posts()

    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir(parents=True)
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")

    assets_dir = DOCS_DIR / "assets"
    shutil.copytree(THEME_DIR, assets_dir, dirs_exist_ok=True)
    images_out = assets_dir / "images"
    images_out.mkdir(parents=True, exist_ok=True)
    if IMAGES_DIR.exists():
        for img in IMAGES_DIR.iterdir():
            if img.is_file():
                shutil.copy2(img, images_out / img.name)

    # Ana sayfa
    write(
        DOCS_DIR / "index.html",
        base_layout(
            "",
            f'<h2 class="page-heading">Son Yazılar</h2>\n{render_post_list(posts, 0)}',
            "/",
            depth=0,
        ),
    )

    # Kategori sayfaları
    for slug, label in CATEGORIES.items():
        cat_posts = [p for p in posts if p["category"] == slug]
        write(
            DOCS_DIR / slug / "index.html",
            base_layout(
                label,
                f'<h2 class="page-heading">{html.escape(label)}</h2>\n{render_post_list(cat_posts, 1)}',
                f"/{slug}/",
                depth=1,
            ),
        )

    # Hakkımda
    about_text = ABOUT_FILE.read_text(encoding="utf-8") if ABOUT_FILE.exists() else ""
    about_html = "\n".join(
        f"<p>{html.escape(p)}</p>" for p in about_text.strip().split("\n\n") if p.strip()
    )
    write(
        DOCS_DIR / "hakkimda" / "index.html",
        base_layout(
            "Hakkımda",
            f'<h2 class="page-heading">Hakkımda</h2>\n<div class="about-body">{about_html}</div>',
            "/hakkimda/",
            depth=1,
        ),
    )

    # Yazı sayfaları
    for post in posts:
        cat_label = CATEGORIES.get(post["category"], post["category"])
        body_html = render_body_html(post["body"])
        content = f"""<article class="post">
  <div class="post-meta">
    <span>{html.escape(post["date"])}</span>
    <span class="tag {post["category"]}">{html.escape(cat_label)}</span>
  </div>
  <h1>{html.escape(post["title"])}</h1>
  {body_html}
  <a class="back-link" href="../../">← Tüm yazılar</a>
</article>"""
        write(
            DOCS_DIR / "posts" / post["slug"] / "index.html",
            base_layout(post["title"], content, "", depth=2),
        )

    return len(posts)


if __name__ == "__main__":
    n = generate_site()
    print(f"Site üretildi: {n} yazı -> {DOCS_DIR}")
