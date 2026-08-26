"""Yerel yönetim paneli.

Çalıştırma: python admin/server.py
Sonra tarayıcıda http://127.0.0.1:8000 adresini açın.

Bu sunucu sadece localhost'ta dinler; içerik ekleme yetkisi bu makineye
fiziksel erişimi olan kişiyle sınırlıdır, ayrı bir kullanıcı/şifre sistemi
yoktur. Kayıtlar content/posts/*.json dosyalarında düz metin olarak durur,
veritabanı kullanılmaz.
"""

import email
import html
import json
import mimetypes
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sitelib import (  # noqa: E402
    BASE_DIR,
    CATEGORIES,
    DOCS_DIR,
    IMAGES_DIR,
    delete_post,
    ensure_dirs,
    load_post,
    load_posts,
    save_post,
)
from build import generate_site  # noqa: E402

HOST = "127.0.0.1"
PORT = 8000


def parse_multipart(body: bytes, content_type: str):
    msg = email.message_from_bytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n\r\n" + body
    )
    fields, files = {}, {}
    if not msg.is_multipart():
        return fields, files
    for part in msg.get_payload():
        name = filename = None
        cd = part.get("Content-Disposition", "")
        for item in cd.split(";"):
            item = item.strip()
            if item.startswith("name="):
                name = item.split("=", 1)[1].strip('"')
            elif item.startswith("filename="):
                filename = item.split("=", 1)[1].strip('"')
        payload = part.get_payload(decode=True) or b""
        if filename:
            files[name] = (filename, payload)
        else:
            fields[name] = payload.decode("utf-8", errors="replace")
    return fields, files


