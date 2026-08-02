#!/usr/bin/env python3
"""
🎸 Devparade「全ての武器をお箸に」アルバム告知コンテンツ生成
=============================================================
8/5 トラックリスト公開・8/12〜8/19カウントダウン用
全SNS投稿テンプレートを生成して表示する。

使い方:
    python3 scripts/album_content_generator.py           # 8/5全貌公開コンテンツ
    python3 scripts/album_content_generator.py --day 12  # 8/12用コンテンツ
    python3 scripts/album_content_generator.py --day 19  # リリース当日コンテンツ
    python3 scripts/album_content_generator.py --all     # 全日程分を一覧表示
"""

import sys
import random
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
LINKMAP_URL  = "https://link-map.jp/links/t7J6lCsV"
SITE_URL     = "https://devparade.jp/"
SUPPORT_URL  = "https://devparade.jp/support.html"

# ===== アルバム情報 =====
ALBUM_TITLE  = "全ての武器をお箸に"
ALBUM_DATE   = "2026年8月19日（水）"
# ※ lyrics_database.json の "1st Full Album Track" メタデータを正とする
# ※ バッチコイ!!!は2009年の2ndシングルでアルバム未収録
TRACKLIST = [
    ("01", "100CAN DIVE"),
    ("02", "自転車"),
    ("03", "パルフェ"),
    ("04", "うっちゃりファンク（先行デジタルシングル）"),
    ("05", "何年経っても万年FAT お前らにゃ一生わかんねえや"),
    ("06", "夏の終わりに（先行配信中）"),
    ("07", "ハッピー乱デブー"),
    ("08", "ダブルベッド"),
    ("09", "メシを喰わせろ！"),
    ("10", "タチアガレ"),
]

def build_tracklist_text():
    lines = []
    for num, title in TRACKLIST:
        marker = "🎵" if "先行" in title else "  "
        lines.append(f"{marker} {num}. {title}")
    return "\n".join(lines)


# ===== 8/5 アルバム全貌公開コンテンツ =====
AUGUST_5_POSTS = {
    "x_main": f"""📀 1st Full Album「{ALBUM_TITLE}」全貌公開！

【全曲トラックリスト】
01. 100CAN DIVE
02. 自転車
03. パルフェ
04. うっちゃりファンク
05. 何年経っても万年FAT お前らにゃ一生わかんねえや
06. 夏の終わりに ← 先行配信中！
07. ハッピー乱デブー
08. ダブルベッド
09. メシを喰わせろ！
10. タチアガレ

8/19リリース。予約受付中！
{SITE_URL}

#デブパレード #全ての武器をお箸に #8月19日""",

    "x_concept": f"""「全ての武器をお箸に」

このタイトルに込めた想い——

すべての争いを終わりにして、
お箸を持って、みんなで美味しくご飯を食べよう。

それがDevparadeの出した答え。
15年かけて届ける、ポジデブ哲学の集大成。

8/19リリース🍖

{LINKMAP_URL}

#デブパレード #全ての武器をお箸に""",

    "x_singles": f"""先行配信曲が2曲アルバムに収録。

「うっちゃりファンク」（Track 04）
「夏の終わりに」（Track 06）

どちらも全配信サービスで今すぐ聴ける。
アルバムでは新曲も盛りだくさん。

1st Album「{ALBUM_TITLE}」
8/19リリース！

{SITE_URL}

#デブパレード #全ての武器をお箸に""",

    "instagram": f"""📀 「{ALBUM_TITLE}」全貌公開！

＼1st Full Album トラックリスト解禁／

{build_tracklist_text()}

8月19日（水）リリース。

このアルバムは「すべての争いを終わりにして、みんなで美味しくご飯を食べよう」というメッセージが込められています。

重いサウンドで、優しいメッセージを届ける。
それがDevparadeのやり方。

先行シングル「夏の終わりに」は今すぐ配信中。
プロフィールのリンクから聴いてください👆

#デブパレード #デブパレ #全ての武器をお箸に #新アルバム #トラックリスト公開 #ロックバンド #8月19日 #拡散希望""",

    "tiktok_script": """【TikTok/Reels台本 (30秒)】
- BGM: うっちゃりファンク（イントロ）→ 夏の終わりに（サビ）→ タチアガレ（ラスト）
- テロップ:
  0:00〜0:05: 「全１０曲、全貌解禁」
  0:05〜0:12: 「先行配信「うっちゃりファンク」「夏の終わりに」も収録」
  0:12〜0:20: 「新曲山盛り！これが15年ぶりの全力」
  0:20〜0:28: 「1st Album「全ての武器をお箸に」」
  0:28〜0:30: 「8/19 リリース！」"""
}

