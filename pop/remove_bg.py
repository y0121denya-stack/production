"""スタッフ写真の背景を透過する。使い方: python3 remove_bg.py 入力.jpg 出力.png"""
import sys
from PIL import Image
from rembg import new_session, remove

src, dst = sys.argv[1], sys.argv[2]
img = Image.open(src)
out = remove(img, session=new_session("isnet-general-use"), alpha_matting=True)
out = out.crop(out.getbbox())  # 余白を切り詰める
out.save(dst)
print("出力:", dst, out.size)
