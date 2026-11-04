// 使い方: node render.js <index.htmlの絶対パス> <出力名(拡張子なし)> [canva]
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1123,height:794},deviceScaleFactor:2});
await p.goto('file://'+process.argv[2]);
if(process.argv[4]==='canva') await p.evaluate(()=>document.body.classList.add('canva'));
await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
await p.screenshot({path:process.argv[3]+'.png'});
await p.pdf({path:process.argv[3]+'.pdf',width:'297mm',height:'210mm',printBackground:true});
await b.close();})();
