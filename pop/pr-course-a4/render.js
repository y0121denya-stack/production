const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1123,height:794},deviceScaleFactor:2});
await p.goto('file://'+process.argv[2]);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
await p.screenshot({path:process.argv[3]+'.png'});
await p.pdf({path:process.argv[3]+'.pdf',width:'297mm',height:'210mm',printBackground:true});
await b.close();})();
