# fhl-eyecatch

[藤沢北部まちづくりラボ](https://fujisawa-hokubu-lab.jp) の記事アイキャッチ画像を生成・保管するリポジトリです。

## 構成

| パス | 内容 |
|---|---|
| `make_eyecatch.py` | 画像生成スクリプト（白ベースのテンプレート） |
| `assets/logo.png` | サイトのロゴ |
| `configs/<スラッグ>.json` | 記事ごとの文言（タイトル、バッジ、カードなど） |
| `images/<スラッグ>.jpg` | 生成した画像（1200×630、JPEG） |

## 使い方

```
python3 make_eyecatch.py configs/<スラッグ>.json images/<スラッグ>.jpg
```

必要なもの：Python 3、Pillow、Noto Sans CJK（日本語フォント）。

## 運用の流れ

1. 記事に合わせて `configs/<スラッグ>.json` を作る
2. 画像を生成して `images/` に保存し、コミット・プッシュする
3. 公開URL（`https://raw.githubusercontent.com/jajaumajam/fhl-eyecatch/main/images/<スラッグ>.jpg`）からWordPressのメディアに取り込む
4. 記事のアイキャッチに設定し、代替テキストに config の `alt` を入れる

## デザインのルール

- 白背景。ロゴの弧をモチーフにした装飾を左上と右下に置く
- タイトルなどの主要情報は中央の幅520pxに集める（Instagramのプロフィール一覧は縦長に切り抜かれるため）
- 左右のカードは任意。横長表示でだけ見える補足情報に使う
- 締切などの期限のある情報は、中央ではなくカードにだけ入れる
- 数字は記事本文と同じものだけを使う

このリポジトリは公開されています。パスワードなどの秘密情報は置かないでください。
