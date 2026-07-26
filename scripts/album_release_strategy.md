# 🎸 デブパレード 8/19 アルバムリリース 全自動化戦略書

**1st Full Album「全ての武器をお箸に」**
**リリース日: 2026年8月19日（水）**

---

## 📊 現在地 (2026/07/26)

| 日付 | イベント | 状態 |
|------|---------|------|
| 7/12 | 下北沢CLUB Que ライブ | ✅ 完了 |
| **7/27** | **シングル配信2日前カウントダウン** | **🔴 今日実行** |
| **7/29** | **「夏の終わりに」配信リリース** | **🔴 3日後** |
| 8/5 | アルバム全貌公開 | 準備中 |
| 8/12 | アルバム1週間前カウントダウン開始 | 準備中 |
| 8/19 | 1stアルバムリリース | 最終目標 |

---

## 🤖 自動化システム全体マップ

```
GitHub Actions
├── debu-posi-marketing.yml  → 1日4回 ポジデブ格言ツイート（継続中）
├── countdown-tweet.yml      → 毎日12:00/20:30 カウントダウン（新規追加✅）
├── debu-posi-monitor.yml    → メンション監視・自動返信
└── follower-growth.yml      → フォロワー拡大エンジン

手動実行スクリプト
├── scripts/generate_royal_campaign.py   → AI生成 王道復活キャンペーン文
├── scripts/generate_recovery_campaign.py → AI生成 リカバリーキャンペーン
├── scripts/grassroots_promoter.py       → ラジオ/プレイリスト草の根促進
└── video-automation/generate_natsunoowarini.sh → リリック動画生成（新規✅）
```

---

## 📅 7/27〜8/19 週別アクションプラン（完全版）

### 🔴 今週 (7/27〜8/2): シングルリリース週

#### 7/27（月）今日やること
- [ ] **X投稿**: `scripts/single_release_posts.md` の7/27テンプレートを手動投稿
- [ ] **Instagram投稿**: 同上 Instagram版を投稿（ハッシュタグ強め）
- [ ] **countdown-tweet.yml を GitHub にプッシュ** → 自動実行スタート

```bash
# Git push コマンド
git add .github/workflows/countdown-tweet.yml scripts/countdown_tweets.py scripts/single_release_posts.md
git commit -m "feat: 7/29シングルリリース対応 カウントダウンBot更新"
git push
```

#### 7/28（火）
- [ ] X/Instagram: 「明日解禁！」前日煽り投稿（single_release_posts.md 参照）
- [ ] TikTok/Reels: 予告ティザー動画（15〜30秒）投稿

#### 7/29（水）【シングルリリース日】🎵
- [ ] **07:00** X/Instagram: リリース告知メイン投稿
- [ ] **09:00** TikTok: リリック動画投稿（`generate_natsunoowarini.sh` で生成）
- [ ] **12:00** X: 感想募集エンゲージメント投稿
- [ ] **15:00** Instagram Stories: 配信リンクストーリーズ
- [ ] **18:00** YouTube: Shorts投稿
- [ ] **20:00** X: NARUTO層向けラストプッシュ
- [ ] 翌日以降: アルバムへの橋渡し投稿

```bash
# リリック動画生成コマンド (7/28までに実行)
cd video-automation
bash generate_natsunoowarini.sh
```

#### 7/30〜8/1
- [ ] 毎日: シングル「夏の終わりに」の感想引用RT・エンゲージメント
- [ ] アルバム予告投稿（8/19リリース告知を徐々に強化）

---

### 🔴 8/2週 (8/3〜8/9): アルバム全貌公開フェーズ

#### 8/5（水）アルバム全貌公開
投稿内容：
```
📀 1st Full Album「全ての武器をお箸に」全貌公開！

【全曲トラックリスト】
01. 100CAN DIVE
02. 自転車
03. パルフェ
（続きはリンクで）

8/19リリース。予約受付中！
https://devparade.jp/
#デブパレード #全ての武器をお箸に
```

手動実行:
```bash
# 王道復活キャンペーンコンテンツを生成
cd /Users/coyass/Desktop/CODE系AI/kaihatsu/dev-parade-site
python scripts/generate_royal_campaign.py
# → viral_outputs/royal_campaign.md に出力される
```

