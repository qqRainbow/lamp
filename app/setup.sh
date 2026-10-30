#!/bin/bash
# Sets up (or refreshes) Lamp's iPhone app. Run it on the Mac, in Terminal, from the lamp folder:
#   bash app/setup.sh
# It can be run again at any time: after changing lamp.html, it rebuilds the app's files and copies them into Xcode's project.
set -e
cd "$(dirname "$0")"

command -v node >/dev/null || { echo "Node.js is missing: install the LTS version from https://nodejs.org, then run this again."; exit 1; }
command -v xcodebuild >/dev/null && xcodebuild -version >/dev/null 2>&1 || { echo "Xcode is missing or not set up: install it from the App Store, open it once, then run this again."; exit 1; }

echo "1/4  Installing Capacitor (first time only, about a minute)…"
npm install --no-fund --no-audit

echo "2/4  Building the app's files (app/www)…"
(cd .. && python3 build.py app)

if [ ! -d ios ]; then
  echo "3/4  Creating the Xcode project (app/ios)…"
  npx cap add ios
else
  echo "3/4  Xcode project already there."
fi
npx cap sync ios

echo "4/4  Name, icon, permissions…"
PL=ios/App/App/Info.plist
set_plist() {  # key type value
  /usr/libexec/PlistBuddy -c "Delete :$1" "$PL" >/dev/null 2>&1 || true
  /usr/libexec/PlistBuddy -c "Add :$1 $2 \"$3\"" "$PL"  # quoted, so spaces and apostrophes are kept as they are
}
set_plist CFBundleDisplayName string "Lamp"
set_plist CFBundleDevelopmentRegion string "en"
/usr/libexec/PlistBuddy -c "Delete :CFBundleLocalizations" "$PL" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c "Add :CFBundleLocalizations array" -c "Add :CFBundleLocalizations:0 string en" -c "Add :CFBundleLocalizations:1 string fr" -c "Add :CFBundleLocalizations:2 string es" "$PL"
# Picking your own photo for a verse picture, and "Save Image" in the share sheet.
set_plist NSPhotoLibraryUsageDescription string "Lamp uses a photo you choose as the background of a verse picture. / Lamp utilise la photo choisie comme fond d’une image de verset."
set_plist NSPhotoLibraryAddUsageDescription string "Lamp saves your verse pictures to Photos. / Lamp enregistre vos images de versets dans Photos."
set_plist NSCameraUsageDescription string "Take a photo to use as the background of a verse picture. / Prenez une photo comme fond d’une image de verset."
# Lamp uses no encryption of its own, so App Store Connect doesn't ask about export rules on each upload.
set_plist ITSAppUsesNonExemptEncryption bool false
# Portrait only, like the website.
/usr/libexec/PlistBuddy -c "Delete :UISupportedInterfaceOrientations" "$PL" >/dev/null 2>&1 || true
/usr/libexec/PlistBuddy -c "Add :UISupportedInterfaceOrientations array" -c "Add :UISupportedInterfaceOrientations:0 string UIInterfaceOrientationPortrait" "$PL"
set_plist UIStatusBarStyle string "UIStatusBarStyleDefault"

# iPhone only for now (an iPad version needs its own screenshots and every orientation).
sed -i '' 's/TARGETED_DEVICE_FAMILY = "1,2";/TARGETED_DEVICE_FAMILY = 1;/g' ios/App/App.xcodeproj/project.pbxproj

# App icon (one 1024×1024 image; Xcode makes the other sizes) and launch screen.
ICONSET=ios/App/App/Assets.xcassets/AppIcon.appiconset
for f in "$ICONSET"/*.png; do cp assets/icon-1024.png "$f"; done
for f in ios/App/App/Assets.xcassets/Splash.imageset/*.png; do cp assets/splash-2732.png "$f"; done

echo
echo "Done. Next: npx cap open ios   (from the app folder) to open the project in Xcode."
