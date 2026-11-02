// 使い方: node export_layout.mjs months/2026-11.json
// 書き出したPOPの「部品ごとの位置・色・文字」を months/2026-11.layout.json に保存する
// （Canvaで編集できる .pptx を作るための下準備。続けて build_pptx.py を実行）
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
for (const o of [data, data.food, data.training, data.stretch]) o.photo = toUri(o.photo);
data.qr = toUri(data.qr);
data.phone = toUri(data.phone);

const here = path.dirname(new URL(import.meta.url).pathname);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1123, height: 1587 }, deviceScaleFactor: 4 });
await page.addInitScript((d) => { window.POP_DATA = d; }, data);
await page.goto("file://" + path.join(here, "template.html"));
await page.evaluate(() => document.fonts.ready);

const layout = await page.evaluate(() => {
  const pr = document.getElementById("page").getBoundingClientRect();
  const rel = (r) => ({ x: r.left - pr.left, y: r.top - pr.top, w: r.width, h: r.height });
  const clear = (c) => !c || c === "transparent" || /rgba\(.*,\s*0\)$/.test(c);
  const items = [];
  let order = 0;
  const push = (o, el) => items.push({ ...o, z: parseInt(getComputedStyle(el).zIndex) || 0, order: order++ });

  for (const el of document.querySelectorAll("#page *")) {
    if (el.closest("svg")) {
      if (el.tagName === "svg") push({ kind: "leaf", ...rel(el.getBoundingClientRect()), id: order }, el);
      continue;
    }
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    const r = rel(el.getBoundingClientRect());
    const radius = Math.max(...["TopLeft", "TopRight", "BottomRight", "BottomLeft"].map((k) => parseFloat(cs[`border${k}Radius`]) || 0));
    const radPct = cs.borderTopLeftRadius.endsWith("%");

    // 外枠リング（box-shadow 0 0 0 Npx / outline）
    const sh = cs.boxShadow.match(/^(rgba?\([^)]*\)) 0px 0px 0px (\d+(?:\.\d+)?)px/);
    if (sh) { const s = +sh[2]; push({ kind: "box", x: r.x - s, y: r.y - s, w: r.w + 2 * s, h: r.h + 2 * s, bg: sh[1], radius: radius + s, oval: radPct }, el); }

    if (el.tagName === "IMG") {
      const bw = parseFloat(cs.borderTopWidth) || 0;
      if (bw) push({ kind: "box", ...r, bg: cs.borderTopColor, radius, oval: radPct }, el);
      push({ kind: "img", x: r.x + bw, y: r.y + bw, w: r.w - 2 * bw, h: r.h - 2 * bw, src: el.src, fit: cs.objectFit, pos: cs.objectPosition, radius, oval: radPct }, el);
    } else {
      const bw = cs.borderTopStyle !== "none" ? parseFloat(cs.borderTopWidth) || 0 : 0;
      if (!clear(cs.backgroundColor) || bw) {
        push({ kind: "box", ...r, bg: clear(cs.backgroundColor) ? null : cs.backgroundColor, bw, bc: cs.borderTopColor,
          radius, oval: radPct && Math.abs(r.w - r.h) < 2, opacity: +cs.opacity, clip: cs.clipPath !== "none" ? cs.clipPath : null }, el);
      }
      const bb = cs.borderBottomStyle !== "none" ? parseFloat(cs.borderBottomWidth) || 0 : 0;
      if (bb && !bw) push({ kind: "box", x: r.x, y: r.y + r.h - bb, w: r.w, h: bb, bg: cs.borderBottomColor }, el);
      const g = cs.backgroundImage.match(/linear-gradient\(.*transparent (\d+)%, (rgba?\([^)]*\)) \d+%/);
      if (g) push({ kind: "box", x: r.x, y: r.y + r.h * g[1] / 100, w: r.w, h: r.h * (1 - g[1] / 100), bg: g[2] }, el);
    }
    if (cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) > 0) {
      const o = parseFloat(cs.outlineOffset) + parseFloat(cs.outlineWidth);
      push({ kind: "box", x: r.x - o, y: r.y - o, w: r.w + 2 * o, h: r.h + 2 * o, bg: null, bw: parseFloat(cs.outlineWidth), bc: cs.outlineColor, radius: radius + o, oval: radPct, under: true }, el);
    }

    // 文字：この要素の直下の文字だけを、見た目どおりの改行で1つのテキストに
    const nodes = [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
    if (!nodes.length) continue;
    const lines = []; let L = null, ux0 = 1e9, uy0 = 1e9, ux1 = -1e9, uy1 = -1e9;
    for (const n of nodes) {
      const t = n.textContent;
      for (let i = 0; i < t.length; i++) {
        const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + 1);
        const cr = rg.getClientRects()[0];
        if (!cr || !t[i].trim() && !L) continue;
        const top = Math.round(cr.top);
        if (!L || Math.abs(top - L.top) > 3) { L = { top, s: "" }; lines.push(L); }
        L.s += t[i];
        if (t[i].trim()) { ux0 = Math.min(ux0, cr.left); uy0 = Math.min(uy0, cr.top); ux1 = Math.max(ux1, cr.right); uy1 = Math.max(uy1, cr.bottom); }
      }
      L = null; // <br>で区切られた次の文字ノードは別の行
    }
    push({ kind: "text", x: ux0 - pr.left, y: uy0 - pr.top, w: ux1 - ux0, h: uy1 - uy0,
      text: lines.map((l) => l.s.trim()).join("\n"), size: parseFloat(cs.fontSize), weight: +cs.fontWeight,
      italic: cs.fontStyle === "italic", family: cs.fontFamily, color: cs.color,
      align: cs.textAlign, ls: parseFloat(cs.letterSpacing) || 0, lh: parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3 }, el);
  }
  return { bg: getComputedStyle(document.getElementById("page")).backgroundColor, items };
});

// 植物の線画は透過PNGにして保存
const out = jsonPath.replace(/\.json$/, "");
const leafDir = out + ".leaves";
fs.mkdirSync(leafDir, { recursive: true });
await page.addStyleTag({ content: "html,body,.page{background:transparent!important} .page *:not(svg):not(svg *){visibility:hidden!important}" });
for (const it of layout.items.filter((i) => i.kind === "leaf")) {
  const clip = { x: Math.max(0, it.x), y: Math.max(0, it.y), width: Math.min(1123, it.x + it.w) - Math.max(0, it.x), height: Math.min(1587, it.y + it.h) - Math.max(0, it.y) };
  Object.assign(it, { x: clip.x, y: clip.y, w: clip.width, h: clip.height, file: `${leafDir}/leaf${it.id}.png` });
  await page.screenshot({ path: it.file, clip, omitBackground: true });
}
fs.writeFileSync(out + ".layout.json", JSON.stringify(layout));
await browser.close();
console.log("出力:", out + ".layout.json", layout.items.length, "部品");
