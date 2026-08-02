#!/usr/bin/env python3
"""
カウントダウン & リリース告知 ツイート生成
==========================================

毎日昼 12:00 に投稿するカウントダウンツイートを生成。
3段階のフェーズ:
  Phase 1: 7/12 ライブ前 → ライブカウントダウン
  Phase 2: 7/12 以降〜7/29 → 先行シングル「夏の終わりに」カウントダウン
  Phase 3: 7/29 以降〜8/19 → 1stアルバムカウントダウン

"""

import os
import random
from datetime import datetime, timezone, timedelta

# ===== ターゲット日付 =====
LIVE_DATE = datetime(2026, 7, 12, 12, 0, 0, tzinfo=timezone(timedelta(hours=9)))
SINGLE_DATE = datetime(2026, 7, 29, 0, 0, 0, tzinfo=timezone(timedelta(hours=9)))
ALBUM_DATE = datetime(2026, 8, 19, 0, 0, 0, tzinfo=timezone(timedelta(hours=9)))

SITE_URL = "https://devparade.jp/"
TICKET_URL = "https://clubque.net/schedule/15101/"
LINKMAP_URL = "https://link-map.jp/links/t7J6lCsV"  # 夏の終わりに & アルバム共通配信リンク
ALBUM_LINKMAP_URL = "https://link-map.jp/links/t7J6lCsV"

def get_days_until(target_date):
    """目標日までの残り日数を計算（0以上）"""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    delta = target_date - now
    return max(0, delta.days)


def is_past(target_date):
    """目標日が過去かどうか判定"""
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    return now >= target_date


def generate_live_countdown(days_left):
    """7/12 ライブカウントダウン用ツイート"""
    
    if days_left == 0:
        return random.choice([
            f"""🔥🔥🔥 今日だ。

下北沢 CLUB Que。
Electric Eel Shock vs Devparade。

全員90kg超のリングに、今日上がる。

来い。
{TICKET_URL}

#デブパレード #DEVPARADE #下北沢 #ライブ""",

            f"""本日。CLUB Que。

15年分の脂肪と魂、全部ぶつける。
EES vs Devparade、開戦。

会場で待ってる🍖

{TICKET_URL}
#Devparade #ElectricEelShock""",
        ])
    
    if days_left <= 3:
        return random.choice([
            f"""あと{days_left}日。

7/12 下北沢 CLUB Que
Electric Eel Shock vs Devparade

15年ぶりに動き出した90kg超の5人。
その重みを、生で浴びに来い🔥

{TICKET_URL}
#Devparade #CLUBQUE""",

            f"""NEXT LIVE まであと {days_left} 日。

下北沢の夜に、
NARUTOのEDバンドが殴り込む。

見届けろ🍖

👇チケット
{TICKET_URL}
#デブパレード #バッチコイ""",
        ])
    
    if days_left <= 7:
        return random.choice([
            f"""【あと{days_left}日】

7/12(日) 下北沢 CLUB Que
⚡ Electric Eel Shock vs Devparade ⚡

全員90kg超 vs 全員ハイボルテージ。
この対バン、見逃したら一生後悔する。

{TICKET_URL}
#DEVPARADE #ライブ""",

            f"""7/12 CLUB Que まで残り{days_left}日。

メンバー全員90kg超が
下北沢で暴れまわる夜。

初めてでも大丈夫。
ドアを開けたらそこは天国（の焼肉屋）🍖

{TICKET_URL}
#デブパレード #バッチコイ""",

            f"""🍖 カウントダウン: {days_left} DAYS 🍖

7/12 @ 下北沢 CLUB Que
RETURN TO INDEPENDENT

「NARUTOのバッチコイ!!!のバンド」が
15年ぶりにライブハウスで暴れてるの
もう見た？

見てないなら、7/12がラストチャンスかも。

{TICKET_URL}
#Devparade #NARUTO""",
        ])
    
    if days_left <= 14:
        return random.choice([
            f"""7/12 CLUB Que まであと{days_left}日💥

Electric Eel Shock vs Devparade
下北沢で激突する2マン。

全員90kg超 × 痛風持ち。
それでもステージに立つ理由がある。

ライブで答えを見せる🍖

{TICKET_URL}
#DEVPARADE #デブパレード""",

            f"""📢 あと{days_left}日

7/12 下北沢 CLUB Que
「RETURN TO INDEPENDENT」

NARUTOのEDテーマ「バッチコイ!!!」
やった全員90kg超バンド、
15年ぶりの復活ライブが止まらない。

次は下北沢。
{TICKET_URL}
#バッチコイ #Devparade""",
        ])
    
    # 15日以上前
    return random.choice([
        f"""7.12 下北沢 CLUB Que
⚡ EES vs DEVPARADE ⚡

NARUTOのED「バッチコイ!!!」バンド。
メンバー全員90kg超。全員痛風。
15年ぶりの復活。

嘘みたいだろ？全部本当なんだぜ。

→ {TICKET_URL}
#DEVPARADE #バッチコイ #NARUTO""",

        f"""【LIVE告知🍖】

7/12(日) 下北沢 CLUB Que
Electric Eel Shock vs Devparade

1stアルバム「全ての武器をお箸に」
8/19リリースに向けた重要ライブ。

来たことない人ほど来てほしい。
度肝を抜くから。

{TICKET_URL}
#デブパレード""",

        f"""NARUTOのED「バッチコイ!!!」
覚えてる人、いる？

あのバンド、15年ぶりに復活して
ライブハウスで暴れてるよ。

全員90kg超。全員痛風。
でも音は誰よりもデカい。

7/12 下北沢 CLUB Que 🍖
{TICKET_URL}

#NARUTO #バッチコイ #Devparade""",
    ])


