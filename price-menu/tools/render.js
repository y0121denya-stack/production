// HTML を A4 の PDF と PNG に書き出す。
// 使い方: node price-menu/tools/render.js <名前>   例: node price-menu/tools/render.js monthly-campaign
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const name = process.argv[2] || 'price-menu';
  const dir = path.resolve(__dirname, '..');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2 });
  await p.goto('file://' + dir + '/' + name + '.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: dir + '/' + name + '.png' });
  await p.pdf({ path: dir + '/' + name + '.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
  console.log('書き出し完了: ' + name + '.pdf / ' + name + '.png');
})();
