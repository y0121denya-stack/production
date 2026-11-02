"""export_layout.mjs の結果から、Canvaで部品ごとに編集できる .pptx（A3縦）を作る。
使い方: python3 build_pptx.py months/2026-11.layout.json  → months/2026-11.pptx"""
import base64
import io
import json
import re
import sys

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

src = sys.argv[1]
layout = json.load(open(src))
EMU = 10692000 / 1123  # A3縦 297mm を 1123px として換算
E = lambda v: Emu(int(round(v * EMU)))


def rgb(c):
    n = [float(v) for v in re.findall(r"[\d.]+", c)]
    return n[:3], (n[3] if len(n) > 3 else 1.0)


PAGE_BG, _ = rgb(layout["bg"])


def color(c, opacity=1.0):
    (r, g, b), a = rgb(c)
    a *= opacity  # 透明度は背景色と混ぜて再現
    return RGBColor(*[round(v * a + bg * (1 - a)) for v, bg in zip((r, g, b), PAGE_BG)])


prs = Presentation()
prs.slide_width, prs.slide_height = E(1123), E(1587)
slide = prs.slides.add_slide(prs.slide_layouts[6])
sh = slide.shapes

bg = sh.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = color(layout["bg"]); bg.line.fill.background(); bg.name = "背景"


def add_box(it):
    w, h = it["w"], it["h"]
    if it.get("clip", "") and it["clip"].startswith("polygon"):
        pts = [tuple(float(v) for v in re.findall(r"[\d.]+", p)) for p in it["clip"][8:-1].split(",")]
        pts = [(it["x"] + px / 100 * w, it["y"] + py / 100 * h) for px, py in pts]
        fb = sh.build_freeform(E(pts[0][0]), E(pts[0][1]), scale=1.0)
        fb.add_line_segments([(E(x), E(y)) for x, y in pts[1:]], close=True)
        s = fb.convert_to_shape()
    else:
        r = it.get("radius", 0)
        kind = MSO_SHAPE.OVAL if it.get("oval") else (MSO_SHAPE.ROUNDED_RECTANGLE if r > 0.5 else MSO_SHAPE.RECTANGLE)
        s = sh.add_shape(kind, E(it["x"]), E(it["y"]), E(w), E(h))
        if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
            s.adjustments[0] = min(0.5, r / min(w, h))
    if it.get("bg"):
        s.fill.solid(); s.fill.fore_color.rgb = color(it["bg"], it.get("opacity", 1))
    else:
        s.fill.background()
    if it.get("bw"):
        s.line.color.rgb = color(it["bc"]); s.line.width = Pt(it["bw"] * 0.75)
    else:
        s.line.fill.background()
    style = s._element.find(qn("p:style"))  # 既定の影・枠線の設定を外す
    if style is not None:
        s._element.remove(style)


def load_img(uri):
    return Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1]))).convert("RGBA")


def add_img(it):
    im = load_img(it["src"])
    w, h = it["w"], it["h"]
    if it["fit"] == "cover":  # 枠に合わせて切り抜く
        px, py = [float(v) / 100 for v in re.findall(r"[\d.]+", it["pos"])]
        s = max(w / im.width, h / im.height)
        cw, ch = w / s, h / s
        x0, y0 = (im.width - cw) * px, (im.height - ch) * py
        im = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch)))
    elif it["fit"] == "contain":  # 縦横比を保って枠の下中央に置く
        s = min(w / im.width, h / im.height)
        nw, nh = im.width * s, im.height * s
        it = {**it, "x": it["x"] + (w - nw) / 2, "y": it["y"] + h - nh, "w": nw, "h": nh}
    if it.get("oval") or it.get("radius"):  # 丸・角丸は透過で切り抜く
        k = im.width / it["w"]
        mask = Image.new("L", im.size, 0)
        d = ImageDraw.Draw(mask)
        if it.get("oval"):
            d.ellipse((0, 0, im.width - 1, im.height - 1), fill=255)
        else:
            d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=it["radius"] * k, fill=255)
        alpha = Image.composite(im.split()[3], mask, mask)
        im.putalpha(alpha)
    im.putalpha(im.split()[3].point(lambda v: 0 if v < 10 else v))  # ほぼ透明なゴミを消す
    buf = io.BytesIO(); im.save(buf, "PNG"); buf.seek(0)
    sh.add_picture(buf, E(it["x"]), E(it["y"]), E(it["w"]), E(it["h"]))


def add_text(it):
    pad = it["size"] * 0.3
    tb = sh.add_textbox(E(it["x"] - pad), E(it["y"] - (it["lh"] - it["size"]) / 2), E(it["w"] + pad * 2), E(it["h"] + it["lh"] - it["size"]))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.TOP
    family = "Cormorant Garamond" if "Serif" in it["family"] else "Zen Maru Gothic"
    for i, line in enumerate(it["text"].split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}.get(it["align"], PP_ALIGN.LEFT)
        p.line_spacing = Pt(it["lh"] * 0.75)
        run = p.add_run(); run.text = line
        f = run.font
        f.size = Pt(it["size"] * 0.75); f.bold = it["weight"] >= 600; f.italic = it["italic"]
        f.name = family; f.color.rgb = color(it["color"])
        rpr = run._r.get_or_add_rPr()
        rpr.set("spc", str(round(it["ls"] * 0.75 * 100)))
        for tag in ("a:ea", "a:latin"):
            el = rpr.find(qn(tag))
            if el is None:
                el = rpr.makeelement(qn(tag), {}); rpr.append(el)
            el.set("typeface", family)


items = layout["items"]
# 外枠リング（outline）は本体より先に、z-index の大きいもの（上下の帯）は最後に描く
items.sort(key=lambda i: (i["z"], i["order"] - (0.5 if i.get("under") else 0)))
for it in items:
    if it["kind"] == "box":
        add_box(it)
    elif it["kind"] == "img":
        add_img(it)
    elif it["kind"] == "leaf":
        sh.add_picture(it["file"], E(it["x"]), E(it["y"]), E(it["w"]), E(it["h"]))
    elif it["kind"] == "text":
        add_text(it)

out = src.replace(".layout.json", ".pptx")
prs.save(out)
print("出力:", out, len(slide.shapes), "部品")
