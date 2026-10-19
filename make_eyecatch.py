"""藤沢北部まちづくりラボ アイキャッチ生成（白ベース版）

使い方:
    python3 make_eyecatch.py configs/<slug>.json images/<slug>.jpg

設計:
- 1200x630（OGP比）。白背景に、ロゴの弧をモチーフにした装飾を四隅に置く。
- タイトルなど主要情報は中央の幅520pxに集める。Instagramのプロフィール一覧
  （縦長3:4に中央を切り抜き）でも読めるようにするため。
- 左右のカード（cards）は任意。横長表示（サイト・Facebook・フィード）でだけ見える補足。
- 文字は濃い色で視認性を確保。

config（JSON）:
    category  : カテゴリ名（例 "地域情報"）
    title     : タイトル（1〜2行の配列。1行8字程度まで）
    badge     : 青いバッジの文言（任意）
    sub       : 補足（任意、配列）
    cards     : [[見出し, 数字, 単位], ...] 最大2枚（任意）
    alt       : 画像の代替テキスト（任意。省略時はタイトル・バッジ・補足から作る）
    post_id   : WordPressの記事ID
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "assets", "logo.png")
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"

S = 2  # 2倍で描いて縮小
W, H = 1200, 630
C = {
    "green": "#3AAA35", "dark": "#2E8A2A", "blue": "#0083B2", "orange": "#FF8A00",
    "text": "#1F2A1F", "sub": "#3C463C", "card": "#F1F8EF", "white": "#FFFFFF",
}

def f(weight, size):
    return ImageFont.truetype(FONT.format(weight), int(size * S), index=0)  # 0 = 日本語字形

def text_center(d, cx, y, s, font, fill):
    w = d.textlength(s, font=font)
    d.text((cx * S - w / 2, y * S), s, font=font, fill=fill)

def pill(d, cx, y, s, font, fill, color, pad_x=22, h=48):
    w = d.textlength(s, font=font) / S + pad_x * 2
    d.rounded_rectangle([(cx - w / 2) * S, y * S, (cx + w / 2) * S, (y + h) * S],
                        radius=h * S // 2, fill=fill)
    bb = d.textbbox((0, 0), s, font=font)
    d.text((cx * S - (bb[2] - bb[0]) / 2 - bb[0], y * S + (h * S - (bb[3] - bb[1])) / 2 - bb[1]),
           s, font=font, fill=color)

def arc(d, cx, cy, r, width, color, start, end):
    d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], start, end,
          fill=color, width=int(width * S))

def dot(d, x, y, r, color):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=color)

def dot_on_arc(d, cx, cy, r, width, deg, dr, color):
    """弧の線の中心（半径 r - width/2）上に点を置く。PILの弧は外周rから内側にwidth分描かれる"""
    import math
    rc = r - width / 2
    dot(d, cx + rc * math.cos(math.radians(deg)), cy + rc * math.sin(math.radians(deg)), dr, color)

def decorate(d):
    # 左上：ロゴの弧（緑の太い弧＋青の細い弧）
    arc(d, -40, -40, 220, 28, C["green"], 0, 90)
    arc(d, -40, -40, 170, 11, C["blue"], 0, 90)
    dot_on_arc(d, -40, -40, 220, 28, 45, 8, C["orange"])
    # 右下
    arc(d, 1240, 670, 230, 28, C["green"], 180, 270)
    arc(d, 1240, 670, 178, 11, C["blue"], 180, 270)
    dot_on_arc(d, 1240, 670, 230, 28, 225, 8, C["orange"])
    # 下端のライン
    d.rectangle([0, (H - 8) * S, W * S, H * S], fill=C["green"])

def side_card(d, cx, cy, label, value, unit):
    w, h = 240, 190
    d.rounded_rectangle([(cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S],
                        radius=22 * S, fill=C["card"], outline=C["green"], width=3 * S)
    text_center(d, cx, cy - 66, label, f("Bold", 22), C["sub"])
    size = 68
    while True:  # カード幅に収まるまで数字を小さくする
        fv, fu = f("Black", size), f("Bold", 28)
        vw, uw = d.textlength(value, font=fv), d.textlength(unit, font=fu)
        if (vw + uw) / S <= w - 36 or size <= 40:
            break
        size -= 4
    x0 = cx * S - (vw + uw) / 2
    d.text((x0, (cy - 38 + (68 - size) * 0.7) * S), value, font=fv, fill=C["dark"])
    d.text((x0 + vw, (cy + 6) * S), unit, font=fu, fill=C["dark"])

def brand(img, d, cx, cy):
    name, fn = "藤沢北部まちづくりラボ", f("Bold", 24)
    r, gap = 26, 10
    nw = d.textlength(name, font=fn) / S
    x0 = cx - (2 * r + gap + nw) / 2
    logo = Image.open(LOGO).convert("RGBA").resize((int(2 * r * S), int(2 * r * S)), Image.LANCZOS)
    img.paste(logo, (int(x0 * S), int((cy - r) * S)), logo)
    bb = d.textbbox((0, 0), name, font=fn)
    d.text(((x0 + 2 * r + gap) * S, cy * S - (bb[3] + bb[1]) / 2), name, font=fn, fill=C["dark"])

def alt_text(cfg):
    if cfg.get("alt"):
        return cfg["alt"]
    t = ""
    for line in cfg["title"]:  # 行末が助詞などなら詰め、それ以外は空白でつなぐ
        t += line if (not t or t[-1] in "のとで・、がにはを「も") else " " + line
    rest = [x for x in ([cfg.get("badge")] + cfg.get("sub", [])) if x]
    if rest:
        t += ("" if t[-1] in "？！。" else "。") + "、".join(rest)
    return t + "（藤沢北部まちづくりラボ）"

def main(cfg, out):
    img = Image.new("RGB", (W * S, H * S), C["white"])
    d = ImageDraw.Draw(img)
    decorate(d)

    cx = 600
    lines = cfg["title"]
    ts = cfg.get("title_size", 62)
    while ts > 44 and max(d.textlength(l, font=f("Black", ts)) for l in lines) / S > 520:
        ts -= 2  # 中央の幅520pxに収まるまで小さくする
    has_sub = bool(cfg.get("badge")) or bool(cfg.get("sub"))
    # 縦方向の中央寄せ
    block = 44 + 30 + len(lines) * (ts + 16) + (26 + 56 if cfg.get("badge") else 0) \
        + (20 + 40 * len(cfg.get("sub", [])) if cfg.get("sub") else 0)
    y = max(48, (560 - block) / 2)
    pill(d, cx, y, cfg["category"], f("Bold", 22), C["dark"], C["white"], h=44)
    y += 44 + 30
    for line in lines:
        text_center(d, cx, y, line, f("Black", ts), C["text"])
        y += ts + 16
    if cfg.get("badge"):
        y += 26
        pill(d, cx, y, cfg["badge"], f("Black", 28), C["blue"], C["white"], h=56)
        y += 56
    if cfg.get("sub"):
        y += 20
        for line in cfg["sub"]:
            text_center(d, cx, y, line, f("Bold", 27), C["sub"])
            y += 40
    brand(img, d, cx, 570)

    for card, ccx in zip(cfg.get("cards", []), (178, 1022)):
        side_card(d, ccx, 315, *card)

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    img.resize((W, H), Image.LANCZOS).save(out, "JPEG", quality=90, optimize=True)

if __name__ == "__main__":
    main(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
