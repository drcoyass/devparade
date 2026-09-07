#!/usr/bin/env python3
"""
Devparade X Follower Growth & Member Retweet Engine
===================================================
フォロワー増加マーケティング ＆ メンバーツイート自動リツイート完全自動化

戦略:
1. メンバー（判治, COYASS, ugazin, ぺー, TAH）の新着ツイート自動リツイート
2. 親和性の高いターゲット層（ボディポジティブ、大盛り、デブあるある、NARUTO等）への安全ないいね巡回
3. デブパレード言及・メンションへの感謝いいね
4. フォロワー推移トラッキング ＆ 成長レポート生成
"""

import os
import sys
import json
import random
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
GROWTH_LOG = _BASE_DIR / "data" / "growth_log.json"
LIKED_FILE = _BASE_DIR / "data" / "liked_tweet_ids.json"

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

# 親和性の高い検索キーワード（デブパレードのファンになりやすい層）
TARGET_KEYWORDS = [
    "デブ", "太った", "体重増えた", "大盛り", "特盛",
    "飯テロ", "深夜のラーメン", "焼肉食べたい", "食べ放題",
    "ボディポジティブ", "ぽっちゃり", "大きいサイズ",
    "NARUTO バッチコイ", "NARUTO エンディング"
]

# 除外キーワード（スパム・アフィリエイト・不適切なアカウントを避ける）
EXCLUDE_KEYWORDS = [
    "副業", "稼ぐ", "在宅", "裏垢", "パパ活", "ママ活", "ギャンブル",
    "カジノ", "暗号資産", "仮想通貨", "fx", "プレゼント企画", "paypay"
]


def load_growth_log():
    try:
        with open(GROWTH_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"runs": [], "liked_tweets": [], "followers_history": []}


