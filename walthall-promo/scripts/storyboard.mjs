// Playwright QA pass: loads index.html, seeks the GSAP timeline to key moments,
// applies the same data-start/data-duration visibility the HyperFrames runtime uses,
// and screenshots each frame. FFmpeg then tiles them into out/storyboard.png.
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
let playwright;
try {
  playwright = require("playwright");
} catch {
  playwright = require(execFileSync("npm", ["root", "-g"]).toString().trim() + "/playwright");
}

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outDir = path.join(root, "out", "frames");
mkdirSync(outDir, { recursive: true });

const times = (process.argv[2] || "1,3.8,5.6,7.6,10.4,13,15.8,17.6,19.4,21.4,23.4,24.8,26.4,28.2,29")
  .split(",")
  .map(Number);

const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(pathToFileURL(path.join(root, "index.html")).href);
await page.evaluate(() => document.fonts.ready);

const files = [];
for (const [i, t] of times.entries()) {
  await page.evaluate((t) => {
    window.__timelines.main.seek(t, false);
    document.querySelectorAll("[data-start]").forEach((el) => {
      if (el.id === "root" || el.tagName === "AUDIO") return;
      const s = +el.dataset.start;
      const d = +el.dataset.duration;
      el.style.visibility = t >= s && t < s + d ? "visible" : "hidden";
    });
  }, t);
  const f = path.join(outDir, `f${String(i).padStart(2, "0")}_${t.toFixed(2)}s.png`);
  await page.screenshot({ path: f });
  files.push(f);
  console.log("frame", t, "->", path.relative(root, f));
}
await browser.close();

// Tile into a contact sheet (5 columns, 384x216 thumbs)
const cols = 5;
const rows = Math.ceil(files.length / cols);
execFileSync("ffmpeg", [
  "-y", "-loglevel", "error",
  "-framerate", "1", "-pattern_type", "glob", "-i", path.join(outDir, "f*.png"),
  "-vf", `scale=384:216,tile=${cols}x${rows}:padding=6:color=0x0b1712`,
  "-frames:v", "1", path.join(root, "out", "storyboard.png"),
]);
console.log("wrote out/storyboard.png");
