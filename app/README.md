# Lamp for the App Store

The iPhone app is the same Lamp as the website, with every file (Bibles, fonts) inside the app, so it works offline from the first launch. It is built with [Capacitor](https://capacitorjs.com) (version 8). Bundle ID: **org.ebn.lamp**.

What is different in the app (all in `lamp.html`, behind `NATIVE`):

- **Daily notification** instead of the calendar reminder: Settings → Daily reminder → On. Each notification shows that day's verse; the next 30 days are scheduled, and again every time Lamp opens.
- **Backups and verse pictures** leave through the share sheet (Save to Files, Save Image, AirDrop, Messages…).
- Shared links and pictures point to the website, https://qqrainbow.github.io/lamp/.
- No "Add to home screen" steps and no service worker.

## What's in this folder

| Path | What it is |
|---|---|
| `setup.sh` | Sets everything up and refreshes the app's files. Run it again after every change to `lamp.html`. |
| `package.json`, `capacitor.config.json` | Capacitor's settings. |
| `assets/` | App icon (1024×1024) and launch screen, with the HTML they were drawn from. |
| `www/` | The app's files, built by `py build.py app`. Not in git. |
| `ios/` | The Xcode project, created by `setup.sh` the first time. Kept in git once it exists. |

## First time on the Mac

1. Install **Xcode** from the Mac App Store and open it once (accept the licence, let it install its components; also add an iOS Simulator if it asks).
2. Install **Node.js** (LTS) from https://nodejs.org.
3. In Terminal:
   ```
   cd ~/lamp
   git pull
   bash app/setup.sh
   cd app && npx cap open ios
   ```
4. In Xcode, pick an iPhone simulator at the top and press ▶ (Run). Lamp opens in the simulator.
5. To run it on your own iPhone: plug it in, select it at the top, then in **App → Signing & Capabilities** choose your Team (your Apple ID works before you pay; the paid Developer account is needed for TestFlight and the App Store). On the iPhone, allow the developer under Settings → General → VPN & Device Management.

## After changing lamp.html

```
cd ~/lamp && bash app/setup.sh
```
then press ▶ in Xcode again.

## Still to do before the App Store

- Check on a real iPhone: notifications arrive at the chosen time, the share sheet saves a backup to Files and a picture to Photos, picking your own photo works, restoring a backup works.
- Privacy policy page (on GitHub Pages) and support contact.
- App Store Connect: create the app with bundle ID org.ebn.lamp, name (plain "Lamp" is probably taken; e.g. "Lamp – Bible Companion"), screenshots (6.9" iPhone), description in English and French, privacy label "Data Not Collected".
- Archive in Xcode (Product → Archive) and upload to TestFlight for church members.
