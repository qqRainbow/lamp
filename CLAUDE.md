# Lamp – notes for Claude

Lamp is a free Bible companion web app (PWA) in **English and French**, built for the owner's church. It is live at https://qqrainbow.github.io/lamp/ from the repo https://github.com/qqRainbow/lamp. The owner has some coding experience; explain things plainly and test before saying something works.

**Ground rules from the owner**
- Lamp must stay **standalone**: no accounts, no tracking, no features that depend on Claude or any service of ours. Everything a user creates stays on their device (localStorage), with Settings → Back up to move it.
- French matters as much as English. Every user-facing string exists in both.
- Pushing to `main` publishes the live site within a minute or two, so test first. Commits use the owner's GitHub no-reply address (set in the repo's local git config), never a personal email.
- Content is for any church: where churches differ (baptism, communion) the text points to "your church" rather than taking a side.

## How the project is laid out

| Path | What it is |
|---|---|
| `lamp.html` | The whole app: styles, markup, strings and script in one file. Edit this. |
| `sw.js` | Service worker: offline support and updates (newest page when online, saved copy offline). |
| `build.py` | Builds `site/` (adds the HTML head, manifest, icons, version date, service worker). |
| `site/` | Build output. Not in git; GitHub Actions builds its own copy. |
| `*.json` | `kjv`, `bsb`, `web`, `lsg` Bibles as `[book][chapter][verse]` text (`""` for verses a version omits); `xref.json` cross-references (OpenBible.info, CC BY); `easton.json` dictionary. |
| `icons/` | App icons (made in the browser from Lamp's lamp symbol). |
| `church/` | Poster, slide and QR code for the church. `py church/make.py` rebuilds them (needs `segno` and Microsoft Edge, so it is Windows-specific as written). |
| `tools/quiz_text.py` | Regenerates `QUIZ_TEXT` (the verse shown after each quiz answer) from the quiz references. |
| `.github/workflows/pages.yml` | On every push to `main`: run `build.py`, deploy `site/` to GitHub Pages. |

`lamp.html` is also the source of an older copy published as a Claude artifact, which has no document head of its own (`build.py` adds one). Code that checks `window.claude`, and `STANDALONE` (true when the page has a manifest link), keeps that copy working; the website is what matters now.

## Inside lamp.html

- **Strings:** `T = { en: {...}, fr: {...} }`, read with `t(key, ...args)`. Static markup uses `data-t`, `data-t-ph`, `data-t-label`, filled by `applyStatic()`. French typography: a no-break space (`NB`, ` `) before `: ; ? !` and inside « ». Watch that it never turns into a stray `$`.
- **Screens:** `<section class="screen" id="s-...">`, listed in `TABS` and opened with `show(tab)`. Tabs: today, find, bible, quiz, saved (Journal); extra screens: settings, memo, badges, start (First steps).
- **Saved data** (localStorage, all backed up): `lamp.lang`, `lamp.ver.<lang>`, `lamp.saved`, `lamp.marks` (highlights and notes, keyed `lang.book.chapter.verse`), `lamp.prayers`, `lamp.plans`, `lamp.memory`, `lamp.daily`, `lamp.best.<level>[.timed]`, `lamp.badges`, `lamp.chapters`, `lamp.start`, `lamp.shared`, `lamp.pic`, `lamp.look`, `lamp.font`, `lamp.kids`, `lamp.reader`, `lamp.lastread`, and a few small settings.
- **Verses:** `remember({ver,b,c,v1,v2,text})` registers a verse so Save, Copy, Share and Read buttons work; `verseCard()` renders one. Books are 0-based (`BOOKS`, `BOOKS_FR`); `parseRef()` reads English or French references.
- **Louis Segond numbering:** LSG counts psalm titles as verses and numbers a few chapters differently (e.g. Jonah 1:17 = Jonas 2:1, 1 Kings 4:21–34 = 1 Rois 5:1–14, Genesis 32 is shifted by one). Precomputed verse tables (`VERSE_TEXT`, `QUIZ_TEXT`, `START_TEXT`) store an `lsgRef`; avoid references that shift unless you map them.
- **Quiz:** `QUIZ` items have `level` (`e`, `m`, `h`, `who`), an `at` reference, and `en`/`fr` as `[question, answer, [3 wrong], note?]`; "Who said it?" items add `quote: {en, fr}`, exact excerpts of the KJV and Louis Segond. 247 questions. When adding questions, check every answer against its verse in both Bibles by script, check quotes word for word, then run `tools/quiz_text.py`.
- **Other pieces:** badges (`BADGES`, earned from stored data via `queueBadges()` after any `store()`); "Which book?" game; verse pictures (canvas, 12 backgrounds plus the user's own photo, 5 fonts); First steps (`START_LESSONS`, `START_WORDS`); leave-round prompt and "Back to the quiz" side trip; update bar (`window.lampUpdated`).

## Building and testing

```
py build.py                       # or python3 on a Mac
py -m http.server 8766 --directory site
```

Test at phone size (375×812), in English and French, light and dark, and check the console for errors. Claude's built-in browser pane blocks service workers; offline behaviour was tested in headless Edge instead.

## Next: the App Store

The owner has a Mac and plans to pay for the Apple Developer Program (personal or church account still to decide). Plan agreed so far:

1. Wrap the built `site/` with **Capacitor** so everything (Bibles, fonts) is bundled in the app and works offline from the first launch. A thin wrapper around the live URL risks rejection under App Store guideline 4.2.
2. **Self-host the fonts** (Cormorant Garamond, Literata, Figtree, Caveat, Playfair Display; all SIL OFL) instead of Google Fonts, for offline use and a clean privacy label.
3. Add **local notifications** for the daily verse at a chosen time (`@capacitor/local-notifications`, no server needed), replacing the calendar reminder in the native app.
4. Native fixes inside the app: `APP_URL` must stay the public site address; hide the "Add to home screen" card; backups and verse pictures must save through the share sheet or Filesystem (WKWebView ignores download links); the service worker is not needed there.
5. Store listing: screenshots, description (EN/FR), a privacy policy page (can live on GitHub Pages: "Lamp collects no data"), support contact; privacy label "Data Not Collected". Use TestFlight with church members first.

Google Play (TWA via PWABuilder, or the same Capacitor project) is the cheaper sibling; it needs a custom domain for Digital Asset Links and 12 testers for 14 days on a new personal account.
