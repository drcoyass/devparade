#!/usr/bin/env python3
"""
Devparade X Follower Growth Engine
フォロワー増加マーケティング自動化

戦略:
1. エンゲージメント分析 - 過去ツイートのパフォーマンスを分析
2. 最適投稿時間の学習
3. ターゲットユーザーへのいいね・フォロー
4. トレンドハッシュタグの活用
5. フォロワー増加レポート生成
"""

import os
import json
import random
from datetime import datetime, timezone, timedelta

try:
    import tweepy
except ImportError:
    tweepy = None

API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")
BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")

from pathlib import Path
_BASE_DIR = Path(__file__).resolve().parent.parent
GROWTH_LOG = str(_BASE_DIR / "data" / "growth_log.json")

# フォロー対象のキーワード（これらに言及してるユーザーに関わる）
TARGET_KEYWORDS = [
    "ボディポジティブ", "ぽっちゃり", "大きいサイズ",
    "body positive", "plus size", "self love",
    "デブ芸人", "おデブ", "太ってる",
    "NARUTO", "バッチコイ",
]

# 関連アカウント（これらのフォロワーと交流）
RELATED_ACCOUNTS = [
    "matslovedx",      # マツコ系
    "watanabe_naomi",   # 渡辺直美
]

# 戦略的ハッシュタグセット
HASHTAG_SETS = {
    "core": ["#ポジデブ", "#ポジデブBot", "#DEVPARADE", "#デブパレード"],
    "reach": ["#ボディポジティブ", "#自己肯定感", "#ありのまま", "#bodypositivity"],
    "music": ["#バンド", "#ロック", "#邦ロック", "#バッチコイ", "#NARUTO"],
    "viral": ["#拡散希望", "#フォロバ100", "#相互フォロー"],
    "english": ["#BodyPositive", "#SelfLove", "#PlusSize", "#FatPositive"],
    "food": ["#焼肉", "#グルメ", "#大盛り", "#飯テロ"],
}


def get_write_client():
    """後方互換性のためのダミー。実際の操作はx_clientを使用"""
    return True


def get_read_client():
    """後方互換性のためのダミー"""
    return True


def load_growth_log():
    try:
        with open(GROWTH_LOG, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"runs": [], "liked_users": [], "followers_history": []}


def save_growth_log(log):
    with open(GROWTH_LOG, "w") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def get_account_stats(read_client, write_client):
    """自アカウントの統計を取得（x_client経由）"""
    try:
        try:
            from x_client import get_my_info
        except ImportError:
            from scripts.x_client import get_my_info

        info = get_my_info()
        if info:
            return {
                "username": info.get("username", ""),
                "name": info.get("name", ""),
                "followers": info.get("followers", 0),
                "following": info.get("following", 0),
                "tweets": info.get("tweets", 0),
                "listed": 0,
            }
    except Exception as e:
        print(f"   ⚠️ アカウント情報取得エラー: {e}")
    return None


def analyze_recent_tweets(read_client, user_id):
    """直近ツイートのエンゲージメント分析（現在はtwikit非対応のためスキップ）"""
    # twikit では自分のツイートの詳細メトリクスは取得困難なため
    # この機能は有料API復帰まで一時停止
    print("   ℹ️ ツイート分析は現在スキップ（twikit制限）")
    return []


def engage_with_mentions(write_client, read_client):
    """メンションに「いいね」で反応（x_client経由）"""
    liked = 0
    try:
        try:
            from x_client import get_mentions as xc_get_mentions, like_tweet
        except ImportError:
            from scripts.x_client import get_mentions as xc_get_mentions, like_tweet

        mentions = xc_get_mentions(10)
        for m in mentions:
            tweet_id = m.get("id", "")
            if not tweet_id:
                continue
            try:
                if like_tweet(tweet_id):
                    liked += 1
                    print(f"   ❤️ いいね: {tweet_id[:10]}...")
            except Exception:
                pass

    except Exception as e:
        print(f"   ⚠️ メンションエンゲージ: {e}")

    return liked