# ===== 8/12〜8/18 カウントダウン投稿 =====
COUNTDOWN_POSTS = {
    7: f"""🎸 リリースまであと７日！

1st Album「{ALBUM_TITLE}」
8/19（水）リリース。

15年分の全部が詰まった、全１０曲。
全配信中の「うっちゃりファンク」「夏の終わりに」も収録。

予約はこちら👇
{SITE_URL}

#デブパレード #全ての武器をお箸に #あと７日""",

    5: f"""あと5日。

「{ALBUM_TITLE}」

タイトルに込めた想いは一つ——
「みんなで美味しくご飯を食べよう」

それだけ。
でもそれが、全てだと思ってる。

8/19リリース🍖
{SITE_URL}

#デブパレード #全ての武器をお箸に""",

    3: f"""あと3日。

NARUTOのED「バッチコイ!!!」から20年近く経った。

あの頃聴いてた人に届いてほしい。
今の俺たちの音楽を。

「{ALBUM_TITLE}」
8/19リリース。

{SITE_URL}

#デブパレード #バッチコイ #NARUTO""",

    2: f"""あと2日。

15年間、俺たちを忘れていた人へ。
15年間、ずっと待っていてくれた人へ。

どちらにも、届けたい音楽がある。

「{ALBUM_TITLE}」
8/19（水）リリース🍖

{LINKMAP_URL}

#デブパレード #全ての武器をお箸に""",

    1: f"""明日だ。

15年ぶりの、俺たちの答えを届ける日が。

「{ALBUM_TITLE}」
明日8/19、全配信サービスで解禁。

眠れなくなってきた。
デブには徹夜は辛いけど、興奮してる。🍖

{LINKMAP_URL}

#デブパレード #全ての武器をお箸に #明日リリース""",
}

# ===== 8/19 リリース当日 =====
RELEASE_DAY_POSTS = {
    "midnight": f"""今日だ。

「{ALBUM_TITLE}」

2026年8月19日、0時。
15年間の全部を、今日世界に解き放つ。

すべての争いを終わりにして、
お箸を持ってみんなで美味しくご飯を食べよう。

それが俺たちDevparadeのすべて。🍖

{LINKMAP_URL}

#デブパレード #全ての武器をお箸に #DEVPARADE""",

    "morning": f"""🎸 本日リリース！

1st Full Album「{ALBUM_TITLE}」/ Devparade

全10曲、今すぐ全配信サービスで聴けます！

Spotify / Apple Music / Amazon Music
YouTube Music / LINE MUSIC ...

{LINKMAP_URL}

再生してシェアしてくれたら最高に嬉しい🍖

#デブパレード #全ての武器をお箸に #配信開始""",

    "afternoon": f"""「{ALBUM_TITLE}」聴いてくれてますか？

どの曲が好きかリプで教えてください🍖

バッチコイ!!!派？
夏の終わりに派？
全ての武器をお箸に派？

全部聴いてくれてる人、最高に嬉しい。

{LINKMAP_URL}

#デブパレード #全ての武器をお箸に""",

    "night_naruto": f"""NARUTOのED「バッチコイ!!!」を覚えてる人へ。

あのバンドが、15年ぶりに帰ってきました。
今日、アルバムを出しました。

「{ALBUM_TITLE}」

バッチコイ!!!を好きだったなら、
今の俺たちの音楽もきっと刺さるはず。
ぜひ聴いてみて。🍖

{LINKMAP_URL}

#NARUTO #バッチコイ #デブパレード""",

    "thanks": f"""今日、アルバムを出した。

聴いてくれた人、シェアしてくれた人、
ずっと待ってくれていた人、
初めて知った人。

全員に、ありがとうを言いたい。

「{ALBUM_TITLE}」
ぜひ聴き続けてください。
俺たちは、続けます。🍖

#デブパレード #全ての武器をお箸に""",
}


