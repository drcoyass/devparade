#!/usr/bin/env python3
"""
PosiDev Monitor - ネガティブなデブ発言を自動検知して自動返信

Mode 1 (AUTO): X APIクレジットがあれば自動で返信投稿
Mode 2 (MANUAL): クレジットなしならワンクリック返信リンク付きIssueを生成
"""

import os
import sys
import random
import time
import urllib.parse
from datetime import datetime, timezone, timedelta

try:
    import tweepy
except ImportError:
    print("tweepy not installed")
    sys.exit(1)

BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")
LAST_ID_FILE = "last_monitor_id.txt"

# 検索クエリ
SEARCH_QUERIES = [
    '"デブ" (辛い OR 悲しい OR 嫌 OR 傷つ OR つらい OR 泣) -is:retweet lang:ja',
    '"太った" (最悪 OR やばい OR ショック OR 泣 OR 嫌) -is:retweet lang:ja',
    '"痩せなきゃ" -is:retweet lang:ja',
    '"痩せろ" (言われ) -is:retweet lang:ja',
    '"デブ" "言われた" -is:retweet lang:ja',
]

MEMBERS = [
    {"name": "ハンサム判治", "role": "Vo.", "weight": "100kg"},
    {"name": "COYASS", "role": "MC", "weight": "93kg"},
    {"name": "ugazin", "role": "Gt.", "weight": "135kg"},
    {"name": "ぺー", "role": "Ba.", "weight": "120kg"},
    {"name": "TAH", "role": "Dr.", "weight": "120kg"},
]

RESPONSES = {
    "デブ": [
        "デブ？ ありがとう！総体重570kg超バンドDEV PARADEから言わせてもらうと、それは最高の褒め言葉🍖 #ポジデブ",
        "「デブ」= Delightful Excellent Beautiful。知らなかった？🍖 by DEV PARADE #ポジデブ",
        "デブは才能。俺たち5人で570kg、全員メジャーデビュー済み。才能に体重は関係ない🍖 #ポジデブ",
        "デブをネガティブに捉えないで。俺たちバンド名にデブ入れて誇ってるから🍖 @dev_parade #ポジデブ",
        "デブって呼ばれた？ おめでとう、DEV PARADEの入団資格満たしてるぞ（条件:90kg以上）🍖 #ポジデブ",
    ],
    "太った": [
        "太った？ それは「成長した」って言うんだよ。細胞レベルで進化してる。おめでとう🎉🍖 #ポジデブ",
        "体重が増えた = 存在感が増した。DEV PARADEが保証する🍖 @dev_parade #ポジデブ",
        "太った分だけ地球がお前を離したくないってこと。モテてるぜ、地球に🌍🍖 #ポジデブ",
        "体重増えた？ それは「影響力」のメーター。デカい奴はデカいことができる🍖 #ポジデブ",
    ],
    "痩せ": [
        "痩せる必要？ ないね。俺たち570kgで武道館目指してる。痩せたら夢が軽くなる💪🍖 #ポジデブ",
        "「痩せたい」→「もっと愛されたい」に変換。大丈夫、そのままで最高🍖 @dev_parade #ポジデブ",
        "痩せなくていい。むしろDEV PARADE入らない？条件は90kg以上🍖 #ポジデブ",
        "ダイエットの語源は「生き方」。今の生き方、最高じゃん。変えなくていい🍖 #ポジデブ",
    ],
    "generic": [
        "大丈夫、お前は最高だ。570kg超のバンドが言ってるんだから間違いない🍖 @dev_parade #ポジデブ",
        "デブは個性。個性は武器。武器は磨け🍖 by DEV PARADE #ポジデブ",
        "この世に無駄な脂肪なんてない。全部お前という作品の一部だ🍖 @dev_parade #ポジデブ",
        "どんな悩みも、焼肉食ったら解決する。解決しなくても美味い。それでいい🍖 #ポジデブ",
    ],
}


def select_response(tweet_text):
    text_lower = tweet_text
    for kw in ["デブ", "でぶ"]:
        if kw in text_lower:
            return random.choice(RESPONSES["デブ"])
    for kw in ["太った", "ふとった", "太り"]:
        if kw in text_lower:
            return random.choice(RESPONSES["太った"])
    for kw in ["痩せ", "やせ"]:
        if kw in text_lower:
            return random.choice(RESPONSES["痩せ"])
    return random.choice(RESPONSES["generic"])


def get_write_client():
    """投稿用クライアント（OAuth 1.0a）"""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        return None
    return tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET,
        wait_on_rate_limit=True,
    )


def get_read_client():
    """検索用クライアント（Bearer Token）"""
    if not BEARER_TOKEN:
        return None
    return tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)