def page(body_html: str, msg: str = "") -> bytes:
    flash = f'<div class="flash">{html.escape(msg)}</div>' if msg else ""
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>Atölye Defteri — Yönetim Paneli</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 780px; margin: 2rem auto; padding: 0 1rem; background:#12130f; color:#eae6d8; }}
  h1 {{ font-size: 1.4rem; }}
  h2 {{ font-size: 1.1rem; border-bottom: 1px solid #333; padding-bottom: .4rem; }}
  label {{ display: block; margin: .9rem 0 .3rem; font-size: .9rem; color:#ccc; }}
  input[type=text], input[type=date], select, textarea {{
    width: 100%; padding: .5rem; background:#1c1d16; color:#eae6d8; border:1px solid #333; border-radius:4px; font-size: .95rem;
  }}
  textarea {{ font-family: ui-monospace, monospace; }}
  button, .btn {{ background:#c98a3c; color:#141400; border:none; padding:.55rem 1rem; border-radius:4px; cursor:pointer; font-weight:600; }}
  button.secondary {{ background:#333; color:#eee; }}
  .hint {{ font-size:.82rem; color:#999; }}
  table {{ width:100%; border-collapse: collapse; margin-top: .5rem; }}
  td, th {{ text-align:left; padding:.4rem .3rem; border-bottom:1px solid #2a2a22; font-size:.9rem; }}
  .actions {{ margin-top:1rem; display:flex; gap:.6rem; align-items:center; }}
  .flash {{ background:#2c3b1f; border:1px solid #4d6b34; padding:.6rem .9rem; border-radius:4px; margin-bottom:1rem; }}
  section {{ margin-bottom: 2.5rem; }}
  a {{ color:#c98a3c; }}
  .row-actions a, .row-actions button {{ margin-right:.5rem; font-size:.85rem; }}
</style>
</head>
<body>
<h1>Atölye Defteri — Yönetim Paneli</h1>
{flash}
{body_html}
</body>
</html>""".encode("utf-8")


def render_form(editing: dict | None) -> str:
    slug = editing["slug"] if editing else ""
    title = editing["title"] if editing else ""
    category = editing["category"] if editing else "hayvanlar"
    date = editing["date"] if editing else ""
    bodytext = editing["body"] if editing else ""

    options = "\n".join(
        f'<option value="{key}"{" selected" if key == category else ""}>{html.escape(label)}</option>'
        for key, label in CATEGORIES.items()
    )
    cancel_link = ' <a href="/" class="btn secondary" style="text-decoration:none;display:inline-block">İptal / Yeni Yazı</a>' if editing else ""

    return f"""
<section>
  <h2>{"Yazıyı Düzenle" if editing else "Yeni Yazı"}</h2>
  <form method="post" action="/save">
    <input type="hidden" name="slug" value="{html.escape(slug)}">
    <label>Başlık</label>
    <input type="text" name="title" value="{html.escape(title)}" required>

    <label>Kategori</label>
    <select name="category">{options}</select>

    <label>Tarih</label>
    <input type="date" name="date" value="{html.escape(date)}">

    <label>Görsel Ekle</label>
    <input type="file" id="image-input" accept="image/*">
    <button type="button" id="upload-btn" class="secondary">Görseli Yükle ve İmlece Ekle</button>
    <span id="upload-status" class="hint"></span>

    <label>Metin</label>
    <textarea name="body" id="body-textarea" rows="14">{html.escape(bodytext)}</textarea>
    <p class="hint">Görseli yükleyip imlecin durduğu yere <code>[gorsel:dosya.jpg|açıklama]</code>
    işareti olarak eklemek için üstteki butonu kullanın. İşareti metnin öncesine koyarsanız
    görsel yazının üstünde, sonrasına koyarsanız altında görünür. Paragraflar arasına boş
    satır bırakın.</p>

    <div class="actions">
      <button type="submit">Kaydet</button>{cancel_link}
    </div>
  </form>
</section>

<script>
document.getElementById('upload-btn').addEventListener('click', async () => {{
  const fileInput = document.getElementById('image-input');
  const statusEl = document.getElementById('upload-status');
  if (!fileInput.files.length) {{ statusEl.textContent = 'Önce bir görsel seçin.'; return; }}
  const fd = new FormData();
  fd.append('image', fileInput.files[0]);
  statusEl.textContent = 'Yükleniyor...';
  try {{
    const res = await fetch('/upload-image', {{ method: 'POST', body: fd }});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Hata');
    const textarea = document.getElementById('body-textarea');
    const marker = '\\n[gorsel:' + data.filename + '|Açıklama yazın]\\n';
    const pos = textarea.selectionStart ?? textarea.value.length;
    textarea.value = textarea.value.slice(0, pos) + marker + textarea.value.slice(pos);
    statusEl.textContent = 'Eklendi: ' + data.filename;
    fileInput.value = '';
  }} catch (e) {{
    statusEl.textContent = 'Hata: ' + e.message;
  }}
}});
</script>
"""


def render_list() -> str:
    posts = load_posts()
    if not posts:
        rows = '<tr><td colspan="4" class="hint">Henüz yazı yok.</td></tr>'
    else:
        rows = "\n".join(
            f"""<tr>
  <td>{html.escape(p["date"])}</td>
  <td>{html.escape(CATEGORIES.get(p["category"], p["category"]))}</td>
  <td>{html.escape(p["title"])}</td>
  <td class="row-actions">
    <a href="/edit?slug={p["slug"]}">Düzenle</a>
    <form method="post" action="/delete" style="display:inline" onsubmit="return confirm('Silinsin mi?')">
      <input type="hidden" name="slug" value="{p["slug"]}">
      <button type="submit" class="secondary">Sil</button>
    </form>
  </td>
</tr>"""
            for p in posts
        )
    return f"""
<section>
  <h2>Yazılar</h2>
  <table>
    <tr><th>Tarih</th><th>Kategori</th><th>Başlık</th><th></th></tr>
    {rows}
  </table>
</section>

<section>
  <h2>Siteyi Güncelle</h2>
  <p class="hint">Önce önizleyin, sorun yoksa GitHub'a gönderin. Yayınlama, statik siteyi
  yeniden üretir ve otomatik olarak commit + push yapar.</p>
  <div class="actions">
    <form method="post" action="/build"><button class="secondary" type="submit">Önizlemeyi Güncelle</button></form>
    <a class="btn" style="text-decoration:none" href="/preview/" target="_blank">Önizlemeyi Aç</a>
    <form method="post" action="/publish" onsubmit="return confirm('GitHub\\'a gönderilsin mi?')"><button type="submit">GitHub'a Gönder</button></form>
  </div>
</section>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "AtolyeDefteriAdmin/1.0"

    def log_message(self, fmt, *args):
        pass

    def _send(self, body: bytes, status=200, content_type="text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self):
        parts = urlsplit(self.path)
        qs = parse_qs(parts.query)

        if parts.path == "/":
            self._send(page(render_form(None) + render_list()))
        elif parts.path == "/edit":
            slug = (qs.get("slug") or [""])[0]
            post = load_post(slug)
            if not post:
                self._redirect("/")
                return
            self._send(page(render_form(post) + render_list()))
        elif parts.path == "/preview" or parts.path == "/preview/":
            self._serve_static(DOCS_DIR / "index.html")
        elif parts.path.startswith("/preview/"):
            rel = parts.path[len("/preview/"):]
            target = (DOCS_DIR / rel).resolve()
            if target.is_dir():
                target = target / "index.html"
            if DOCS_DIR.resolve() not in target.parents and target != DOCS_DIR.resolve():
                self._send(b"Not found", 404, "text/plain")
                return
            self._serve_static(target)
        else:
            self._send(b"Not found", 404, "text/plain")

    def _serve_static(self, path: Path):
        if not path.exists() or not path.is_file():
            self._send(b"Bulunamadi. Once 'Onizlemeyi Guncelle' butonuna basin.", 404, "text/plain; charset=utf-8")
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self._send(path.read_bytes(), 200, ctype)

    def do_POST(self):
        parts = urlsplit(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        content_type = self.headers.get("Content-Type", "")

        if parts.path == "/upload-image":
            self._handle_upload(body, content_type)
            return

        fields = {k: v[0] for k, v in parse_qs(body.decode("utf-8")).items()}

        if parts.path == "/save":
            slug = save_post(
                slug=fields.get("slug", ""),
                title=fields.get("title", ""),
                category=fields.get("category", "hayvanlar"),
                post_date=fields.get("date", ""),
                body=fields.get("body", ""),
            )
            self._redirect("/")
        elif parts.path == "/delete":
            delete_post(fields.get("slug", ""))
            self._redirect("/")
        elif parts.path == "/build":
            generate_site()
            self._send(page(render_form(None) + render_list(), "Önizleme güncellendi."))
        elif parts.path == "/publish":
            self._handle_publish()
        else:
            self._send(b"Not found", 404, "text/plain")

    def _handle_upload(self, body: bytes, content_type: str):
        ensure_dirs()
        _, files = parse_multipart(body, content_type)
        if "image" not in files:
            self._send(json.dumps({"error": "Görsel bulunamadı"}).encode(), 400, "application/json")
            return
        filename, data = files["image"]
        safe_name = Path(filename).name.replace(" ", "-")
        target = IMAGES_DIR / safe_name
        i = 2
        while target.exists():
            target = IMAGES_DIR / f"{Path(safe_name).stem}-{i}{Path(safe_name).suffix}"
            i += 1
        target.write_bytes(data)
        self._send(json.dumps({"filename": target.name}).encode(), 200, "application/json")

    def _handle_publish(self):
        generate_site()
        cmds = [
            ["git", "add", "-A"],
            ["git", "commit", "-m", "Site guncellemesi"],
            ["git", "push"],
        ]
        log = []
        failed = False
        for cmd in cmds:
            result = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)
            log.append(f"$ {' '.join(cmd)}\n{result.stdout}{result.stderr}")
            if result.returncode != 0 and cmd[1] != "commit":
                failed = True
                break
            if result.returncode != 0 and cmd[1] == "commit" and "nothing to commit" not in (result.stdout + result.stderr).lower():
                failed = True
                break
        log_html = "<pre style='white-space:pre-wrap;background:#1c1d16;padding:1rem;border-radius:6px;font-size:.82rem'>" + html.escape("\n\n".join(log)) + "</pre>"
        status = "Yayınlandı." if not failed else "Bir sorun oluştu, günlüğe bakın."
        body = f"<section><h2>{status}</h2>{log_html}<p><a href='/'>Panele dön</a></p></section>"
        self._send(page(body))


def main():
    ensure_dirs()
    generate_site()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Yönetim paneli çalışıyor: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
