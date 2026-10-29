// How the App Store screenshots were made (Playwright; run from a machine where it is installed):
//   serve app/www on port 8767, then: node capture.js <dir>  and  node compose.js <dir>
// Raw App Store screens: the app build (pretend iPhone bridge and voice), sample data, 390×844 at 3×.
const { chromium } = require("playwright");
const OUT = process.argv[2];
(async () => {
  const b = await chromium.launch(), errs = [];
  for (const lang of ["en", "fr"]) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, colorScheme: "light" });
    await ctx.addInitScript(() => {
      window.webkit = { messageHandlers: { bridge: { postMessage() {} } } };
      const m = (...n) => n.map(name => ({ name, rtype: "promise" }));
      window.Capacitor = { PluginHeaders: [{ name: "Filesystem", methods: m("writeFile") }, { name: "Share", methods: m("share") },
        { name: "LocalNotifications", methods: m("getPending", "cancel", "schedule", "requestPermissions") }],
        nativePromise: async (pl, me) => me === "getPending" ? { notifications: [] } : {}, nativeCallback: () => "cb" };
      // A voice that never finishes its verse, so the player stays on it.
      Object.defineProperty(window, "speechSynthesis", { value: { speak(u) { if (!window.__first) { window.__first = 1; setTimeout(() => u.onstart && u.onstart(), 10); } }, cancel() { window.__first = 0; },
        getVoices: () => [{ name: "S", lang: "en-US", localService: true }, { name: "T", lang: "fr-FR", localService: true }], addEventListener() {} } });
      Object.defineProperty(window, "SpeechSynthesisUtterance", { value: function (t) { this.text = t; } });
    });
    const p = await ctx.newPage();
    p.on("pageerror", e => errs.push(e.message));
    await p.goto("http://localhost:8767/"); await p.waitForTimeout(600);
    await p.evaluate(l => {
      const day = n => keyOfDay(dayNum(todayKey()) - n), set = (k, v) => localStorage.setItem(k, JSON.stringify(v));
      localStorage.clear();
      set("lamp.lang", l);
      const active = {}; for (let i = 0; i < 12; i++) active[day(i)] = 1; set("lamp.active", active);
      const done = {}; for (let i = 0; i < 9; i++) done[i] = day(9 - i); set("lamp.plans", { gospels: { start: day(9), done } });
      set("lamp.marks", { [`${l === "fr" ? "lsg" : "kjv"}.42.2.15`]: { ver: l === "fr" ? "lsg" : "kjv", b: 42, c: 2, v: 15, hl: "y", at: Date.now() } });
      const badges = {}; ["daily", "streak3", "streak7", "read10", "prayer", "memo1", "share", "firststeps", "perfect", "who", "bookE"].forEach((id, i) => badges[id] = Date.now() - i * 86400000); set("lamp.badges", badges);
      set("lamp.chapters", Array.from({ length: 24 }, (_, i) => "42." + (i % 21)));
      set("lamp.prayers", [
        { id: 1, text: l === "fr" ? "Pour la santé de ma grand-mère" : "For my grandmother's health", at: Date.now() - 3 * 864e5, answered: null },
        { id: 2, text: l === "fr" ? "Sagesse pour mon nouveau travail" : "Wisdom for my new job", at: Date.now() - 9 * 864e5, answered: Date.now() - 864e5 },
      ]);
      set("lamp.start", { done: { welcome: Date.now() - 20 * 864e5 } });
    }, lang);
    await p.reload(); await p.waitForTimeout(1000);
    const shot = async name => { await p.mouse.move(2, 2); await p.waitForTimeout(500); await p.screenshot({ path: `${OUT}/raw-${lang}-${name}.png` }); };
    const hideToast = () => p.evaluate(() => { $("#toast").hidden = true; });

    // 1 Today
    await hideToast(); await shot("1-today");
    // 2 A verse for how you feel
    await p.evaluate(() => show("find")); await p.waitForTimeout(300);
    await p.locator("#chips [data-mood]").nth(0).click(); await p.waitForTimeout(800);
    await p.evaluate(() => { const r = document.querySelector("#s-find .verse, #s-find article"); if (r) scrollTo(0, r.getBoundingClientRect().top + scrollY - 250); });
    await hideToast(); await shot("2-find");
    // 3 Reader, reading aloud John 3:16
    await p.evaluate(() => openChapter(42, 2, null)); await p.waitForTimeout(1200);
    await p.evaluate(() => startListening(15)); await p.waitForTimeout(800);
    await p.evaluate(() => { const el = document.querySelector('.v[data-v="15"]'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 300); });
    await hideToast(); await shot("3-reader");
    await p.evaluate(() => stopListening());
    // 4 Verse sheet
    await p.evaluate(() => { const el = document.querySelector('.v[data-v="15"]'); scrollTo(0, el.getBoundingClientRect().top + scrollY - 120); });
    await p.locator('.v[data-v="15"]').first().click(); await p.waitForTimeout(700);
    await hideToast(); await shot("4-sheet");
    await p.evaluate(() => clearSelection());
    // 5 Quiz question
    await p.evaluate(() => show("quiz")); await p.waitForTimeout(300);
    await p.click('[data-level="m"]'); await p.waitForTimeout(500);
    await hideToast(); await shot("5-quiz");
    await p.evaluate(() => { quiz.over = true; show("today", true); }); await p.waitForTimeout(300);
    // 6 Verse picture
    await p.click("#votd [data-picture]"); await p.waitForTimeout(1500);
    await hideToast(); await shot("6-picture");
    await p.evaluate(() => closePicture()); await p.waitForTimeout(200);
    // 7 Badges
    await p.evaluate(() => show("badges")); await p.waitForTimeout(500);
    await hideToast(); await shot("7-badges");
    await ctx.close();
  }
  console.log("errors:", errs.join(" | ") || "none");
  await b.close();
})();
