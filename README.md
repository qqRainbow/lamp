# Lamp – Bible Companion

Lamp is an installable web app (a PWA). Once someone opens it in their phone's browser, they can add it to the home screen. It then opens full screen with its own icon and keeps working offline for any Bible already opened.

## What's in this folder

| File | What it is |
|---|---|
| `lamp.html` | The whole app. Edit this one. |
| `sw.js` | The service worker, which keeps Lamp working offline. |
| `icons/` | App icons: home screen, install prompt and browser tab. |
| `*.json` | Bibles (KJV, BSB, WEB, Louis Segond 1910), cross-references and Easton's dictionary. |
| `build.py` | Puts everything together into `site/`. |
| `site/` | The finished website, built by `build.py`. It isn't stored in Git, because GitHub builds its own copy. |
| `.github/workflows/pages.yml` | Tells GitHub to build and publish Lamp on every push. |
| `tools/quiz_text.py` | Rebuilds the verse shown after each quiz answer, after adding questions. |
| `church/` | Poster, slide and QR code for church (`py church/make.py`). |
| `CLAUDE.md` | Notes that let a new Claude session (on any computer) pick up the project. |

## Publishing changes (GitHub Pages)

Lamp is published from GitHub. After editing `lamp.html`, push the change:

```
git add -A
git commit -m "Describe the change"
git push
```

GitHub runs `build.py` and updates the live site within a minute or two. You can watch it under the repository's **Actions** tab. Phones get the new version the next time Lamp is opened.

To try the site on your computer first, run `py build.py`, then `py -m http.server 8000 --directory site`, and open http://localhost:8000.

## Other free hosts

### Netlify (no Git)

1. Create a free account at https://app.netlify.com/signup.
2. Go to https://app.netlify.com/drop and drag the **`site`** folder onto the page.
3. Netlify gives you an address like `https://something-random.netlify.app`. Under **Site configuration → Change site name** you can pick a nicer one, such as `lamp-bible.netlify.app`.
4. **To update:** run `py build.py`, open your site in Netlify, go to **Deploys**, and drag the `site` folder onto the drop area again.

Netlify uses HTTPS, which installing and offline mode need.

## Installing on a phone

- **Android (Chrome):** open the site. Then either tap **Install Lamp** under Settings → *Add Lamp to your home screen*, or use the ⋮ menu → **Install app**.
- **iPhone (Safari):** open the site, tap **Share**, then **Add to Home Screen**.

## Notes

- **Where data is kept:** prayers, highlights, notes and plans are stored on each phone, in that browser. A home-screen Lamp on iPhone has its own separate storage from Safari. Use **Settings → Backup** to move data between them, or to a new phone.
- **Moving from the Claude version:** data from the version on claude.ai doesn't carry over automatically. Save a backup there and restore it on the new site.
- **Offline mode:** Lamp downloads each Bible version only the first time you open it, about 4 MB each. After that, it stays on the phone.
- **Fonts:** fonts load from Google Fonts on first use and are then kept offline.
