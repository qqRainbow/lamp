// Puts each raw screen under a headline, at the App Store's 6.9" size: 440×956 points at 3× = 1320×2868 pixels.
const { chromium } = require("playwright");
const fs = require("fs");
const DIR = process.argv[2];
const CAPTIONS = {
  en: {
    "1-today": ["A verse for every day", "Your verse of the day, and a streak to keep you going"],
    "2-find": ["Verses for how you feel", "Anxious, tired, grateful? Find words for this moment"],
    "3-reader": ["The whole Bible, read aloud", "Four Bibles in English and French"],
    "4-sheet": ["Highlight, note and pray", "Make every verse your own"],
    "5-quiz": ["Learn as you play", "247 questions, three levels and a daily question"],
    "6-picture": ["Share a verse beautifully", "With your own photo or twelve backgrounds"],
    "7-badges": ["Grow a little every day", "Reading plans, 39 badges, and no ads"],
  },
  fr: {
    "1-today": ["Un verset pour chaque jour", "Le verset du jour, et une série pour vous motiver"],
    "2-find": ["Des versets selon ce que vous ressentez", "Inquiet, fatigué, reconnaissant ? Des mots pour ce moment"],
    "3-reader": ["Toute la Bible, lue à voix haute", "Quatre Bibles en français et en anglais"],
    "4-sheet": ["Surlignez, annotez, priez", "Faites de chaque verset le vôtre"],
    "5-quiz": ["Apprenez en jouant", "247 questions, trois niveaux et une question du jour"],
    "6-picture": ["Partagez un verset en beauté", "Avec votre propre photo ou douze fonds"],
    "7-badges": ["Grandir un peu chaque jour", "Plans de lecture, 39 badges, et aucune pub"],
  },
};
(async () => {
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 440, height: 956 }, deviceScaleFactor: 3 });
  for (const lang of ["en", "fr"]) for (const [key, [title, sub]] of Object.entries(CAPTIONS[lang])) {
    const img = "data:image/png;base64," + fs.readFileSync(`${DIR}/raw-${lang}-${key}.png`).toString("base64");
    await page.goto("http://localhost:8767/fonts/fonts.css");  // same origin as the fonts
    await page.setContent(`<!doctype html><html><head><link rel="stylesheet" href="http://localhost:8767/fonts/fonts.css"><style>
      html, body { margin: 0; width: 440px; height: 956px; overflow: hidden; }
      body { background: radial-gradient(120% 60% at 50% 18%, rgba(227,180,90,.28), rgba(227,180,90,0) 60%), linear-gradient(165deg, #1d2748, #0b0f1c 70%);
        color: #f6f1e6; font-family: Figtree, sans-serif; text-align: center; position: relative; }
      .cap { position: absolute; left: 28px; right: 28px; top: 58px; }
      h1 { margin: 0; font: 600 37px/1.08 "Cormorant Garamond", serif; text-wrap: balance; letter-spacing: -.2px; }
      p { margin: 12px auto 0; font: 500 16px/1.35 Figtree, sans-serif; color: rgba(246,241,230,.74); max-width: 340px; text-wrap: balance; }
      .phone { position: absolute; left: 50%; transform: translateX(-50%); top: 226px; width: 336px; height: 727px;
        border-radius: 42px; padding: 9px; background: #05070d; box-shadow: 0 30px 60px rgba(0,0,0,.55), 0 0 0 1px rgba(255,255,255,.12); }
      .phone img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: top; border-radius: 34px; }
    </style></head><body><div class="cap"><h1>${title}</h1><p>${sub}</p></div><div class="phone"><img src="${img}"></div></body></html>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(250);
    await page.screenshot({ path: `${DIR}/lamp-${lang}-${key}.png` });
  }
  await b.close();
})();
