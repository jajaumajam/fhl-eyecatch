"""configs/ のすべての設定から images/ に画像を作り、一覧（contact_sheet.jpg）も作る。
使い方: python3 build_all.py
"""
import glob, json, os
from PIL import Image, ImageDraw, ImageFont
import make_eyecatch as me

HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    paths = sorted(glob.glob(os.path.join(HERE, "configs", "*.json")))
    thumbs = []
    for p in paths:
        slug = os.path.splitext(os.path.basename(p))[0]
        out = os.path.join(HERE, "images", slug + ".jpg")
        cfg = json.load(open(p, encoding="utf-8"))
        me.main(cfg, out)
        thumbs.append((slug, cfg.get("post_id"), out))
    # 確認用の一覧（4列）
    tw, th, cols = 300, 158, 4
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 34) + 10), "#DDDDDD")
    d = ImageDraw.Draw(sheet)
    fn = ImageFont.truetype(me.FONT.format("Regular"), 14, index=0)
    for i, (slug, pid, out) in enumerate(thumbs):
        x, y = 10 + (i % cols) * (tw + 10), 10 + (i // cols) * (th + 34)
        sheet.paste(Image.open(out).resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y + th + 4), f"{pid}  {slug}", font=fn, fill="#333")
    sheet.save(os.path.join(HERE, "contact_sheet.jpg"), quality=85)
    print(len(thumbs), "images")

if __name__ == "__main__":
    main()