def get_last_id():
    try:
        with open(LAST_ID_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_id(tweet_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(str(tweet_id))


def main():
    print("=" * 50)
    print("🍖 PosiDev Monitor")
    print("=" * 50)

    read_client = get_read_client()
    write_client = get_write_client()
    auto_mode = write_client is not None

    print(f"Mode: {'AUTO (自動返信)' if auto_mode else 'MANUAL (Issue生成)'}")

    if not read_client:
        print("⚠️ Bearer Token not set. Cannot search tweets.")
        generate_sample_issue()
        return

    last_id = get_last_id()
    found_tweets = []
    seen_ids = set()
    newest_id = last_id
    auto_replies = []

    for query in SEARCH_QUERIES:
        try:
            kwargs = {
                "query": query,
                "max_results": 10,
                "tweet_fields": ["created_at", "author_id", "text"],
                "user_fields": ["username"],
                "expansions": ["author_id"],
            }
            if last_id:
                kwargs["since_id"] = last_id

            result = read_client.search_recent_tweets(**kwargs)
            if not result.data:
                continue

            users = {}
            if result.includes and "users" in result.includes:
                for user in result.includes["users"]:
                    users[user.id] = user.username

            for tweet in result.data:
                if tweet.id in seen_ids:
                    continue
                seen_ids.add(tweet.id)

                username = users.get(tweet.author_id, "unknown")

                # 自分自身のツイートはスキップ
                if username == "dev_parade":
                    continue

                response = select_response(tweet.text)
                member = random.choice(MEMBERS)
                reply_text = f"@{username} {response}"

                tweet_data = {
                    "id": str(tweet.id),
                    "username": username,
                    "text": tweet.text,
                    "response": response,
                    "reply_text": reply_text,
                    "member": member,
                    "status": "pending",
                }

                # 自動投稿モード
                if auto_mode and len(auto_replies) < 10:
                    try:
                        write_client.create_tweet(
                            text=reply_text,
                            in_reply_to_tweet_id=tweet.id,
                        )
                        tweet_data["status"] = "sent"
                        print(f"✅ Auto-replied to @{username}")
                        auto_replies.append(tweet_data)
                        time.sleep(5)
                    except Exception as e:
                        print(f"❌ Auto-reply failed: {e}")
                        tweet_data["status"] = f"failed: {e}"

                found_tweets.append(tweet_data)

                # 最新IDを追跡
                if newest_id is None or tweet.id > int(newest_id or 0):
                    newest_id = str(tweet.id)

                if len(found_tweets) >= 15:
                    break

        except Exception as e:
            print(f"Search error: {e}")
            continue

        if len(found_tweets) >= 15:
            break

    if newest_id and newest_id != last_id:
        save_last_id(newest_id)

    print(f"\nFound: {len(found_tweets)} tweets")
    if auto_mode:
        print(f"Auto-replied: {len(auto_replies)} tweets")

    generate_issue(found_tweets, auto_mode)


def generate_issue(tweets, auto_mode):
    now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")
    mode_str = "AUTO（自動返信済み）" if auto_mode else "MANUAL（ワンクリック返信）"

    lines = [
        "## 🍖 デブポジ返信レポート",
        "",
        f"**検知日時:** {now}",
        f"**モード:** {mode_str}",
        f"**検知数:** {len(tweets)}件",
        "",
        "---",
        "",
    ]

    if not tweets:
        lines.append("*ネガティブなデブ発言は見つかりませんでした。平和！🍖*")
    else:
        for i, t in enumerate(tweets, 1):
            intent_url = f"https://twitter.com/intent/tweet?in_reply_to={t['id']}&text={urllib.parse.quote(t['reply_text'])}"
            tweet_url = f"https://twitter.com/{t['username']}/status/{t['id']}"

            status_emoji = "✅" if t["status"] == "sent" else "👉"
            status_text = "自動返信済み" if t["status"] == "sent" else "未返信"

            lines.append(f"### #{i} {status_emoji} {status_text}")
            lines.append(f"**元ツイート** by @{t['username']}:")
            lines.append(f"> {t['text'][:200]}")
            lines.append(f"")
            lines.append(f"**デブポジ返信** ({t['member']['name']} {t['member']['role']}):")
            lines.append(f"```")
            lines.append(f"{t['reply_text']}")
            lines.append(f"```")

            if t["status"] != "sent":
                lines.append(f"")
                lines.append(f"**[👉 ワンクリック返信]({intent_url})** | [元ツイート]({tweet_url})")

            lines.append(f"")
            lines.append(f"---")
            lines.append(f"")

    lines.append("*Powered by DEV PARADE ポジデブBot 🍖*")

    with open("monitor_issue.md", "w") as f:
        f.write("\n".join(lines))

    print("✅ Issue markdown generated!")


def generate_sample_issue():
    now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")
    sample = f"""## 🍖 デブポジ返信候補

**検知日時:** {now}
**ステータス:** ⚠️ Bearer Token未設定

X Developer PortalでAPIクレジット（最低$5）を購入すると、完全自動で返信投稿まで行います。

---

*Powered by DEV PARADE ポジデブBot 🍖*
"""
    with open("monitor_issue.md", "w") as f:
        f.write(sample)


if __name__ == "__main__":
    main()
