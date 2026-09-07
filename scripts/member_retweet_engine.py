#!/usr/bin/env python3
"""
🔄 デブパレード メンバーツイート自動リツイートエンジン
=====================================================
メンバー（ハンサム判治, COYASS, ugazin, ぺー, TAH）のツイートを検知し、
デブパレード公式アカウント（@dev_parade）およびCOYASSアカウントで自動リツイートします。

メンバーアカウント:
- ハンサム判治: @han363
- COYASS: @coyass
- ugazin: @ugazin
- ぺー: @tapemewonder
- TAH: @lolMusika
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

_BASE_DIR = Path(__file__).resolve().parent.parent
MEMBER_RETWEET_FILE = _BASE_DIR / "data" / "member_retweeted_ids.json"

MEMBERS = [
    {"name": "ハンサム判治", "screen_name": "han363", "role": "Vo./Leader"},
    {"name": "COYASS", "screen_name": "coyass", "role": "MC"},
    {"name": "ugazin", "screen_name": "ugazin", "role": "Gt."},
    {"name": "ぺー", "screen_name": "tapemewonder", "role": "Ba."},
    {"name": "TAH", "screen_name": "lolMusika", "role": "Dr."},
]


def load_retweeted():
    try:
        with open(MEMBER_RETWEET_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_retweeted(retweeted_set):
    MEMBER_RETWEET_FILE.parent.mkdir(parents=True, exist_ok=True)
    # 最新1000件のみ保持
    recent_ids = list(retweeted_set)[-1000:]
    with open(MEMBER_RETWEET_FILE, "w", encoding="utf-8") as f:
        json.dump(recent_ids, f, indent=2)


async def process_member_retweets(dry_run=False):
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst).strftime("%Y-%m-%d %H:%M JST")
    print("=" * 60)
    print(f"🎸 デブパレード メンバーツイート自動リツイート巡回 [{now}]")
    print("=" * 60)

    try:
        from x_client import _get_twikit_client
    except ImportError:
        try:
            from scripts.x_client import _get_twikit_client
        except ImportError:
            print("❌ x_client モジュールが見つかりません")
            return

    client = await _get_twikit_client()
    if not client:
        print("❌ 公式アカウント (@dev_parade) のクライアント取得に失敗しました")
        return

    retweeted_ids = load_retweeted()
    total_rt_count = 0

    for member in MEMBERS:
        s_name = member["screen_name"]
        m_name = member["name"]
        print(f"\n🔍 @{s_name} ({m_name}) の最新ツイートを確認中...")

        try:
            user = await client.get_user_by_screen_name(s_name)
            if not user:
                print(f"   ⚠️ ユーザーが見つかりません: @{s_name}")
                continue

            tweets = await user.get_tweets("Tweets", count=5)
            if not tweets:
                print(f"   ツイートなし")
                continue

            for t in tweets:
                tid = str(t.id)
                text = getattr(t, "text", "")
                is_reply = bool(getattr(t, "reply_to", None))

                # 他者へのリプライはノイズ防止のため除外
                if is_reply:
                    continue

                if tid in retweeted_ids:
                    continue

                print(f"  ✨ 新着ツイート検出! ID={tid}")
                print(f"     「{text[:60].replace(chr(10), ' ')}...」")

                if dry_run:
                    print(f"     🔍 [DRY RUN] 公式リツイートをスキップ")
                    retweeted_ids.add(tid)
                    total_rt_count += 1
                    continue

                # 公式アカウントでリツイート
                try:
                    await client.retweet(tid)
                    print(f"     🎉 公式アカウント (@dev_parade) でリツイート成功！")
                    retweeted_ids.add(tid)
                    total_rt_count += 1
                    # APIレート制限対策のインターバル
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"     ❌ リツイート失敗: {e}")

        except Exception as e:
            print(f"   ⚠️ @{s_name} のタイムライン取得エラー: {e}")

    save_retweeted(retweeted_ids)
    print(f"\n🏁 メンバー巡回完了: 新規リツイート {total_rt_count} 件")
    return total_rt_count


def main():
    parser = argparse.ArgumentParser(description="メンバーツイート自動リツイート")
    parser.add_argument("--dry-run", action="store_true", help="リツイートを実行せずテスト")
    args = parser.parse_args()

    asyncio.run(process_member_retweets(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
