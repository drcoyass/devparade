#!/usr/bin/env python3
"""
🔄 デブパレード メンバーツイート超拡散エンジン (v2.0)
=====================================================
メンバー（ハンサム判治, COYASS, ugazin, ぺー, TAH）のツイートを検知し、
1. 公式から即時「いいね ❤️」
2. 重要キーワード検出時に「熱狂コメント付き引用ポスト（Quote Tweet）」
3. 通常時は公式「リツイート 🔄」
4. COYASSアカウントでの相互拡散

メンバーアカウント:
- ハンサム判治: @han363 (Vo./Leader)
- COYASS: @coyass (MC)
- ugazin: @ugazin (Gt.)
- ぺー: @tapemewonder (Ba.)
- TAH: @lolMusika (Dr.)
"""

import os
import sys
import json
import random
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

_BASE_DIR = Path(__file__).resolve().parent.parent
MEMBER_RETWEET_FILE = _BASE_DIR / "data" / "member_retweeted_ids.json"

MEMBERS = [
    {"name": "ハンサム判治", "screen_name": "han363", "role": "Vo./Leader", "tag": "判治リーダー"},
    {"name": "COYASS", "screen_name": "coyass", "role": "MC", "tag": "COYASS"},
    {"name": "ugazin", "screen_name": "ugazin", "role": "Gt.", "tag": "ugazin"},
    {"name": "ぺー", "screen_name": "tapemewonder", "role": "Ba.", "tag": "ぺー"},
    {"name": "TAH", "screen_name": "lolMusika", "role": "Dr.", "tag": "TAH"},
]

# 引用ポストを優先発動するキーワード
HIGHLIGHT_KEYWORDS = [
    "デブパレード", "devparade", "9月4日", "夏の終わりに", "バッチコイ",
    "新曲", "リリース", "配信", "ライブ", "ワンマン", "肉", "アルバム",
    "スタジオ", "リハ", "mv", "spotify", "apple music"
]

# メンバーごとの引用熱狂コメントテンプレート
QUOTE_TEMPLATES = {
    "han363": [
        "🍖 【魂の言霊】ハンサム判治リーダーからの熱いメッセージ！全員受け止めろ！🔥",
        "🍖 判治リーダーが吠えた！このバイブス、全人類に届け！🔥 #デブパレード",
        "🍖 Vo.ハンサム判治の言葉の重み＝92kg！心して聴け！🔥"
    ],
    "coyass": [
        "🍖 【言霊炸裂】MC COYASSの極太パンチラインを体感せよ！🎙️🔥",
        "🍖 ドクターCOYASSからの激熱メッセージ！全員チェック！🎙️✨ #デブパレード",
        "🍖 COYASSの魂のラップ＆スピリット！拡散せよ！🎙️🍖"
    ],
    "ugazin": [
        "🍖 【超重量級】Gt. ugazinのヘヴィな魂のグルーヴを喰らえ！🎸🔥",
        "🍖 ギタリストugazinの爆音バイブス！この音の太さ、必聴！🎸🍖 #デブパレード",
        "🍖 ugazinのロック魂！重低音で世界を揺らすぜ！🎸✨"
    ],
    "tapemewonder": [
        "🍖 【低音爆発】Ba. ぺーの唸る重低音グルーヴ、要チェック！⚡🔥",
        "🍖 ベーシストぺーからのメッセージ！大地を揺らすベースを体感せよ！🎸🍖 #デブパレード",
    ],
    "lolMusika": [
        "🍖 【爆裂ビート】Dr. TAHの激熱ドラミングが止まらない！🥁🔥",
        "🍖 ドラマーTAHの超重量級グルーヴ！全員ついてこい！🥁🍖 #デブパレード",
    ]
}


def load_retweeted():
    try:
        with open(MEMBER_RETWEET_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_retweeted(retweeted_set):
    MEMBER_RETWEET_FILE.parent.mkdir(parents=True, exist_ok=True)
    recent_ids = list(retweeted_set)[-1000:]
    with open(MEMBER_RETWEET_FILE, "w", encoding="utf-8") as f:
        json.dump(recent_ids, f, indent=2)


def is_highlight_tweet(text):
    text_lower = text.lower()
    return any(k in text_lower for k in HIGHLIGHT_KEYWORDS)


async def process_member_retweets(dry_run=False):
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst).strftime("%Y-%m-%d %H:%M JST")
    print("=" * 60)
    print(f"🎸 デブパレード メンバーツイート超拡散エンジン巡回 [{now}]")
    print("=" * 60)

    try:
        from x_client import _get_twikit_client
    except ImportError:
        try:
            from scripts.x_client import _get_twikit_client
        except ImportError:
            print("❌ x_client モジュールが見つかりません")
            return 0

    client = await _get_twikit_client()
    if not client:
        print("❌ 公式アカウント (@dev_parade) のクライアント取得に失敗しました")
        return 0

    retweeted_ids = load_retweeted()
    total_action_count = 0

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

                if is_reply:
                    continue

                if tid in retweeted_ids:
                    continue

                print(f"  ✨ 新着ツイート検出! ID={tid}")
                print(f"     「{text[:50].replace(chr(10), ' ')}...」")

                if dry_run:
                    print(f"     🔍 [DRY RUN] いいね＆リツイート処理をスキップ")
                    retweeted_ids.add(tid)
                    total_action_count += 1
                    continue

                # 1. 自動いいね ❤️
                try:
                    await client.favorite_tweet(tid)
                    print(f"     ❤️ 公式からいいね完了!")
                except Exception as e:
                    print(f"     ⚠️ いいねスキップ: {e}")

                await asyncio.sleep(1.5)

                # 2. 引用ツイート or 通常リツイートの判定
                tweet_url = f"https://x.com/{s_name}/status/{tid}"
                should_quote = is_highlight_tweet(text) or random.random() < 0.4

                if should_quote:
                    # 引用ポスト（Quote Tweet）
                    templates = QUOTE_TEMPLATES.get(s_name, [f"🍖 【メンバー発信】{m_name}の最新ポスト！チェック！🔥"])
                    quote_comment = random.choice(templates)
                    quote_post_text = f"{quote_comment}\n\n{tweet_url}"
                    try:
                        res = await client.create_tweet(text=quote_post_text)
                        print(f"     💬 【引用ポスト成功!】: {quote_comment[:30]}...")
                        retweeted_ids.add(tid)
                        total_action_count += 1
                    except Exception as eq:
                        print(f"     ⚠️ 引用ポスト失敗、通常RTにフォールバック: {eq}")
                        try:
                            await client.retweet(tid)
                            print(f"     🎉 通常リツイート成功！")
                            retweeted_ids.add(tid)
                            total_action_count += 1
                        except Exception as er:
                            print(f"     ❌ 通常リツイートも失敗: {er}")
                else:
                    # 通常リツイート
                    try:
                        await client.retweet(tid)
                        print(f"     🎉 通常リツイート成功！")
                        retweeted_ids.add(tid)
                        total_action_count += 1
                    except Exception as e:
                        print(f"     ❌ リツイート失敗: {e}")

                await asyncio.sleep(2.5)

        except Exception as e:
            print(f"   ⚠️ @{s_name} のタイムライン取得エラー: {e}")

    save_retweeted(retweeted_ids)
    print(f"\n🏁 メンバー巡回完了: 拡散アクション実行 {total_action_count} 件")
    return total_action_count


def main():
    parser = argparse.ArgumentParser(description="メンバーツイート超拡散エンジン")
    parser.add_argument("--dry-run", action="store_true", help="実行せずテスト")
    args = parser.parse_args()

    asyncio.run(process_member_retweets(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
