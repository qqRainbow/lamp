# Builds Lamp's own website into site/: the app page, its data, icons, the web app manifest and the offline service worker.
# Run from this folder:  py build.py   — then upload the site folder (see README.md).
import hashlib, json, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
DATA = ["kjv.json", "bsb.json", "web.json", "lsg.json", "xref.json", "easton.json"]
ICONS = ["icon-192.png", "icon-512.png", "icon-maskable-512.png", "apple-touch-icon.png", "favicon-32.png"]

def digest(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(p.read_bytes())
    return h.hexdigest()[:10]

page = (ROOT / "lamp.html").read_text(encoding="utf-8")
# lamp.html is written for a Claude artifact, which supplies the document skeleton; drop the Claude-only meta.
page = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Lamp: a Bible companion with verses for how you feel, a full Bible reader in English and French, quizzes, reading plans and a prayer journal.">
<meta name="theme-color" content="#e9edf3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0e1220" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Lamp">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>[hidden] { display: none !important; } body { margin: 0; }</style>
</head>
<body>
"""
FOOT = """
<script>
if ("serviceWorker" in navigator) addEventListener("load", () => navigator.serviceWorker.register("sw.js"));
</script>
</body>
</html>
"""

MANIFEST = {
    "name": "Lamp – Bible Companion",
    "short_name": "Lamp",
    "description": "Verses for how you feel, the Bible in English and French, quizzes, plans and a prayer journal.",
    "id": "./",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0e1220",
    "theme_color": "#0e1220",
    "lang": "en",
    "categories": ["books", "education", "lifestyle"],
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

if SITE.exists():
    shutil.rmtree(SITE)
(SITE / "icons").mkdir(parents=True)
(SITE / "index.html").write_text(HEAD + page + FOOT, encoding="utf-8", newline="\n")
(SITE / "manifest.webmanifest").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
(SITE / ".nojekyll").write_text("")  # GitHub Pages: serve files as they are
for f in DATA:
    shutil.copy2(ROOT / f, SITE / f)
for f in ICONS:
    shutil.copy2(ROOT / "icons" / f, SITE / "icons" / f)

# The service worker's cache names change whenever the files do, so phones pick up new versions by themselves.
shell = ["index.html", "manifest.webmanifest"] + ["icons/" + f for f in ICONS]
sw = (ROOT / "sw.js").read_text(encoding="utf-8")
sw = sw.replace("__SHELL_VERSION__", digest([SITE / f for f in shell])).replace("__DATA_VERSION__", digest([SITE / f for f in DATA]))
(SITE / "sw.js").write_text(sw, encoding="utf-8", newline="\n")

size = sum(p.stat().st_size for p in SITE.rglob("*") if p.is_file())
print(f"Built {SITE} ({size / 1e6:.1f} MB)")
