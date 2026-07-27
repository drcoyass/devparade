#!/usr/bin/env python3
"""
🎵 Devparade「夏の終わりに」リリース当日 全SNS一括投稿スクリプト
=================================================================
7/29（配信リリース日）に手動で実行する。
時刻に応じて最適な投稿文を選択・表示する。

使い方:
    python3 scripts/release_day_poster.py          # 現在時刻に応じた投稿を表示
    python3 scripts/release_day_poster.py --all    # 全時間帯の投稿を一覧表示
    python3 scripts/release_day_poster.py --slot 07  # 朝7時の投稿を表示
"""

import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
LINKMAP_URL = "https://link-map.jp/links/t7J6lCsV"
SITE_URL = "https://devparade.jp/"
IG_URL = "https://www.instagram.com/dev.parade/"

# ===== 時間帯別投稿コンテンツ =====
POSTS = {
    "00": {
        "time": "00:00 JST",
        "label": "🌙 0時ジャスト解禁",
        "platform": "X（Twitter）",
        "text": f"""0時。解禁。

「夏の終わりに」/ Devparade

15年間、ずっと作り続けた音楽。
今夜、世界に解き放つ。

Spotify / Apple Music / YouTube Music
全サービスで今すぐ聴けます👇

{LINKMAP_URL}

#デブパレード #夏の終わりに #配信開始 #Devparade"""
    },
    "07": {
        "time": "07:00 JST",
        "label": "☀️ 朝の告知メイン",
        "platform": "X / Instagram",
        "x": f"""🎵 配信スタート！

「夏の終わりに」/ Devparade

15年の沈黙を破る、初のリリース。
デブたちが本気で作った、夏の終わりのラブソング。

Spotify / Apple Music / Amazon / YouTube Music
今すぐ聴けます👇
{LINKMAP_URL}

再生・シェアで拡散を！🍖

#デブパレード #夏の終わりに #配信開始 #新曲""",
        "instagram": f"""🎵 本日リリース！

「夏の終わりに」/ Devparade

ついに、出した。

15年間、ずっと温めてきた音楽を、2026年の夏に届けることができた。

この曲は、誰もが感じたことのある「夏の終わりの切なさ」について書いた曲です。
失った恋、遠ざかった友達、あの頃の自分。

デブパレードのメロディに乗せて、あなたの「夏の終わり」を思い出してほしい。

Spotify / Apple Music / YouTube Music などで今すぐ聴けます。
プロフィールのリンクから👆

#デブパレード #デブパレ #夏の終わりに #配信開始 #新曲 #ロックバンド #インディーズバンド #バッチコイ #NARUTO #ポジデブ #拡散希望"""
    },
    "12": {
        "time": "12:00 JST",
        "label": "🍖 昼 エンゲージメント強化",
        "platform": "X（Twitter）",
        "text": f"""「夏の終わりに」配信中！

聴いた人、感想リプ下さい🍖

「切ない」「懐かしい」「やっぱりデブパレードだ」
なんでもいい。メンバー全員で読んでます。

{LINKMAP_URL}

#デブパレード #夏の終わりに"""
    },
    "18": {
        "time": "18:00 JST",
        "label": "🌆 夕方 YouTube/Shorts",
        "platform": "YouTube Shorts / TikTok",
        "text": """【動画投稿タイミング】

✅ リリック動画（generate_natsunoowarini.sh で生成済み）を投稿

キャプション（コピペ用）:
「夏の終わりに」/ Devparade

夏の終わりのリズムが、また僕を惑わせた。
15年ぶりに鳴らす、デブたちのラブソング。

配信中👇
https://link-map.jp/links/t7J6lCsV

#デブパレード #夏の終わりに #NARUTO #バッチコイ #ロックバンド #Shorts"""
    },
    "20": {
        "time": "20:00 JST",
        "label": "🌙 夜 NARUTO層訴求",
        "platform": "X（Twitter）",
        "text": f"""NARUTOのED「バッチコイ!!!」のデブパレードが
15年ぶりに新曲出した。

「夏の終わりに」— 今日から配信中。

バッチコイを知ってるならぜひ聴いてみて。
あの頃より全員デカくなったけど、
音楽への情熱はそのままです🍖

{LINKMAP_URL}

#NARUTO #バッチコイ #デブパレード #夏の終わりに"""
    },
    "21": {
        "time": "21:00 JST",
        "label": "🌃 夜 Instagram Reels",
        "platform": "Instagram Reels",
        "text": """【Instagram Reels 投稿タイミング】

✅ 動画ファイル: video-automation/output/natsu_no_owari_ni_lyric.mp4

Reelsキャプション（コピペ用）:
「夏の終わりに」/ Devparade 🍖

あなたの夏の終わりを、俺たちのサウンドで彩ってほしい。

配信リンクはプロフィールから↗️

#デブパレード #夏の終わりに #NARUTO #バッチコイ #ロックバンド #リリック動画"""
    }
}