def generate_single_countdown(days_left):
    """7/29 先行シングル「夏の終わりに」カウントダウン用ツイート"""

    if days_left == 0:
        return random.choice([
            f"""🎵 本日配信スタート！

「夏の終わりに」/ Devparade

15年の沈黙を破る、デブたちの切ないラブソング。

Spotify / Apple Music / YouTube Music
今すぐ聴いてくれ🍖

{LINKMAP_URL}
#デブパレード #夏の終わりに #配信開始""",

            f"""今日、出す。

「夏の終わりに」

あの頃の夏の切なさ、全部詰め込んだ。
NARUTOのあのバンドが送る、
15年ぶりの新曲。

聴いてくれ👇
{LINKMAP_URL}

#デブパレード #夏の終わりに""",
        ])

    if days_left <= 3:
        return random.choice([
            f"""あと{days_left}日。

「夏の終わりに」/ Devparade
7/29 配信スタート。

デブの哀愁とメロディの組み合わせ、
これが最強だと思ってる。

{LINKMAP_URL}
#デブパレード #夏の終わりに""",

            f"""先行シングルまであと{days_left}日🍖

「夏の終わりに」
7/29 Spotify / Apple Music etc.で配信開始！

15年ぶりに鳴らす、
デブたちのラブソング。

{LINKMAP_URL}
#デブパレード #夏の終わりに #新曲""",
        ])

    if days_left <= 7:
        return random.choice([
            f"""【あと{days_left}日】

先行シングル「夏の終わりに」
7/29 配信スタート。

夏の終わりの切なさを
デブパレードのサウンドで届ける。

{LINKMAP_URL}
#デブパレード #夏の終わりに""",

            f"""7/29まであと{days_left}日。

NARUTOのED「バッチコイ!!!」バンドが
15年ぶりに新曲を出す。

「夏の終わりに」
— デブの切なさが詰まった一曲。

👇もうすぐ配信
{LINKMAP_URL}
#Devparade #NARUTO #夏の終わりに""",
        ])

    # 8日以上前
    return random.choice([
        f"""先行シングル配信まであと{days_left}日。

「夏の終わりに」/ Devparade
2026.07.29

15年ぶりに鳴り響く、
デブたちの切ないメロディ。

COMING SOON🍖
{LINKMAP_URL}
#デブパレード #夏の終わりに""",

        f"""📢 先行シングル告知

7/29 配信リリース
「夏の終わりに」/ Devparade

NARUTOのED「バッチコイ!!!」を歌っていた
全員90kg超のバンドが、
15年ぶりに届ける新曲。

{LINKMAP_URL}
#デブパレード #NARUTO #バッチコイ""",
    ])


def generate_album_countdown(days_left):
    """8/19 アルバムカウントダウン用ツイート"""

    if days_left <= 7:
        return random.choice([
            f"""1st Album「全ての武器をお箸に」
リリースまであと{days_left}日。

15年分の想いを全曲に詰めた。
90kg超の5人が作った、
どこにもない音楽。

{ALBUM_LINKMAP_URL}
#デブパレード #全ての武器をお箸に""",
        ])

    return random.choice([
        f"""2026.08.19
1st Full Album
「全ての武器をお箸に」

あと{days_left}日。

武器はいらない。お箸があれば、
俺たちは何でもできる。

COMING SOON🍖

#Devparade #全ての武器をお箸に""",

        f"""8/19 1st Album リリース決定🎉

「全ての武器をお箸に」

メンバー全員90kg超の
ヘヴィメタボバンド Devparade。
15年ぶり、初のフルアルバム。

先行シングル「夏の終わりに」はこちら👇
{ALBUM_LINKMAP_URL}

#デブパレード #DEVPARADE""",
    ])


