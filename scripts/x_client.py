#!/usr/bin/env python3
"""
x_client.py — Devparade 共通X(Twitter)投稿モジュール

twikit（ブラウザ認証・無料）を優先使用し、
tweepy（公式API・有料）をフォールバックとして保持する。

使い方:
    from x_client import post_tweet, get_mentions, get_my_info

    # ツイート投稿
    tweet_id = post_tweet("テスト投稿 🍖")

    # メンション取得
    mentions = get_mentions()

    # アカウント情報取得
    info = get_my_info()
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# ===== 認証情報 =====
X_USERNAME = os.environ.get("X_USERNAME", "")
X_EMAIL = os.environ.get("X_EMAIL", "")
X_PASSWORD = os.environ.get("X_PASSWORD", "")

# tweepy用 (フォールバック)
X_API_KEY = os.environ.get("X_API_KEY", "")
X_API_SECRET = os.environ.get("X_API_SECRET", "")
X_ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN", "")
X_ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET", "")
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")

# クッキーファイルのパス（セッション持続化用）
COOKIES_FILE = Path(__file__).parent.parent / "data" / "twikit_cookies.json"

# DRY RUN モード
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"


def _has_twikit_creds():
    """twikit用の認証情報があるか"""
    return bool(X_USERNAME and X_EMAIL and X_PASSWORD)


def _has_tweepy_creds():
    """tweepy用の認証情報があるか"""
    return bool(X_API_KEY and X_API_SECRET and X_ACCESS_TOKEN and X_ACCESS_SECRET)


# ===== twikit 方式 =====

async def _get_twikit_client():
    """twikit クライアントを取得（クッキー持続化対応）"""
    try:
        from twikit import Client
    except ImportError:
        print("⚠️ twikit未インストール。pip install twikit を実行してください。")
        return None

    client = Client("ja-JP")

    # クッキーファイルが存在すれば読み込む（再ログイン不要）
    if COOKIES_FILE.exists():
        try:
            client.load_cookies(str(COOKIES_FILE))
            print("🍪 セッションクッキーを読み込みました")
            return client
        except Exception as e:
            print(f"⚠️ クッキー読み込み失敗（再ログインします）: {e}")

    # 新規ログイン
    if not _has_twikit_creds():
        print("⚠️ twikit認証情報なし (X_USERNAME, X_EMAIL, X_PASSWORD)")
        return None

    try:
        await client.login(
            auth_info_1=X_USERNAME,
            auth_info_2=X_EMAIL,
            password=X_PASSWORD,
        )
        # クッキーを保存（次回以降はログイン不要）
        COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        client.save_cookies(str(COOKIES_FILE))
        print("✅ twikit ログイン成功 & クッキー保存完了")
        return client
    except Exception as e:
        print(f"❌ twikit ログイン失敗: {e}")
        return None


async def _twikit_post(text):
    """twikit でツイート投稿"""
    client = await _get_twikit_client()
    if not client:
        return None

    try:
        result = await client.create_tweet(text=text)
        tweet_id = result.id if hasattr(result, 'id') else str(result)
        print(f"✅ [twikit] 投稿成功! Tweet ID: {tweet_id}")
        return str(tweet_id)
    except Exception as e:
        print(f"❌ [twikit] 投稿失敗: {e}")
        return None


async def _twikit_get_mentions(count=20):
    """twikit でメンション取得"""
    client = await _get_twikit_client()
    if not client:
        return []

    try:
        notifications = await client.get_notifications("mentions")
        mentions = []
        if notifications:
            for notif in notifications[:count]:
                mentions.append({
                    "id": str(notif.id) if hasattr(notif, 'id') else "",
                    "text": notif.text if hasattr(notif, 'text') else "",
                    "username": notif.user.screen_name if hasattr(notif, 'user') and notif.user else "unknown",
                })
        print(f"📩 [twikit] メンション {len(mentions)}件取得")
        return mentions
    except Exception as e:
        print(f"⚠️ [twikit] メンション取得失敗: {e}")
        return []


async def _twikit_get_my_info():
    """twikit でアカウント情報取得"""
    client = await _get_twikit_client()
    if not client:
        return None

    try:
        user = await client.user()
        return {
            "username": user.screen_name if hasattr(user, 'screen_name') else "",
            "name": user.name if hasattr(user, 'name') else "",
            "followers": user.followers_count if hasattr(user, 'followers_count') else 0,
            "following": user.following_count if hasattr(user, 'following_count') else 0,
            "tweets": user.statuses_count if hasattr(user, 'statuses_count') else 0,
        }
    except Exception as e:
        print(f"⚠️ [twikit] アカウント情報取得失敗: {e}")
        return None


async def _twikit_reply(text, reply_to_tweet_id):
    """twikit でリプライ投稿"""
    client = await _get_twikit_client()
    if not client:
        return None

    try:
        result = await client.create_tweet(
            text=text,
            reply_to=reply_to_tweet_id,
        )
        tweet_id = result.id if hasattr(result, 'id') else str(result)
        print(f"✅ [twikit] リプライ成功! Tweet ID: {tweet_id}")
        return str(tweet_id)
    except Exception as e:
        print(f"❌ [twikit] リプライ失敗: {e}")
        return None


async def _twikit_search(query, count=10):
    """twikit でツイート検索"""
    client = await _get_twikit_client()
    if not client:
        return []

    try:
        results = await client.search_tweet(query, product="Latest", count=count)
        tweets = []
        for tweet in results:
            tweets.append({
                "id": str(tweet.id),
                "text": tweet.text if hasattr(tweet, 'text') else "",
                "username": tweet.user.screen_name if hasattr(tweet, 'user') and tweet.user else "unknown",
            })
        print(f"🔍 [twikit] 検索結果 {len(tweets)}件")
        return tweets
    except Exception as e:
        print(f"⚠️ [twikit] 検索失敗: {e}")
        return []


async def _twikit_like(tweet_id):
    """twikit でいいね"""
    client = await _get_twikit_client()
    if not client:
        return False

    try:
        await client.favorite_tweet(tweet_id)
        print(f"❤️ [twikit] いいね成功: {tweet_id}")
        return True
    except Exception as e:
        print(f"⚠️ [twikit] いいね失敗: {e}")
        return False


# ===== tweepy 方式（フォールバック） =====

def _tweepy_post(text):
    """tweepy でツイート投稿（有料API・フォールバック）"""
    if not _has_tweepy_creds():
        return None

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_SECRET,
            wait_on_rate_limit=True,
        )
        response = client.create_tweet(text=text)
        tweet_id = response.data['id']
        print(f"✅ [tweepy] 投稿成功! Tweet ID: {tweet_id}")
        return str(tweet_id)
    except Exception as e:
        print(f"❌ [tweepy] 投稿失敗: {e}")
        return None


def _tweepy_reply(text, reply_to_tweet_id):
    """tweepy でリプライ（フォールバック）"""
    if not _has_tweepy_creds():
        return None

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_SECRET,
            wait_on_rate_limit=True,
        )
        response = client.create_tweet(text=text, in_reply_to_tweet_id=reply_to_tweet_id)
        tweet_id = response.data['id']
        print(f"✅ [tweepy] リプライ成功! Tweet ID: {tweet_id}")
        return str(tweet_id)
    except Exception as e:
        print(f"❌ [tweepy] リプライ失敗: {e}")
        return None


# ===== 公開API（同期ラッパー） =====

def post_tweet(text):
    """
    ツイートを投稿する（メインAPI）。
    twikit → tweepy の順で試行。
    DRY_RUN=true の場合は投稿せずにテキストを表示。
    """
    if DRY_RUN:
        print(f"🔍 [DRY RUN] 投稿スキップ ({len(text)}文字)")
        print(f"   {text[:100]}...")
        return "dry_run"

    # 方式1: twikit（無料）
    if _has_twikit_creds() or COOKIES_FILE.exists():
        tweet_id = asyncio.run(_twikit_post(text))
        if tweet_id:
            return tweet_id

    # 方式2: tweepy（有料API・フォールバック）
    if _has_tweepy_creds():
        tweet_id = _tweepy_post(text)
        if tweet_id:
            return tweet_id

    print("❌ 全ての投稿方式が失敗しました。")
    print("   → GitHub Secrets に X_USERNAME, X_EMAIL, X_PASSWORD を設定してください。")
    return None


def reply_tweet(text, reply_to_tweet_id):
    """
    リプライを投稿する。
    twikit → tweepy の順で試行。
    """
    if DRY_RUN:
        print(f"🔍 [DRY RUN] リプライスキップ → {reply_to_tweet_id}")
        return "dry_run"

    # 方式1: twikit
    if _has_twikit_creds() or COOKIES_FILE.exists():
        tweet_id = asyncio.run(_twikit_reply(text, reply_to_tweet_id))
        if tweet_id:
            return tweet_id

    # 方式2: tweepy
    if _has_tweepy_creds():
        tweet_id = _tweepy_reply(text, reply_to_tweet_id)
        if tweet_id:
            return tweet_id

    print("❌ リプライ失敗")
    return None


def get_mentions(count=20):
    """メンション取得"""
    if _has_twikit_creds() or COOKIES_FILE.exists():
        return asyncio.run(_twikit_get_mentions(count))
    return []


def get_my_info():
    """アカウント情報取得"""
    if _has_twikit_creds() or COOKIES_FILE.exists():
        return asyncio.run(_twikit_get_my_info())

    # tweepy フォールバック
    if _has_tweepy_creds():
        try:
            import tweepy
            client = tweepy.Client(
                consumer_key=X_API_KEY,
                consumer_secret=X_API_SECRET,
                access_token=X_ACCESS_TOKEN,
                access_token_secret=X_ACCESS_SECRET,
                wait_on_rate_limit=True,
            )
            me = client.get_me(user_fields=["public_metrics"])
            if me.data:
                metrics = me.data.public_metrics or {}
                return {
                    "username": me.data.username,
                    "name": me.data.name,
                    "followers": metrics.get("followers_count", 0),
                    "following": metrics.get("following_count", 0),
                    "tweets": metrics.get("tweet_count", 0),
                }
        except Exception as e:
            print(f"⚠️ [tweepy] アカウント情報取得失敗: {e}")

    return None


def search_tweets(query, count=10):
    """ツイート検索"""
    if _has_twikit_creds() or COOKIES_FILE.exists():
        return asyncio.run(_twikit_search(query, count))
    return []


def like_tweet(tweet_id):
    """いいね"""
    if DRY_RUN:
        print(f"🔍 [DRY RUN] いいねスキップ: {tweet_id}")
        return True

    if _has_twikit_creds() or COOKIES_FILE.exists():
        return asyncio.run(_twikit_like(tweet_id))
    return False


# ===== テスト =====

def _test():
    """接続テスト"""
    print("=" * 50)
    print("🧪 X Client 接続テスト")
    print("=" * 50)

    print(f"\n📋 認証情報:")
    print(f"   twikit: {'✅' if _has_twikit_creds() else '❌'} (X_USERNAME, X_EMAIL, X_PASSWORD)")
    print(f"   tweepy: {'✅' if _has_tweepy_creds() else '❌'} (X_API_KEY etc.)")
    print(f"   cookies: {'✅ 存在' if COOKIES_FILE.exists() else '❌ なし'}")
    print(f"   DRY_RUN: {DRY_RUN}")

    if _has_twikit_creds() or COOKIES_FILE.exists():
        print("\n🔌 twikit 接続テスト...")
        info = get_my_info()
        if info:
            print(f"   ✅ @{info['username']} ({info['name']})")
            print(f"   フォロワー: {info['followers']} / フォロー中: {info['following']}")
        else:
            print("   ❌ 接続失敗")
    else:
        print("\n⚠️ twikit認証情報なし。テストスキップ。")

    print("\n✅ テスト完了")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _test()
    else:
        print("使い方: python x_client.py --test")
        print("  または: from x_client import post_tweet")