def print_section(title, content):
    print(f"\n{'='*55}")
    print(f"📝 {title}")
    print("="*55)
    print(content)
    print(f"\n[{len(content)}文字]")


def show_august5():
    print("\n\n🗓️  8/5（水）アルバム全貌公開コンテンツ")
    print("="*55)
    print_section("X メイン（トラックリスト）", AUGUST_5_POSTS["x_main"])
    print_section("X コンセプト告知", AUGUST_5_POSTS["x_concept"])
    print_section("X NARUTO層向け", AUGUST_5_POSTS["x_naruto"])
    print_section("Instagram", AUGUST_5_POSTS["instagram"])
    print(f"\n{'='*55}")
    print("🎬 TikTok/Reels")
    print("="*55)
    print(AUGUST_5_POSTS["tiktok_script"])


def show_countdown(day):
    if day in COUNTDOWN_POSTS:
        print(f"\n\n🗓️  8/{20-day}（あと{day}日）カウントダウン投稿")
        print_section(f"X/Instagram（あと{day}日）", COUNTDOWN_POSTS[day])
    else:
        # 最も近いカウントダウンを表示
        available = sorted(COUNTDOWN_POSTS.keys())
        print(f"\n利用可能なカウントダウン日: {[f'あと{d}日' for d in available]}")


def show_release_day():
    print("\n\n🎸 8/19（水）リリース当日コンテンツ")
    print("="*55)
    for key, post in RELEASE_DAY_POSTS.items():
        labels = {
            "midnight": "🌙 00:00 0時解禁",
            "morning": "☀️ 07:00 朝の告知",
            "afternoon": "🍖 12:00 昼のエンゲージメント",
            "night_naruto": "🌙 20:00 NARUTO層向け",
            "thanks": "🌃 22:00 感謝投稿",
        }
        print_section(labels.get(key, key), post)


def main():
    args = sys.argv[1:]
    now = datetime.now(JST)

    print(f"\n🎸 Devparade アルバム告知コンテンツジェネレーター")
    print(f"   {now.strftime('%Y-%m-%d %H:%M JST')}")
    print(f"   アルバムリリース: {ALBUM_DATE}")
    album_date = datetime(2026, 8, 19, 0, 0, 0, tzinfo=JST)
    days_left = max(0, (album_date - now).days)
    print(f"   あと{days_left}日！")

    if "--all" in args:
        show_august5()
        for day in sorted(COUNTDOWN_POSTS.keys(), reverse=True):
            show_countdown(day)
        show_release_day()
        return

    if "--day" in args:
        idx = args.index("--day")
        day_str = args[idx+1] if idx+1 < len(args) else "5"
        day = int(day_str)
        if day == 5:
            show_august5()
        elif day == 19:
            show_release_day()
        else:
            # 残り日数に換算
            days_to_album = (datetime(2026, 8, 19, tzinfo=JST) - datetime(2026, 8, day, tzinfo=JST)).days
            show_countdown(days_to_album)
        return

    # デフォルト: 今日の日付に応じたコンテンツを表示
    today_day = now.day
    if now.month == 8:
        if today_day <= 5:
            show_august5()
        elif today_day <= 12:
            days_left_val = (datetime(2026, 8, 19, tzinfo=JST) - now).days
            show_countdown(days_left_val)
        elif today_day == 19:
            show_release_day()
        else:
            print(f"\n🎉 アルバムリリース後！引き続き拡散を！")
    else:
        show_august5()

    print(f"\n\n{'='*55}")
    print("📋 全コンテンツ: python3 scripts/album_content_generator.py --all")
    print("📋 特定日付:     python3 scripts/album_content_generator.py --day [5/12/19]")
    print("="*55)


if __name__ == "__main__":
    main()
