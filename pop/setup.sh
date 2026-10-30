#!/usr/bin/env bash
# POP作成に必要なフォント・背景透過ライブラリを準備する（無料のものだけ）
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p fonts
css=$(curl -sS -A "Wget" "https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700;900&family=M+PLUS+Rounded+1c:wght@800&display=swap")
echo "$css" | awk '/font-family/{gsub(/[^A-Za-z0-9]/,"",$2);fam=$2} /font-weight/{gsub(/;/,"",$2);w=$2} /src:/{match($0,/https:[^)]*/);print fam"-"w" "substr($0,RSTART,RLENGTH)}' |
while read -r name url; do
  [ -f "fonts/$name.ttf" ] || curl -sSL -o "fonts/$name.ttf" "$url"
done
python3 -c "import rembg" 2>/dev/null || pip install -q "rembg[cpu]"
ls fonts
