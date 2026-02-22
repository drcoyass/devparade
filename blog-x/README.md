# 🦷🎤 COYASS Auto-Posting System

**歯科医師 × ラッパー × 自動投稿** — note & X への自動コンテンツ投稿システム

## 🚀 クイックスタート

### 1. セットアップ
```bash
# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate

# 依存パッケージをインストール
pip install -r requirements.txt

# Playwright のブラウザをインストール
playwright install chromium

# 環境変数ファイルをコピーして設定
cp .env.example .env
# .env を編集して各APIキーを設定
```

### 2. データベース初期化
```bash
python src/main.py init-db
```

### 3. コンテンツ生成テスト
```bash
# Note記事を1本生成（投稿はしない）
python src/main.py generate --platform note --category dental_tips

# X投稿を1本生成
python src/main.py generate --platform x --category music_review
```

### 4. スケジューラ起動
```bash
# DRY RUNモード（投稿せずにログ出力のみ）
python src/main.py run

# 本番モード（settings.yaml で dry_run: false に変更）
python src/main.py run
```

### 5. ダッシュボード起動
```bash
python src/main.py dashboard
# → http://127.0.0.1:5000 でアクセス
```

## 📁 ディレクトリ構成

```
Blog&X/
├── config/
│   ├── settings.yaml          # 全体設定
│   ├── schedule.yaml          # 投稿スケジュール
│   └── content_templates/     # カテゴリ別プロンプト
├── src/
│   ├── main.py                # エントリーポイント
│   ├── scheduler.py           # スケジューラ
│   ├── content/
│   │   ├── generator.py       # AI記事生成
│   │   └── editor.py          # 品質チェック
│   ├── publishers/
│   │   ├── note_publisher.py  # Note投稿
│   │   └── x_publisher.py     # X投稿
│   ├── data/
│   │   ├── models.py          # DB定義
│   │   └── repository.py      # データアクセス
│   └── dashboard/
│       ├── app.py             # Flask ダッシュボード
│       └── templates/         # HTML テンプレート
├── data/                      # SQLite DB
├── requirements.txt
└── .env.example               # APIキー設定テンプレート
```

## 📅 投稿スケジュール

| 時刻 | Platform | カテゴリ |
|------|----------|---------|
| 06:00 | 📝 Note | メイン記事（曜日ローテーション） |
| 07:00 | 🐦 X | おはようツイート |
| 12:00 | 🐦 X | ランチ / 歯の豆知識 |
| 18:00 | 🐦 X | 音楽レビュー |
| 20:00 | 📝 Note | サブ記事（日記系） |
| 21:00 | 🐦 X | 夜の振り返り |

## ⚠️ 注意事項

- **DRY RUN**: 初回は必ず `dry_run: true` で動作確認してください
- **Note**: 公式APIがないためブラウザ自動化を使用しています
- **X API**: 無料枠は月500投稿まで（1日約16投稿）
