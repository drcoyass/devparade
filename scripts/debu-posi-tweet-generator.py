#!/usr/bin/env python3
"""
DebuPosi Tweet Generator

ツイート文を自動生成し、ワンクリック投稿リンク付きのIssueを作成。
X APIクレジット不要。GitHub Issueのリンクをクリックするだけで投稿可能。
"""

import os
import random
import urllib.parse
from datetime import datetime, timezone, timedelta

CAMPAIGN = os.environ.get("CAMPAIGN", "scheduled")
BOT_URL = "https://dev-parade.github.io/debu-bot.html"
SITE_URL = "https://dev-parade.github.io/"

# ===== ツイートテンプレート =====
TWEETS = {
    "launch": [
        f"""🍖【世界初】デブポジBot、爆誕。

SNS上の全ての「デブ」をポジティブに変換するBot、作りました。

総体重570kg超のバンド DEV PARADEが、全てのネガティブなデブ発言を全力で肯定します。

試してみて👇
{BOT_URL}

#デブポジBot #DEVPARADE #デブパレード""",

        f"""「デブ」って言われて傷ついた全ての人へ。

俺たちDEV PARADE、メンバー全員90kg以上。
バンド名にデブ入れてる。
しかもメジャーデビューした。

デブは才能。脂肪は努力の結晶。

そんな俺たちが作った「デブポジBot」🍖

{BOT_URL}
#デブポジBot #DEVPARADE""",
    ],

    "scheduled": [
        f"""Q. デブのメリットは？

A.
・冬あったかい
・存在感がある
・海で浮きやすい
・抱きしめた時の安心感
・食レポの説得力が段違い
・地球に愛されてる（重力的な意味で）

反論は受け付けません。🍖

{BOT_URL}
#デブポジBot #DEVPARADE""",

        f"""【定期】DEV PARADEのメンバー体重

🎤 ハンサム判治 100kg
🎙️ COYASS 93kg
🎸 ugazin 135kg
🎸 ぺー 120kg
🥁 TAH 120kg

合計: 570kg超
全員痛風ホルダー。
全員メジャーデビュー経験あり。

体重と才能は比例する。🍖
#DEVPARADE #デブパレード""",

        f"""「太った」→「成長した」
「デブ」→「存在感がある」
「メタボ」→「ロックな体型」
「ビール腹」→「人生楽しんでる証拠」
「痩せろ」→「そのままでいい」

全部ポジティブに変換するBot作った🍖
{BOT_URL}

#デブポジBot #DEVPARADE""",

        f"""今日のデブポジ名言:

「この世に無駄な脂肪はない。
全部、お前という作品の一部だ。」

— DEV PARADE（総体重570kg超）🍖

{BOT_URL}
#デブポジBot #デブポジ""",

        f"""体重と幸福度は比例する。
（DEV PARADE調べ）

source: 俺たち570kg超で幸せ🍖

#デブポジBot #DEVPARADE
{BOT_URL}""",

        f"""NARUTOのエンディングテーマ歌ってた
メンバー全員90kg以上のバンドが
15年ぶりに復活して
「デブをポジティブにするBot」を作った

という情報が流れてきたら
それは全部事実です🍖

{SITE_URL}
#DEVPARADE #デブパレード #バッチコイ""",

        f"""ダイエットの語源は「生き方」（ギリシャ語 diaita）

つまり「ダイエットしなきゃ」は
「生き方を変えなきゃ」という意味。

でも今の生き方、最高じゃん？
変えなくていいよ。🍖

#デブポジBot #DEVPARADE
{BOT_URL}""",

        f"""あなたの「デブ」エピソード、
デブポジBotが全力ポジティブに変換します。

入力: ネガティブな体型の悩み
出力: DEV PARADEメンバーからの全力肯定

やってみて👇🍖
{BOT_URL}

#デブポジBot""",

        f"""太ってる人にしかわからないこと

・椅子の肘掛けは敵
・ジェットコースターのバーが下がらない
・飛行機のベルト延長を頼む勇気

全部わかる。全部経験した。
でも全部ネタになる。
それがDEV PARADEのスピリット🍖

#デブポジBot #DEVPARADE""",

        f"""【急募】体重90kg以上の仲間

資格:
・体重90kg以上
・音楽が好き
・デブに誇りを持てる

待遇:
・DEV PARADEが全力で肯定
・デブポジBotが24時間あなたの味方

{BOT_URL}
#デブポジBot #DEVPARADE""",

        f"""太ったことを後悔してるあなたへ。

後悔する必要ゼロ。

俺たちは太ったことを武器にして
バンド組んで
メジャーデビューして
NARUTOのエンディング歌って
15年ぶりに復活した。

全部、太ってたから。🍖

#デブポジBot #DEVPARADE #バッチコイ
{SITE_URL}""",

        f"""デブポジBot 変換例:

😢「また太った...」
🍖「太った？ それは成長した！細胞レベルで進化してる。おめでとう！」

😢「デブって言われた」
🍖「DEV PARADEの入団資格を満たしてます（条件:90kg以上）」

あなたも変換してみて👇
{BOT_URL}
#デブポジBot""",
    ],

    "collab": [
        f"""【コラボ募集】

デブポジBotと一緒にデブをポジティブにしたい
企業・ブランド・インフルエンサーを募集中！

・フードブランド🍔
・アパレル（大きいサイズ）👕
・お笑い芸人（デブ芸人さん大歓迎）🎤

DM or リプライで！🍖
#デブポジBot #コラボ募集""",
    ],
}


def main():
    tweets = TWEETS.get(CAMPAIGN, TWEETS["scheduled"])
    tweet_text = random.choice(tweets)

    # X intent URL（ワンクリック投稿リンク）
    intent_url = "https://twitter.com/intent/tweet?text=" + urllib.parse.quote(tweet_text)

    # Issue用Markdown生成
    now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")

    issue_md = f"""## 🍖 デブポジツイート（自動生成）

**生成日時:** {now}
**キャンペーン:** {CAMPAIGN}

---

### ツイート内容（{len(tweet_text)}文字）

```
{tweet_text}
```

---

### 👇 ワンクリックで投稿 👇

| プラットフォーム | リンク |
|---|---|
| **𝕏 (Twitter)** | **[ここをクリックして投稿する]({intent_url})** |
| **LINE** | [LINEで共有](https://social-plugins.line.me/lineit/share?url={urllib.parse.quote(BOT_URL)}&text={urllib.parse.quote(tweet_text)}) |
| **Facebook** | [Facebookで共有](https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(BOT_URL)}&quote={urllib.parse.quote(tweet_text)}) |

---

### 📋 手動投稿する場合

1. 上のツイート内容をコピー
2. [X (Twitter)](https://twitter.com/compose/tweet) を開く
3. ペーストして投稿

---

投稿したらこのIssueをCloseしてください ✅
"""

    with open("tweet_issue.md", "w") as f:
        f.write(issue_md)

    print(f"Campaign: {CAMPAIGN}")
    print(f"Tweet ({len(tweet_text)} chars):")
    print(tweet_text)
    print(f"\nIntent URL: {intent_url}")
    print("✅ Issue markdown generated!")


if __name__ == "__main__":
    main()