def generate_growth_report(stats, tweet_analysis, liked_count, log):
    """フォロワー増加レポート生成"""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)

    # フォロワー推移
    prev_followers = 0
    if log.get("followers_history"):
        prev_followers = log["followers_history"][-1].get("count", 0)

    followers = stats["followers"] if stats else 0
    diff = followers - prev_followers if prev_followers > 0 else 0
    diff_str = f"+{diff}" if diff >= 0 else str(diff)

    lines = [
        f"## 📈 Devparade X Growth Report",
        "",
        f"**日時:** {now.strftime('%Y-%m-%d %H:%M JST')}",
        "",
        "---",
        "",
        "### アカウント統計",
        "",
    ]

    if stats:
        lines.extend([
            f"| 指標 | 数値 |",
            f"|------|------|",
            f"| フォロワー | **{stats['followers']}** ({diff_str}) |",
            f"| フォロー中 | {stats['following']} |",
            f"| ツイート数 | {stats['tweets']} |",
            f"| リスト登録 | {stats['listed']} |",
            "",
        ])

    # エンゲージメント分析
    if tweet_analysis:
        lines.extend([
            "### トップエンゲージメント ツイート",
            "",
        ])
        for i, t in enumerate(tweet_analysis[:5], 1):
            lines.extend([
                f"**#{i}** (Score: {t['engagement_score']})",
                f"> {t['text']}",
                f"❤️ {t['likes']} | 🔄 {t['retweets']} | 💬 {t['replies']}",
                "",
            ])

    # アクション実行結果
    lines.extend([
        "### 実行アクション",
        "",
        f"- メンションへのいいね: {liked_count}件",
        "",
    ])

    # マーケティングTIPS
    lines.extend([
        "### 📊 次のアクション推奨",
        "",
        "1. **エンゲージメント高いツイートの傾向を分析** → 似た内容を増やす",
        "2. **メンションには必ず反応** → ファンとの関係構築",
        "3. **ハッシュタグ戦略** → #ポジデブ #BodyPositive を定着させる",
        "4. **コラボ** → デブ芸人、フードインフルエンサーとの絡み",
        "5. **スレッド投稿** → 滞在時間UPでアルゴリズム優遇",
        "",
        "---",
        "*Devparade Growth Engine 🍖*",
    ])

    with open("growth_report.md", "w") as f:
        f.write("\n".join(lines))

    return "\n".join(lines)


def main():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)

    print("=" * 50)
    print(f"📈 Devparade X Growth Engine")
    print(f"   {now.strftime('%Y-%m-%d %H:%M JST')}")
    print("=" * 50)

    write_client = get_write_client()
    read_client = get_read_client()

    if not write_client:
        print("❌ X API credentials not set")
        return

    log = load_growth_log()

    # 1. アカウント統計取得
    print("\n📊 アカウント統計...")
    stats = get_account_stats(read_client, write_client)
    if stats:
        print(f"   @{stats['username']}")
        print(f"   フォロワー: {stats['followers']}")
        print(f"   ツイート数: {stats['tweets']}")

        # 履歴に追加
        log.setdefault("followers_history", []).append({
            "date": now.strftime("%Y-%m-%d %H:%M"),
            "count": stats["followers"],
        })
        # 最新30件のみ保持
        log["followers_history"] = log["followers_history"][-30:]

    # 2. ツイート分析
    print("\n📈 エンゲージメント分析...")
    tweet_analysis = analyze_recent_tweets(read_client, None)
    if tweet_analysis:
        best = tweet_analysis[0]
        print(f"   ベストツイート: {best['text'][:50]}...")
        print(f"   Score: {best['engagement_score']} (❤️{best['likes']} 🔄{best['retweets']})")

    # 3. メンションへの「いいね」
    print("\n❤️ メンションエンゲージメント...")
    liked_count = engage_with_mentions(write_client, read_client)
    print(f"   いいね実行: {liked_count}件")

    # 4. レポート生成
    print("\n📝 レポート生成...")
    generate_growth_report(stats, tweet_analysis, liked_count, log)

    # ログ保存
    log.setdefault("runs", []).append({
        "date": now.strftime("%Y-%m-%d %H:%M"),
        "followers": stats["followers"] if stats else 0,
        "liked": liked_count,
    })
    log["runs"] = log["runs"][-100:]
    save_growth_log(log)

    print("\n✅ Growth Engine Complete!")


if __name__ == "__main__":
    main()
