#!/usr/bin/env python3
"""
🔄 デブパレード公式ツイート ➔ Dr.COYASSアカウント自動リツイートスクリプト
===================================================================
@dev_parade がツイートした内容を検知し、@COYASS のアカウントで即時リツイートします。

使い方:
    python3 scripts/auto_retweet_coyass.py                     # 最新ツイートを検知してリツイート
    python3 scripts/auto_retweet_coyass.py --tweet-id <ID>     # 特定のツイートIDをリツイート
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
RETWEETED_FILE = _BASE_DIR / "data" / "coyass_retweeted_ids.json"


async def main():
    parser = argparse.ArgumentParser(description="公式ツイートを @coyass で自動リツイート")
    parser.add_argument("--tweet-id", help="特定のリツイート対象ツイートID")
    parser.add_argument("--dry-run", action="store_true", help="リツイートを実行せず確認のみ")
    args = parser.parse_args()

    # twikit のインポート
    try:
        from twikit import Client
    except ImportError:
        print("❌ twikit/twifork がインストールされていません")
        return

    # COYASS のクッキー取得
    coyass_env = os.environ.get("COYASS_COOKIES_JSON", "")
    cookies = None
    if coyass_env:
        try:
            cookies = json.loads(coyass_env)
        except Exception:
            pass

    # ローカルファイルからのフォールバック
    if not cookies:
        local_coyass_file = _BASE_DIR / "data" / "coyass_cookies.json"
        if local_coyass_file.exists():
            with open(local_coyass_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)

    if not cookies:
        print("❌ COYASS のCookieが見つかりません (COYASS_COOKIES_JSON)")
        return

    # クライアント初期化
    client = Client("ja-JP")
    client.set_cookies(cookies)

    # アカウント確認
    try:
        user = await client.user()
        print(f"👤 実行アカウント: @{user.screen_name} ({user.name})")
        if user.screen_name.lower() != "coyass":
            print(f"⚠️ アカウントが @coyass ではありません (@{user.screen_name})。処理を中断します。")
            return
    except Exception as e:
        print(f"⚠️ ユーザー情報取得スキップ (Cloudflare等): {e}")

    # 過去リツイート済みIDの読み込み
    retweeted_ids = set()
    if RETWEETED_FILE.exists():
        try:
            with open(RETWEETED_FILE, "r", encoding="utf-8") as f:
                retweeted_ids = set(json.load(f))
        except Exception:
            pass

    targets = []
    if args.tweet_id:
        targets.append(args.tweet_id)
    else:
        # @dev_parade の最新ツイートを取得
        print("🔍 @dev_parade の最新ツイートを取得中...")
        try:
            dev_user = await client.get_user_by_screen_name("dev_parade")
            tweets = await dev_user.get_tweets("Tweets", count=5)
            for t in tweets:
                tid = str(t.id)
                if tid not in retweeted_ids:
                    targets.append(tid)
                    print(f"  ・新着ツイート検出: ID={tid} ({t.text[:30]}...)")
        except Exception as e:
            print(f"⚠️ 公式ツイートタイムライン取得エラー: {e}")

    if not targets:
        print("✅ 新たにリツイートするツイートはありません。")
        return

    # リツイート実行
    for tid in targets:
        if tid in retweeted_ids and not args.tweet_id:
            continue

        print(f"\n🔄 リツイート実行中: Tweet ID = {tid}")
        if args.dry_run:
            print("  🔍 DRY RUN: リツイートはスキップされました")
            continue

        try:
            await client.retweet(tid)
            print(f"  🎉 @coyass でリツイート成功！")
            retweeted_ids.add(tid)
        except Exception as e:
            print(f"  ❌ リツイート失敗: {e}")

    # リツイート済みIDの保存
    RETWEETED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RETWEETED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(retweeted_ids), f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
