# 今月のおすすめPOP（A3縦）

2026年10月版のデザインを元にしたテンプレート。毎月、内容と季節の色だけを差し替えて作る。

## 毎月の流れ

1. きょんちゃまが次の内容を送る
   ```
   ●最近ハマっているもの
   ●先月の思い出
   ●今月に楽しみなこと
   ①食（食材とおすすめの食材を使った料理名）
   ②トレーニング
   ③ストレッチ
   ```
2. ドライブ「クロードコード/今月のおすすめPOP」にスタッフ写真を入れてもらう（QRコードは保存済み）
   - スマホ部分は10月版と同じデザイン（Instagram画面のスクショ＋QR）。スクショ画像から
     `python3 make_phone.py スクショ.png assets/instagram_qr.png materials/phone_screen.png` で画面を切り出し、QRをくっきり差し替える
3. Claude の作業
   - 文章を整え、材料・作り方・ポイント・説明文を書き足して `months/YYYY-MM.json` を作る
   - スタッフ写真をダウンロードして `photos/` に置き、背景透過：`python3 remove_bg.py photos/元.jpg photos/staff.png`
   - 書き出し：`node render.mjs months/YYYY-MM.json` → A3縦の PDF（印刷用）と PNG（確認用）
   - PDF・PNG をドライブの「今月のおすすめPOP」フォルダにアップロードする

## ファイル

| ファイル | 内容 |
|---|---|
| `template.html` | デザイン本体。月ごとの季節カラー（`THEMES`）もここ |
| `render.mjs` | JSON を流し込んで PDF / PNG を書き出す |
| `make_phone.py` | スマホ画面の切り出しとQR差し替え |
| `remove_bg.py` | スタッフ写真の背景透過（rembg・無料） |
| `setup.sh` | フォントと rembg の準備（新しい環境で最初に1回） |
| `months/*.json` | 毎月の内容 |
| `assets/instagram_qr.png` | Instagram の QR コード |

写真（`photos/`・`materials/`）・フォント・書き出した PDF/PNG は GitHub には置かない（.gitignore 済み）。
料理・トレーニング・ストレッチの写真は任意。JSON の `photo` にパスを入れると表示される。
