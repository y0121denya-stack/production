"""10月版POPのスマホ部分の画像から画面だけを切り出し、QRをくっきりした画像に差し替える。
使い方: python3 make_phone.py スマホ画像.png assets/instagram_qr.png materials/phone_screen.png"""
import sys
from PIL import Image

src, qr_path, dst = sys.argv[1:4]
S = 3  # 印刷用に拡大する倍率
im = Image.open(src).convert("RGB")
w, h = im.size
g = im.convert("L")

# 画面（白い部分）の左右端を、真ん中の高さで探す
# 外側から内側へ：黒い枠を越えて白になったところが画面の端
row = [g.getpixel((x, h // 2)) for x in range(w)]
def edge(xs):
    seen_frame = False
    for x in xs:
        if row[x] < 60:
            seen_frame = True
        elif seen_frame and row[x] > 245:
            return x
left = edge(range(w)) + 3
right = edge(range(w - 1, 0, -1)) - 3
# 上はノッチの下、下は画面の白が終わる手前
col = [g.getpixel((w // 2, y)) for y in range(h)]
top = next(y for y in range(h // 4) if col[y] < 60 and all(c > 240 for c in col[y + 4:y + 12])) + 3
bottom = h - 14
screen = im.crop((left, top, right, bottom))
screen = screen.resize((screen.width * S, screen.height * S), Image.LANCZOS)

# スクショ内のQRの位置（下半分の黒い部分）を探して差し替え
sg = screen.convert("L")
pts = [(x, y) for y in range(int(screen.height * 0.71), int(screen.height * 0.97), 2)
       for x in range(int(screen.width * 0.15), int(screen.width * 0.85), 2) if sg.getpixel((x, y)) < 80]
x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
qr = Image.open(qr_path).convert("L")
qbox = qr.point(lambda v: 255 if v < 128 else 0).getbbox()
qr = qr.crop(qbox).resize((x1 - x0 + 1, y1 - y0 + 1), Image.NEAREST).convert("RGB")
screen.paste(qr, (x0, y0))
screen.save(dst)
print("出力:", dst, screen.size, "QR:", (x0, y0, x1, y1))
