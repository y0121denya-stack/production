// 使い方: node render.mjs months/2026-11.json
// 同じフォルダに .pdf（A3縦・印刷用）と .png（確認用）を書き出す
import { createRequire } from "module";
import fs from "fs";
import path from "path";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const jsonPath = path.resolve(process.argv[2]);
const dir = path.dirname(jsonPath);
const data = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
const toUri = (p) => {
  if (!p) return "";
  const abs = path.resolve(dir, p);
  const ext = path.extname(abs).slice(1).toLowerCase().replace("jpg", "jpeg");
  return `data:image/${ext};base64,${fs.readFileSync(abs).toString("base64")}`;
};
data.photo = toUri(data.photo);
data.qr = toUri(data.qr);
data.phone = toUri(data.phone);
data.food.photo = toUri(data.food.photo);
data.training.photo = toUri(data.training.photo);
data.stretch.photo = toUri(data.stretch.photo);

const here = path.dirname(new URL(import.meta.url).pathname);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1123, height: 1587 }, deviceScaleFactor: 2 });
await page.addInitScript((d) => { window.POP_DATA = d; }, data);
await page.goto("file://" + path.join(here, "template.html"));
await page.evaluate(() => document.fonts.ready);
const out = jsonPath.replace(/\.json$/, "");
await page.screenshot({ path: out + ".png" });
await page.pdf({ path: out + ".pdf", width: "297mm", height: "420mm", printBackground: true, pageRanges: "1" });
await browser.close();
console.log("出力:", out + ".pdf", out + ".png");