def save_growth_log(log):
    GROWTH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(GROWTH_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def load_liked_ids():
    try:
        with open(LIKED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_liked_ids(liked_set):
    LIKED_FILE.parent.mkdir(parents=True, exist_ok=True)
    # 最新2000件のみ保持
    recent_ids = list(liked_set)[-2000:]
    with open(LIKED_FILE, "w", encoding="utf-8") as f:
        json.dump(recent_ids, f, indent=2)


def is_safe_tweet(text):
    """スパム・不適切ツイートを排除する安全フィルター"""
    text_lower = text.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in text_lower:
            return False
    return True


def run_target_likes(max_likes=6):
    """
    ターゲット層の一般ユーザーツイートに安全に「いいね」して公式を認知してもらう
    （アカウント制限を避けるため1回5〜6件の極小安全運用）
    """
    try:
        from x_client import search_tweets, like_tweet
    except ImportError:
        try:
            from scripts.x_client import search_tweets, like_tweet
        except ImportError:
            print("❌ x_client が見つかりません")
            return 0

    liked_ids = load_liked_ids()
    new_liked = 0

    # ランダムにキーワードを2つ選択
    selected_keywords = random.sample(TARGET_KEYWORDS, min(3, len(TARGET_KEYWORDS)))
    print(f"\n🎯 ターゲットいいね巡回（キーワード: {', '.join(selected_keywords)}）...")

    for kw in selected_keywords:
        if new_liked >= max_likes:
            break

        print(f"  🔍 検索中: 「{kw}」")
        try:
            results = search_tweets(kw, count=5)
            for t in results:
                if new_liked >= max_likes:
                    break

                tid = t.get("id")
                text = t.get("text", "")
                username = t.get("username", "")

                if not tid or tid in liked_ids:
                    continue

                if not is_safe_tweet(text):
                    continue

                print(f"     ❤️ いいね対象: @{username} 「{text[:40].replace(chr(10), ' ')}...」")
                if DRY_RUN:
                    print(f"        [DRY RUN] いいねをスキップ")
                    liked_ids.add(tid)
                    new_liked += 1
                else:
                    success = like_tweet(tid)
                    if success:
                        liked_ids.add(tid)
                        new_liked += 1
                        time.sleep(random.uniform(2.0, 3.5))  # レート制限回避

        except Exception as e:
            print(f"  ⚠️ 検索・いいねエラー ({kw}): {e}")

    save_liked_ids(liked_ids)
    print(f"  ✅ いいね巡回完了: 今回 {new_liked} 件実行")
    return new_liked


def run_brand_mentions_like(max_likes=4):
    """「デブパレード」に言及してくれているツイートに感謝のいいね"""
    try:
        from x_client import search_tweets, like_tweet
    except ImportError:
        return 0

    liked_ids = load_liked_ids()
    brand_liked = 0
    queries = ["デブパレード", "Devparade", "#デブパレード"]

    print("\n📣 バンド言及ツイートへのいいね巡回...")
    for q in queries:
        if brand_liked >= max_likes:
            break
        try:
            results = search_tweets(q, count=4)
            for t in results:
                if brand_liked >= max_likes:
                    break
                tid = t.get("id")
                text = t.get("text", "")
                username = t.get("username", "")

                # 公式自身のツイートはスキップ
                if username.lower() == "dev_parade" or tid in liked_ids:
                    continue

                if not is_safe_tweet(text):
                    continue

                print(f"     🍖 バンド言及発見: @{username} 「{text[:40].replace(chr(10), ' ')}...」")
                if DRY_RUN:
                    liked_ids.add(tid)
                    brand_liked += 1
                else:
                    if like_tweet(tid):
                        liked_ids.add(tid)
                        brand_liked += 1
                        time.sleep(2.0)
        except Exception as e:
            print(f"  ⚠️ ブランド検索エラー ({q}): {e}")

    save_liked_ids(liked_ids)
    return brand_liked


def generate_growth_report(stats, target_likes, brand_likes, member_rts, log):
    """フォロワー増加レポート生成"""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)

    prev_followers = 0
    if log.get("followers_history"):
        prev_followers = log["followers_history"][-1].get("count", 0)

    followers = stats.get("followers", 0) if stats else 0
    diff = followers - prev_followers if prev_followers > 0 else 0
    diff_str = f"+{diff}" if diff >= 0 else str(diff)

    lines = [
        f"## 📈 Devparade X Growth & RT Report",
        "",
        f"**日時:** {now.strftime('%Y-%m-%d %H:%M JST')}",
        "",
        "---",
        "",
        "### 📊 アカウント統計",
        "",
        f"| 指標 | 数値 |",
        f"|------|------|",
        f"| フォロワー | **{followers}** ({diff_str}) |",
        f"| フォロー中 | {stats.get('following', 0)} |",
        f"| 累計ツイート | {stats.get('tweets', 0)} |",
        "",
        "### 🚀 今回のアクション実績",
        "",
        f"- 🎸 **メンバーツイート自動RT**: {member_rts} 件",
        f"- 🎯 **ターゲット層へのいいね**: {target_likes} 件",
        f"- 📣 **バンド言及への感謝いいね**: {brand_likes} 件",
        f"- ❤️ **合計エンゲージメント**: {target_likes + brand_likes} 件",
        "",
        "### 💡 フォロワー増加の好循環サイクル",
        "1. **メンバーRT**: 判治・COYASS・ugazin・ぺー・TAHのツイートを公式が拡散しTL活発化",
        "2. **ターゲットいいね**: 「大盛り」「デブ」「飯テロ」投稿者へ公式からリアクション ➔ プロフィール流入",
        "3. **888種デブ語録**: 1日4回の圧倒的クオリティ投稿でフォロー継続率を最大化",
        "",
        "---",
        "*Devparade Automated Growth Engine 🍖*",
    ]

    with open("growth_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)

    print("=" * 60)
    print(f"📈 Devparade X Growth & Member RT Engine")
    print(f"   {now.strftime('%Y-%m-%d %H:%M JST')}")
    print("=" * 60)

    log = load_growth_log()

    # 1. アカウント統計取得
    stats = {}
    try:
        from x_client import get_my_info
        stats = get_my_info() or {}
        if stats:
            print(f"👤 公式アカウント: @{stats.get('username')}")
            print(f"   フォロワー: {stats.get('followers')} / フォロー中: {stats.get('following')}")
            log.setdefault("followers_history", []).append({
                "date": now.strftime("%Y-%m-%d %H:%M"),
                "count": stats.get("followers", 0),
            })
            log["followers_history"] = log["followers_history"][-60:]
    except Exception as e:
        print(f"⚠️ アカウント統計取得スキップ: {e}")

    # 2. メンバーのツイート自動リツイート
    member_rts = 0
    try:
        from member_retweet_engine import process_member_retweets
        import asyncio
        member_rts = asyncio.run(process_member_retweets(dry_run=DRY_RUN)) or 0
    except Exception as e:
        try:
            from scripts.member_retweet_engine import process_member_retweets
            import asyncio
            member_rts = asyncio.run(process_member_retweets(dry_run=DRY_RUN)) or 0
        except Exception as e2:
            print(f"⚠️ メンバーRTエンジン実行エラー: {e2}")

    # 3. ターゲット層への安全ないいね巡回
    target_likes = run_target_likes(max_likes=6)

    # 4. バンド言及ツイートへのいいね巡回
    brand_likes = run_brand_mentions_like(max_likes=4)

    # 5. レポート生成
    generate_growth_report(stats, target_likes, brand_likes, member_rts, log)

    # ログ保存
    log.setdefault("runs", []).append({
        "date": now.strftime("%Y-%m-%d %H:%M"),
        "followers": stats.get("followers", 0),
        "target_likes": target_likes,
        "brand_likes": brand_likes,
        "member_rts": member_rts,
    })
    log["runs"] = log["runs"][-100:]
    save_growth_log(log)

    print("\n🎉 Growth & RT Engine 巡回完了!")


if __name__ == "__main__":
    main()