def generate_band_story():
    """夜の投稿用: バンドストーリー / NARUTO / エンゲージメント系"""
    
    stories = [
        # NARUTO関連
        f"""NARUTOのエンディングに俺たちの曲が流れた時、
海外からDMが殺到した。

「あなたたちが90kg超全員？マジで？」

マジだよ。全員マジのデブだよ。
それでもソニーからメジャーデビューしたんだよ。

あの頃の全力を、今また出す。🍖

#NARUTO #バッチコイ #Devparade""",

        f"""HEY!HEY!HEY!で松ちゃんに
「お前ら全員デカいな！」って言われて
会場爆笑だったの覚えてる。

あの頃は恥ずかしかった。
今は誇りに思ってる。

90kg超は、俺たちのアイデンティティ。🍖

{SITE_URL}
#デブパレード #HEY3""",

        f"""2008年、SUMMER SONICのステージに立った。
メンバー全員90kg超で。

照明が当たった時、
自分たちの影がバカみたいにデカくて
笑ってしまった。

デカくて何が悪い。
影もデカいってことは、存在もデカいってこと。🍖

#Devparade #SUMMERSONIC""",

        # 復活ストーリー
        f"""2011年。メンバーがダイエットに成功して解散。

バンド史上、最も意味不明な解散理由。

2026年。全員リバウンドして復活。

バンド史上、最も美しい復活劇。

8/19 1st Album「全ての武器をお箸に」
リリース決定🍖

#デブパレード #DEVPARADE""",

        # メンバー紹介系
        f"""うちのメンバー紹介:

🎙️ COYASS（Vo.）— 歯科医師 × ラッパー。93kg。
🎤 ハンサム判治（Vo.）— 100kg超のハンサム。
🎸 ugazin（Gt.）— 135kg。バンド最重量。
🎸 ぺー（Ba.）— 120kgの低音番長。
🥁 TAH（Dr.）— 120kgのグルーヴマスター。

合計体重は企業秘密🍖

#Devparade #デブパレード""",

        # エンゲージメント系
        f"""質問：
NARUTOのED曲で一番好きなの何？

俺はもちろんバッチコイ!!!
（自分で言うな）

リプで教えて🍖

#NARUTO #バッチコイ #Devparade""",

        f"""2026年の復活から4ヶ月。

曲を出した。ライブをやった。
Botまで作った。

でもまだ全然足りない。
もっと多くの人に届けたい。

初めてDevparadeを知った人、
まずはSpotifyで「バッチコイ」聴いてくれ。
あとは任せろ🍖

{LINKMAP_URL}
#デブパレード""",
    ]
    
    return random.choice(stories)


def main():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)

    live_days = get_days_until(LIVE_DATE)
    single_days = get_days_until(SINGLE_DATE)
    album_days = get_days_until(ALBUM_DATE)

    print("=" * 50)
    print(f"🍖 Devparade カウントダウン ツイート生成")
    print(f"   {now.strftime('%Y-%m-%d %H:%M JST')}")
    print(f"   7/12 LIVE まで: {live_days}日")
    print(f"   7/29 SINGLE まで: {single_days}日")
    print(f"   8/19 ALBUM まで: {album_days}日")
    print("=" * 50)

    # ===== フェーズ判定 =====
    # Phase 1: ライブ前 → ライブカウントダウン
    # Phase 2: ライブ後〜シングル配信前 → シングルカウントダウン
    # Phase 3: シングル配信後〜アルバム発売 → アルバムカウントダウン
    if not is_past(LIVE_DATE):
        tweet = generate_live_countdown(live_days)
        category = "live_countdown"
    elif not is_past(SINGLE_DATE):
        tweet = generate_single_countdown(single_days)
        category = "single_countdown"
    else:
        tweet = generate_album_countdown(album_days)
        category = "album_countdown"

    print(f"\n📢 [{category}] ツイート:")
    print("-" * 40)
    print(tweet)
    print("-" * 40)
    print(f"文字数: {len(tweet)}")

    # 夜20:30枠: バンドストーリー
    story = generate_band_story()
    print(f"\n🌙 [band_story] ツイート:")
    print("-" * 40)
    print(story)
    print("-" * 40)
    print(f"文字数: {len(story)}")

    return tweet, story


if __name__ == "__main__":
    main()
