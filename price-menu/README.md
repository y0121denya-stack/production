# 料金表・キャンペーン（price-menu）

絆Style-gym Legame の料金表類。HTML が元データで、PDF・PNG は書き出し結果。

| ファイル | 内容 |
|---|---|
| `price-menu.html` | 料金表（短期集中・月額） |
| `campaign.html` | 短期集中コースのキャンペーン |
| `short.html` | 短期集中コースのみの料金表 |
| `course.html` | 月額コースのコース概要 |
| `monthly-campaign.html` | 月額コースのキャンペーン（毎月更新） |

書き出し: `node price-menu/tools/render.js <名前>`（例: `monthly-campaign`）

## 月額コースキャンペーンの毎月更新ルール

「〇月キャンペーンに修正」と言われたら、次をセットで全て修正する。

1. 見出しの「〇月キャンペーン」を指定の月にする
2. 表の **特別価格適用期間**（「〇年〇月分会費まで」）を、進んだ月数だけ全てずらす
3. 表の **コース変更・休会・退会 申請可能開始日**（「〇年〇月1日～」）も、同じ月数だけ全てずらす

手順:

```bash
python3 -I price-menu/tools/shift_campaign.py 12 --dry   # 変更内容を確認
python3 -I price-menu/tools/shift_campaign.py 12         # 保存
node price-menu/tools/render.js monthly-campaign         # PDF・PNG を書き出し
```

- 今のキャンペーン年月は `monthly-campaign.html` の `<body data-campaign="YYYY-M">` に記録してある。
- 月だけ指定して、それが今の月より前なら翌年とみなす。年をまたぐときは `2027-1` のように年も指定できる。
- 2026年11月版の日付（基準）: A・P・R 入会金無料 = 2027年4月分会費まで／2027年11月1日～、入会金半額 = 2027年1月分会費まで／2027年5月1日～、B = 2027年2月分会費まで／2027年6月1日～、C = 特別価格なし／2027年3月1日～