#### 8/7〜8/9
- [ ] メンバー個人SNSから「アルバムについての想い」投稿
- [ ] 草の根プロモーター実行（ラジオ・プレイリスト提案）

```bash
python scripts/grassroots_promoter.py --mode radio
python scripts/grassroots_promoter.py --mode playlist
```

---

### 🔴 8/10週 (8/10〜8/16): 1週間前カウントダウン

#### 8/12（水）カウントダウン開始
- countdown-tweet.yml が自動的にアルバムカウントダウンに切り替わる（single_days < 0になるため）
- 手動で追加投稿:

```
🎸 1st Album リリースまであと7日！

「全ての武器をお箸に」

すべての争いを終わりにして、
お箸を持って、みんなで美味しくご飯を食べよう。

それがDevparadeの答え。
15年かけて出した、たった一つの答え。

予約はこちら👇
https://devparade.jp/
#デブパレード #全ての武器をお箸に
```

#### 8/13〜8/18: 毎日1投稿
- カウントダウン自動投稿（countdown-tweet.yml）
- メンバー個人SNSリレー投稿

---

### 🔴 8/19（水）リリース日 完全ガイド

#### 全時間帯タイムライン

| 時間 | プラットフォーム | 内容 |
|------|--------------|------|
| 00:00 | X | 0時ジャスト解禁ツイート |
| 07:00 | X/Instagram | リリース告知メイン |
| 09:00 | TikTok | アルバムティーザー動画 |
| 12:00 | X | 感想募集・エンゲージメント |
| 15:00 | Instagram Stories | 各曲紹介ストーリーズ |
| 18:00 | YouTube | アルバムトレーラー/リリック動画 |
| 20:00 | X | 「聴いてくれてありがとう」感謝投稿 |
| 21:00 | 全SNS | ライブ告知（次の活動予告） |

#### 当日の投稿テンプレート（00:00）
```
🎸 今日、俺たちの全部を世界に解き放つ。

「全ての武器をお箸に」

2026年8月19日、0時解禁。

すべての争いを終わりにして、
みんなで美味しくご飯を食べよう。

それがDevparadeのすべて。
15年間待ってくれた人へ。ありがとう。🍖

https://link-map.jp/links/t7J6lCsV

#デブパレード #全ての武器をお箸に #DEVPARADE
```

---

## 🔧 自動化システム 実行コマンドまとめ

```bash
# 現状確認 (今何フェーズか)
python scripts/countdown_tweets.py

# Xへの自動投稿テスト (DRY_RUN)
DRY_RUN=true python scripts/debu-posi-tweet-generator.py

# 王道キャンペーンコンテンツ生成
python scripts/generate_royal_campaign.py

# リリック動画生成 (事前に音源が必要)
cd video-automation && bash generate_natsunoowarini.sh

# GitHub Actions 手動トリガー
gh workflow run countdown-tweet.yml
gh workflow run debu-posi-marketing.yml

# フォロワー成長エンジン
python scripts/follower-growth.py
```

---

## ❗ 残課題・要確認事項

### 1. X API 403エラーについて
`marketing_log.md` に 403 Forbidden が記録されています。
**原因**: Free tier のX APIは書き込み権限が制限されている場合がある
**対応**: twikit（ブラウザ自動化）を使用 → GitHub Secrets に `X_USERNAME`, `X_EMAIL`, `X_PASSWORD` を設定が必要

```
必要なGitHub Secrets:
- X_USERNAME   (Xのユーザー名 @なし)
- X_EMAIL      (登録メールアドレス)
- X_PASSWORD   (パスワード)
- OPENAI_API_KEY (AI生成機能)
```

### 2. アルバムのトラックリスト確認
lyrics_database.json に収録曲が入っているが、リリース用の公式トラックリストと合致しているか確認が必要:
- Track 01: 100CAN DIVE
- Track 02: 自転車
- Track 03: パルフェ
- Track 05: 何年経っても万年FAT お前らにゃ一生わかんねえや
- Track 06: 夏の終わりに（先行シングル）
- Track 07: ハッピー乱デブー

### 3. support.html の Stripe決済状況
投げ銭・物販機能は設定済みか確認。アルバムリリースと同時に物販告知も強化する。
