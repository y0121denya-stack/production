# ピラティス＆ランニングコース POP（A4横・1枚）

- `index.html` … レイアウト本体（A4横 297×210mm）
- `render.js` … PDF / PNG 書き出し（Playwright）

## 写真素材
Googleドライブ「クロードコード」>「P＆RコースPOP」から取得し、`img/` に置く（リポジトリには入れない）。

| ファイル | ドライブ上の名前 |
|---|---|
| img/p1.jpg | ピラティスコース写真.JPEG |
| img/p3.jpg | ピラティスコース写真3.JPEG |
| img/r1.jpg | ランニングコース写真.JPG |
| img/r2.jpg | ランニングコース写真.JPEG |

## 書き出し
```bash
mkdir -p out && node render.js "$PWD/index.html" "$PWD/out/PRコースPOP_A4横"
```
