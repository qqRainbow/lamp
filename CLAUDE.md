# Lamp – notes for Claude

Lamp is a free Bible companion web app (PWA) in **English and French**, built for the owner's church. It is live at https://qqrainbow.github.io/lamp/ from the repo https://github.com/qqRainbow/lamp. The owner has some coding experience; explain things plainly and test before saying something works.

**Keep this file up to date (the owner asked for this).** The owner switches between a Windows PC and a Mac, and each computer has its own Claude conversations, so this file is the only memory they share. Whenever a piece of work is finished (a feature, a fix, a decision, a change of plan):
1. Add a dated line to the **Work log** at the end of this file: what changed, and anything left unfinished.
2. Update the other sections if they no longer match (layout, conventions, the App Store plan, open decisions).
3. Commit this file together with the change, and push it, so the other computer gets it with `git pull`.

At the start of a session, run `git pull` first, then read the Work log and **Open decisions** to see where things stand.

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
| `build.py` | Builds `site/` (adds the HTML head, manifest, icons, fonts, version date, service worker). `build.py app` builds `app/www` for the iPhone app instead. |
| `site/` | Build output. Not in git; GitHub Actions builds its own copy. |
| `*.json` | `kjv`, `bsb`, `web`, `lsg` Bibles as `[book][chapter][verse]` text (`""` for verses a version omits); `xref.json` cross-references (OpenBible.info, CC BY); `easton.json` dictionary. |
| `privacy.html` | Privacy policy and support page (EN/FR, picks French from the browser or `?lang=fr`), published as `/privacy.html` for the App Store listing. The contact appears once `CONTACT_EMAIL` is set in `build.py`. |
| `icons/` | App icons (made in the browser from Lamp's lamp symbol). |
| `fonts/` | The five fonts as subset `.woff` files (Latin, for English and French) with `fonts.css` and their OFL licences. `build.py` swaps the Google Fonts links in `lamp.html` for `fonts/fonts.css`. |
| `app/` | The App Store app (Capacitor 8, bundle ID `org.ebn.lamp`): `setup.sh`, Capacitor config, icon and launch screen in `assets/`, and `ios/` once created on the Mac. See `app/README.md`. |
| `church/` | Poster, slide and QR code for the church. `py church/make.py` rebuilds them (needs `segno` and Microsoft Edge, so it is Windows-specific as written). |
| `tools/quiz_text.py` | Regenerates `QUIZ_TEXT` (the verse shown after each quiz answer) from the quiz references. |
| `.github/workflows/pages.yml` | On every push to `main`: run `build.py`, deploy `site/` to GitHub Pages. |

`lamp.html` is also the source of an older copy published as a Claude artifact (which still loads Google Fonts, since the links stay in `lamp.html`), which has no document head of its own (`build.py` adds one). Code that checks `window.claude`, and `STANDALONE` (true when the page has a manifest link), keeps that copy working; the website is what matters now.

## Inside lamp.html

- **Strings:** `T = { en: {...}, fr: {...} }`, read with `t(key, ...args)`. Static markup uses `data-t`, `data-t-ph`, `data-t-label`, filled by `applyStatic()`. French typography: a no-break space (`NB`, ` `) before `: ; ? !` and inside « ». Watch that it never turns into a stray `$`.
- **Screens:** `<section class="screen" id="s-...">`, listed in `TABS` and opened with `show(tab)`. Tabs: today, find, bible, quiz, saved (Journal); extra screens: settings, memo, badges, start (First steps).
- **Saved data** (localStorage, all backed up): `lamp.lang`, `lamp.ver.<lang>`, `lamp.saved`, `lamp.marks` (highlights and notes, keyed `lang.book.chapter.verse`), `lamp.prayers`, `lamp.plans`, `lamp.memory`, `lamp.daily`, `lamp.best.<level>[.timed]`, `lamp.badges`, `lamp.chapters`, `lamp.start`, `lamp.shared`, `lamp.pic`, `lamp.look`, `lamp.font`, `lamp.kids`, `lamp.reader`, `lamp.lastread`, `lamp.active` (streak days), `lamp.listen.rate`, `lamp.evening.on` and `lamp.evening` (evening reminder), and a few small settings.
- **Verses:** `remember({ver,b,c,v1,v2,text})` registers a verse so Save, Copy, Share and Read buttons work; `verseCard()` renders one. Books are 0-based (`BOOKS`, `BOOKS_FR`); `parseRef()` reads English or French references.
- **Louis Segond numbering:** LSG counts psalm titles as verses and numbers a few chapters differently (e.g. Jonah 1:17 = Jonas 2:1, 1 Kings 4:21–34 = 1 Rois 5:1–14, Genesis 32 is shifted by one). Precomputed verse tables (`VERSE_TEXT`, `QUIZ_TEXT`, `START_TEXT`) store an `lsgRef`; avoid references that shift unless you map them.
- **Quiz:** `QUIZ` items have `level` (`e`, `m`, `h`, `who`), an `at` reference, and `en`/`fr` as `[question, answer, [3 wrong], note?]`; "Who said it?" items add `quote: {en, fr}`, exact excerpts of the KJV and Louis Segond. 247 questions. When adding questions, check every answer against its verse in both Bibles by script, check quotes word for word, then run `tools/quiz_text.py`.
- **The iPhone app:** `NATIVE` is true inside Capacitor. Then `plugin(name)` returns a Capacitor plugin (Filesystem, Share, LocalNotifications); files leave through `nativeShareFile()` (share sheet); `saveFile()`, `shareText()` and the picture Share button use it; the picture Save button is hidden; `APP_URL` is `STORE_URL` (the App Store page, empty until App Store Connect gives Lamp its id; while empty the app shares text without a link, hides the link in Settings and prints only "Lamp" on pictures — once set, pictures say "Free on the App Store"). The app never mentions the GitHub website; no zooming in the app (viewport and `touch-action` in `build.py`'s `APP_HEAD`); the reminder card shows an On/Off switch (`lamp.remind.on`) and `scheduleReminders()` schedules the next 30 days' verses (`votdFor(date)`); the home-screen card becomes "Share Lamp".
- **Streak:** one streak for the whole app, on Today (`renderStreak()`). A day counts when a chapter's end comes on screen (`watchChapterEnd()`), a plan day is ticked, a First steps lesson is finished, a quiz round is finished or the question of the day is answered. `activeDays()` joins `lamp.active` with the plan, question and lesson dates. One rest day in any 7 keeps it alive (`streakAt()`). The 3/7/30-day badges use `longestStreak()`. It replaced the old reading-plan and question-of-the-day streaks.
- **Read aloud:** Listen button in the reader's Compare row; `startListening()` queues the chapter verse by verse with the phone's own voice (Web Speech, offline, voice picked by `pickVoice()` from the Bible's language, France/Belgium or US/UK first), marks the verse being read, carries on to the next chapter (`nextChapterAloud()`), and stops when the reader goes elsewhere. Player bar `#listen` above the tab bar: play/pause (pause = cancel and resume from the verse), speed 0.8/1/1.25×, stop.
- **Evening streak reminder (app only):** Settings → Daily reminder; `scheduleReminders()` also schedules 30 evenings at `#etime` (ids 2000+), skipping tonight once today counts (rescheduled by `streakMoved()` and when Lamp comes back on screen).
- **Other pieces:** badges (`BADGES`, earned from stored data via `queueBadges()` after any `store()`); "Which book?" game; verse pictures (canvas, 12 backgrounds plus the user's own photo, 5 fonts); First steps (`START_LESSONS`, `START_WORDS`); leave-round prompt and "Back to the quiz" side trip; update bar (`window.lampUpdated`).

## Building and testing

```
py build.py                       # or python3 on a Mac
py -m http.server 8766 --directory site
```

Test at phone size (375×812), in English and French, light and dark, and check the console for errors. The app build can be tried in a browser by serving `app/www` with a pretend `window.Capacitor` (as was done on 2026-10-28); the real test is Xcode's simulator or an iPhone.

The app (on the Mac, in the owner's own Terminal, not Claude's sandbox): `bash app/setup.sh`, then `cd app && npx cap open ios`. Claude's shell on the Mac is a Linux sandbox with no internet and no Xcode, so npm and Xcode steps are the owner's. Claude's built-in browser pane blocks service workers; offline behaviour was tested in headless Edge instead.

## Next: the App Store

The owner has a Mac and plans to pay for the Apple Developer Program (personal or church account still to decide). Plan agreed so far:

Steps 1–4 are done (2026-10-28) and Lamp runs in Xcode's iPhone simulator; still to try on a real iPhone.

1. Wrap the built `site/` with **Capacitor** so everything (Bibles, fonts) is bundled in the app and works offline from the first launch. A thin wrapper around the live URL risks rejection under App Store guideline 4.2.
2. **Self-host the fonts** (Cormorant Garamond, Literata, Figtree, Caveat, Playfair Display; all SIL OFL) instead of Google Fonts, for offline use and a clean privacy label.
3. Add **local notifications** for the daily verse at a chosen time (`@capacitor/local-notifications`, no server needed), replacing the calendar reminder in the native app.
4. Native fixes inside the app: links point to the App Store page (`STORE_URL`, to fill in), never to GitHub; hide the "Add to home screen" card; backups and verse pictures must save through the share sheet or Filesystem (WKWebView ignores download links); the service worker is not needed there.
5. Store listing: screenshots, description (EN/FR), a privacy policy page (can live on GitHub Pages: "Lamp collects no data"), support contact; privacy label "Data Not Collected". Use TestFlight with church members first.

Google Play (TWA via PWABuilder, or the same Capacitor project) is the cheaper sibling; it needs a custom domain for Digital Asset Links and 12 testers for 14 days on a new personal account.

## Open decisions

- **Bundle ID** decided: `org.ebn.lamp` (EBN is the church). Permanent once uploaded.
- **App Store name:** plain "Lamp" is probably taken; something like "Lamp – Bible Companion". Not decided.

- **Apple account:** decided 2026-10-28: personal (shows the owner's legal name as seller); app transfer to a church account stays possible. Was: personal or the church's (needs a free D-U-N-S number; nonprofits can ask for a fee waiver). Turn on automatic renewal: if the membership lapses, all apps leave the store until it is renewed.
- **Own domain** (e.g. lampbible.app, about 10–15 € a year): not bought yet. Needed for Google Play; best done before printing many church posters, since the QR code points to the current address (`church/make.py` regenerates everything).
- **Notifications on the website:** only possible with a small server (e.g. a free Cloudflare Worker). The owner asked only out of curiosity; the calendar reminder stays for now. The App Store version gets local notifications instead.
- **First steps lessons:** suggested that a pastor reads them before they are shared widely; not done yet as far as we know.
- **Still to try on a real phone:** sharing a verse picture through the share sheet, picking a photo as a background, scanning the printed poster's QR code.

## Work log

Newest last. One line per finished piece of work; say what is unfinished.

- **2026-10-27** Built Lamp as a Claude artifact first: verse for how you feel, full Bible reader (KJV, BSB, WEB, Louis Segond) with search and side-by-side comparison, quiz with levels, timed mode, question of the day and "Who said it?", reading plans, prayer journal, highlights and notes, memorize, cross-references and Easton's dictionary, reading look and fonts, kids mode, backup and restore.
- **2026-10-27** Made it a standalone installable website: manifest, icons, offline service worker, `build.py`; published on GitHub Pages with a GitHub Actions workflow.
- **2026-10-27** Bible screens given proper spacing; one verse per line in the reader.
- **2026-10-27** Added the "Which book?" game, Share buttons and 21 badges.
- **2026-10-27** Leaving a quiz round asks first and resets it; "Read" from inside a round is a side trip with a floating "Back to the quiz" button.
- **2026-10-27** Faster updates on phones: the newest page loads when online (3-second limit, then the saved copy), and an "A new version of Lamp is ready" bar appears when an update arrives while Lamp is open.
- **2026-10-27** Church materials in `church/`: bilingual A4 poster, 16:9 slide, QR code.
- **2026-10-28** Verse pictures: 12 backgrounds, the user's own photo, 5 fonts, square or story shape. Quiz grown to 247 questions, every answer checked against KJV and Louis Segond.
- **2026-10-28** "First steps": 8 beginner lessons, a reading guide and 13 key words, in English and French, with a badge.
- **2026-10-28** Polish pass: one-row verse buttons ("Read"), Find example as a hint, back buttons on Badges and First steps, speech-bubble icon for "Who said it?", Settings → About Lamp (version, privacy, credits), compact quiz page.
- **2026-10-28** Owner has a Mac and will pay for the Apple Developer Program; App Store plan written above. Added this file and `tools/quiz_text.py`. Next: start the Capacitor iOS version on the Mac.
- **2026-10-28** App Store version started (Mac): fonts self-hosted in `fonts/` for the website and the app (no more Google Fonts requests on the website; the service worker precaches them); `app/` Capacitor 8 project setup (`setup.sh`, config, 1024 icon, dark launch screen, iPhone only, portrait, photo/camera permission texts); native code in `lamp.html` for the share sheet (backups, pictures, text), daily verse notifications and the "Share Lamp" card; `build.py app`. Fixed stray `$` before French colons in About Lamp. Tested website and app build in a browser with a pretend Capacitor (EN/FR, light/dark, no console errors, no outside requests). Unfinished: the owner installs Xcode and Node, runs `bash app/setup.sh`, then the simulator and a real iPhone; privacy policy page; App Store Connect listing.
- **2026-10-28** First `app/setup.sh` run on the Mac: fixed `build.py` for the Mac's Python 3.9 (`write_unix()` instead of `write_text(newline=)`); dropped `@capacitor/filesystem`'s browser script (it needs `@capacitor/synapse`), Lamp reaches Filesystem through `registerPlugin`. Tested with the real Capacitor 8.5 scripts over a pretend iOS bridge. GitHub push from the Mac works (classic token with `repo` scope, in the Keychain).
- **2026-10-28** Lamp runs in the iOS simulator; owner checked the main features. Fixes on the way: `setup.sh` quotes PlistBuddy values (French apostrophes broke it); `main` gets `env(safe-area-inset-top)` on top, since in the app the top row (with the Settings gear) was hidden under the status bar (0 in a browser, so the website is unchanged). Next: real iPhone, privacy policy page, Apple Developer account, App Store Connect listing.
- **2026-10-28** Owner ran Lamp on their iPhone: works. App only: no pinch or double-tap zoom; no mention of the GitHub site (share text without a link, Settings link hidden, picture shows just "Lamp"). To do: set `STORE_URL` in `lamp.html` once the App Store Connect record exists.
- **2026-10-28** Double-tap zoom confirmed gone on the owner's iPhone (`touch-action: manipulation` on `html` in the app; Capacitor already turns pinch off). Tip: after any change, `bash app/setup.sh` must end with "Done." before pressing ▶; if `app/ios/App/App/public/index.html` is older than the change, the build didn't reach Xcode.
- **2026-10-28** Privacy policy page `privacy.html` (EN/FR, Lamp's look, light/dark), built into the website as https://qqrainbow.github.io/lamp/privacy.html; also serves as the support URL. Unfinished: owner is making a new email for the app; put it in `CONTACT_EMAIL` in `build.py` (the contact section is hidden until then; Apple needs a contact for the support URL).
- **2026-10-28** Apple account decision: enrol as the **church (EBN), organization account** (EBN is a registered legal entity with its own website, domain email and a signatory). Steps: D-U-N-S lookup/request via Apple's tool, Apple Account with 2FA on a church-domain email, enrol as organization, ask for the nonprofit fee waiver (Lamp is free with no in-app purchases), turn on auto-renewal. Not started yet.
- **2026-10-28** Correction: the owner is a churchgoer, not a church officer, so they can't sign for EBN alone. Options: (a) a church leader enrols as Account Holder and adds the owner as Admin in App Store Connect; (b) the owner enrols personally now (own legal name as seller) and transfers the app to a church account later. Not decided; the owner will ask the church.
- **2026-10-28** Decided: the owner enrols **personally** in the Apple Developer Program (own legal name as seller; the app can be transferred to a church account later). Enrolment not done yet.
- **2026-10-28** Contact for the app (privacy/support page, App Store Connect): maxdeveh@gmail.com, set as `CONTACT_EMAIL` in `build.py`.
- **2026-10-29** One streak for the whole app, at the top of Today: reading a chapter to its end, a plan day, a First steps lesson, a finished quiz round or the question of the day each count; one rest day per week. Replaces the two old streaks; streak badges now follow it; earlier activity counts, so existing streaks carry on. Tested in a browser (rules with made-up histories, chapter end, quiz round, toasts, EN/FR, dark). Made in the cloud session while the Mac was offline; delivered as `lamp-streak.bundle`. Idea not done: an evening "keep your streak" notification in the app.
- **2026-10-29** Kids mode: Bible stories on Today are one row that swipes sideways (opens at the next unread story) instead of a 9-row grid; the heading shows "3 of 17 read".
- **2026-10-29** 17 new badges (39 in all): 100- and 365-day streaks, 30 questions of the day, perfect Hard, perfect timed, every game played, 500 chapters, all Psalms, the four Gospels, the New Testament, the whole Bible, 3 plans, 10 prayers, 5 answered, 10 verses learned, all kids' stories, 10 shares. Reading badges count chapters opened (`lamp.chapters`), as before; the streak counts chapters read to the end.
- **2026-10-29** Read aloud in the Bible reader (phone voices, EN/FR, verse highlighting, next chapter, pause, speed) and, in the app, an evening streak reminder that skips days already counted. Tested in a browser with a pretend voice and a pretend iPhone. Still to check on the iPhone: the voices themselves, and that reading stops when the screen locks (WKWebView); a keep-awake option could follow.
- **2026-10-29** Verse sheet redesigned (`#selbar`): docked to the bottom like an iOS sheet, reference with a version chip, bigger colour swatches with a ✓, and 8 icon actions in a 4×2 grid (Save, Note, Copy, Share, Pray, Study, Memorize, Listen). New: Memorize and "Listen from this verse" straight from the sheet. Icons fill in from `ICONS` via `data-icon`.
