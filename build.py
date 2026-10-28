# Builds Lamp's own website into site/: the app page, its data, fonts, icons, the web app manifest and the offline service worker.
# Run from this folder:  py build.py   — then upload the site folder (see README.md).
#                        py build.py app   — builds app/www instead, the files bundled into the App Store app (see app/README.md).
import datetime, hashlib, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).parent
APP = len(sys.argv) > 1 and sys.argv[1] == "app"
SITE = ROOT / "app" / "www" if APP else ROOT / "site"
DATA = ["kjv.json", "bsb.json", "web.json", "lsg.json", "xref.json", "easton.json"]
# The contact shown on privacy.html (Apple's privacy policy and support page). While empty, that section is left out.
CONTACT_EMAIL = "maxdeveh@gmail.com"
ICONS = ["icon-192.png", "icon-512.png", "icon-maskable-512.png", "apple-touch-icon.png", "favicon-32.png"]

def write_unix(path, text):
    # Unix line endings on every computer (Path.write_text only takes newline= from Python 3.10, and Macs ship 3.9).
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def digest(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(p.read_bytes())
    return h.hexdigest()[:10]

page = (ROOT / "lamp.html").read_text(encoding="utf-8")
# lamp.html is written for a Claude artifact, which supplies the document skeleton; drop the Claude-only meta.
page = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
# The version shown in Settings → About Lamp: the day the site was built.
page = page.replace("__LAMP_VERSION__", datetime.date.today().strftime("%Y.%m.%d"))
# The fonts come with Lamp (fonts/) rather than from Google Fonts, so they work offline and nothing is fetched from elsewhere.
lines = page.split("\n")
google = [i for i, l in enumerate(lines) if "fonts.googleapis.com" in l or "fonts.gstatic.com" in l]
assert len(google) == 4, "expected the three Google Fonts links in the head and one in loadPicFonts"
lines[google[0]] = '<link rel="stylesheet" href="fonts/fonts.css">'
for i in google[1:3]:
    lines[i] = None
lines[google[3]] = lines[google[3]].replace(lines[google[3]].split('"')[1], "fonts/fonts.css")
page = "\n".join(l for l in lines if l is not None)
FONTS = sorted(p.name for p in (ROOT / "fonts").iterdir() if p.suffix in (".css", ".woff", ".txt"))

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
// Offline support. Lamp also looks for a new version each time it comes back on screen, and offers to switch to it.
if ("serviceWorker" in navigator) addEventListener("load", async () => {
  const hadVersion = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener("controllerchange", () => { if (hadVersion && window.lampUpdated) lampUpdated(); });
  const reg = await navigator.serviceWorker.register("sw.js");
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") reg.update().catch(() => {}); });
});
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

# The App Store app: no zooming (like a native app; the Bible reader has its own text size), no manifest or service worker (the files are already in the app), but Capacitor's scripts, which
# `npm install` in app/ puts in app/node_modules (setup.sh runs it before this).
APP_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="format-detection" content="telephone=no">
<style>[hidden] { display: none !important; } body { margin: 0; } html { -webkit-tap-highlight-color: transparent; touch-action: manipulation; }</style>
"""
CAP_SCRIPTS = {  # node_modules path → name in www/
    "@capacitor/core/dist/capacitor.js": "capacitor.js",
    "@capacitor/share/dist/plugin.js": "cap-share.js",
    "@capacitor/local-notifications/dist/plugin.js": "cap-local-notifications.js",
}

if SITE.exists():
    shutil.rmtree(SITE)
(SITE / "fonts").mkdir(parents=True)
for f in FONTS:
    shutil.copy2(ROOT / "fonts" / f, SITE / "fonts" / f)
if APP:
    mods = ROOT / "app" / "node_modules"
    missing = [m for m in CAP_SCRIPTS if not (mods / m).exists()]
    if missing:
        sys.exit("Missing " + ", ".join(missing) + ". Run `npm install` in the app folder first.")
    for m, name in CAP_SCRIPTS.items():
        shutil.copy2(mods / m, SITE / name)
    scripts = "".join(f'<script src="{name}"></script>\n' for name in CAP_SCRIPTS.values())
    write_unix(SITE / "index.html", APP_HEAD + scripts + "</head>\n<body>\n" + page + "\n</body>\n</html>\n")
    for f in DATA:
        shutil.copy2(ROOT / f, SITE / f)
    size = sum(p.stat().st_size for p in SITE.rglob("*") if p.is_file())
    print(f"Built {SITE} ({size / 1e6:.1f} MB)")
    sys.exit()
(SITE / "icons").mkdir()
write_unix(SITE / "index.html", HEAD + page + FOOT)
(SITE / "manifest.webmanifest").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2), encoding="utf-8")
(SITE / ".nojekyll").write_text("")  # GitHub Pages: serve files as they are
for f in DATA:
    shutil.copy2(ROOT / f, SITE / f)
for f in ICONS:
    shutil.copy2(ROOT / "icons" / f, SITE / "icons" / f)
# The privacy policy, linked from the App Store listing (and used as its support page).
privacy = (ROOT / "privacy.html").read_text(encoding="utf-8")
if CONTACT_EMAIL:
    privacy = privacy.replace("__CONTACT_EMAIL__", CONTACT_EMAIL)
else:
    privacy = re.sub(r"\s*<!-- CONTACT -->.*?<!-- /CONTACT -->", "", privacy, flags=re.S)
assert "__CONTACT_EMAIL__" not in privacy
write_unix(SITE / "privacy.html", privacy)

# The service worker's cache names change whenever the files do, so phones pick up new versions by themselves.
shell = ["index.html", "manifest.webmanifest"] + ["icons/" + f for f in ICONS] + ["fonts/" + f for f in FONTS if not f.endswith(".txt")]
sw = (ROOT / "sw.js").read_text(encoding="utf-8")
sw = sw.replace("__FONT_FILES__", ", ".join(f'"fonts/{f}"' for f in FONTS if not f.endswith(".txt")))
sw = sw.replace("__SHELL_VERSION__", digest([SITE / f for f in shell])).replace("__DATA_VERSION__", digest([SITE / f for f in DATA]))
write_unix(SITE / "sw.js", sw)

size = sum(p.stat().st_size for p in SITE.rglob("*") if p.is_file())
print(f"Built {SITE} ({size / 1e6:.1f} MB)")
