"""月額コースキャンペーン（monthly-campaign.html）の月を切り替える。

見出しの「〇月キャンペーン」と、表の中の日付
（特別価格適用期間の「〇年〇月分会費まで」・申請可能開始日の「〇年〇月1日～」）を
キャンペーン月が進んだ分だけ、すべて同じ月数ずらす。

使い方:
  python3 price-menu/tools/shift_campaign.py 12        # 12月キャンペーンにする
  python3 price-menu/tools/shift_campaign.py 2027-1    # 年をまたぐ場合は年も指定できる
  python3 price-menu/tools/shift_campaign.py 12 --dry  # 変更内容の確認だけ（保存しない）
"""
import re
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / "monthly-campaign.html"


def ym_add(y, m, d):
    t = y * 12 + (m - 1) + d
    return t // 12, t % 12 + 1


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)
    s = HTML.read_text(encoding="utf-8")

    cur = re.search(r'data-campaign="(\d{4})-(\d{1,2})"', s)
    cy, cm = int(cur.group(1)), int(cur.group(2))

    if "-" in args[0]:
        ty, tm = map(int, args[0].split("-"))
    else:
        tm = int(args[0])
        ty = cy if tm >= cm else cy + 1  # 今の月より前の月なら翌年とみなす
    if not 1 <= tm <= 12:
        sys.exit("月は1〜12で指定してください")
    delta = (ty * 12 + tm) - (cy * 12 + cm)
    if delta == 0:
        print(f"すでに {cy}年{cm}月 のキャンペーンです。変更なし。")
        return

    # 見出しの月と、キャンペーン年月の記録
    s = s.replace(f'data-campaign="{cur.group(1)}-{cur.group(2)}"', f'data-campaign="{ty}-{tm}"')
    s, n = re.subn(r'(<span class="mon"><span class="d">)\d{1,2}(</span>)', rf'\g<1>{tm}\g<2>', s)
    assert n == 1, "見出しの月が見つかりません"

    # 表（class="per"）の中の「YYYY年M月」をすべてずらす
    a = s.index('<table class="per">')
    b = s.index("</table>", a)
    changes = []

    def rep(mo):
        y, m = int(mo.group(1)), int(mo.group(2))
        ny, nm = ym_add(y, m, delta)
        changes.append(f"  {y}年{m}月 → {ny}年{nm}月")
        return f"{ny}年{nm}月"

    table = re.sub(r"(\d{4})年(\d{1,2})月", rep, s[a:b])
    s = s[:a] + table + s[b:]

    print(f"{cy}年{cm}月 → {ty}年{tm}月 キャンペーン（{delta:+d}ヶ月）")
    print("\n".join(changes))
    if dry:
        print("（--dry のため保存していません）")
        return
    HTML.write_text(s, encoding="utf-8")
    print("保存しました: " + str(HTML))


if __name__ == "__main__":
    main()