# ===== 翌日以降のフォロー投稿 =====
FOLLOW_UP = f"""【7/30以降 フォロー投稿】

「夏の終わりに」、聴いてくれてありがとう。

実はこの曲、8/19リリース予定の1stアルバム
『全ての武器をお箸に』に収録されています。

先行シングルを聴いてくれた人に、
アルバム全曲聴いてほしい。
15年分の全部が詰まってます🍖

予約はこちら👇
{SITE_URL}

#デブパレード #全ての武器をお箸に #8月19日"""


def get_current_slot():
    """現在時刻から対応するスロットを返す"""
    now = datetime.now(JST)
    hour = now.hour
    if hour < 7:
        return "00"
    elif hour < 12:
        return "07"
    elif hour < 18:
        return "12"
    elif hour < 20:
        return "18"
    elif hour < 21:
        return "20"
    else:
        return "21"


def print_post(slot_key, post_data):
    print(f"\n{'='*55}")
    print(f"⏰ {post_data['time']} — {post_data['label']}")
    print(f"📱 投稿先: {post_data['platform']}")
    print(f"{'='*55}")

    if 'text' in post_data:
        print(f"\n【投稿テキスト】（{len(post_data['text'])}文字）")
        print("-" * 40)
        print(post_data['text'])
        print("-" * 40)
    elif 'x' in post_data:
        print(f"\n【X投稿】（{len(post_data['x'])}文字）")
        print("-" * 40)
        print(post_data['x'])
        print("-" * 40)
        print(f"\n【Instagram投稿】")
        print("-" * 40)
        print(post_data['instagram'])
        print("-" * 40)


def main():
    now = datetime.now(JST)
    args = sys.argv[1:]

    print(f"\n🎵 Devparade「夏の終わりに」リリース当日 投稿管理ツール")
    print(f"   {now.strftime('%Y-%m-%d %H:%M JST')}")
    print(f"   配信リンク: {LINKMAP_URL}")

    if "--all" in args:
        print("\n\n📋 全時間帯の投稿コンテンツ:")
        for slot_key, post_data in sorted(POSTS.items()):
            print_post(slot_key, post_data)
        print(f"\n\n{'='*55}")
        print("📋 7/30以降 フォロー投稿")
        print("="*55)
        print(FOLLOW_UP)
        return

    # 特定スロット指定
    for arg in args:
        if arg.startswith("--slot"):
            slot = arg.split("=")[-1] if "=" in arg else args[args.index(arg)+1]
            if slot in POSTS:
                print_post(slot, POSTS[slot])
            else:
                print(f"❌ スロット {slot} は存在しません。利用可能: {list(POSTS.keys())}")
            return

    # 現在時刻に応じたスロット
    current_slot = get_current_slot()
    post_data = POSTS[current_slot]
    print(f"\n⚡ 現在時刻に対応する投稿:")
    print_post(current_slot, post_data)

    # 次のスロットも表示
    slot_keys = sorted(POSTS.keys())
    current_idx = slot_keys.index(current_slot)
    if current_idx < len(slot_keys) - 1:
        next_slot = slot_keys[current_idx + 1]
        next_post = POSTS[next_slot]
        print(f"\n\n⏭️  次の投稿: {next_post['time']} — {next_post['label']}")
        print(f"   (--slot {next_slot} で表示)")

    print(f"\n\n{'='*55}")
    print("📋 全投稿を見るには: python3 scripts/release_day_poster.py --all")
    print("="*55)


if __name__ == "__main__":
    main()
