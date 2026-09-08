#!/usr/bin/env python3
"""
🎬 新曲『9月4日』動画付きプロモーションツイート自動投稿スクリプト
============================================================
生成された縦型プロモ動画（single0904_promo.mp4）をXに直接添付し、
インプレッションと視聴維持率を最大化する動画付きポストを送信します。
"""

import os
import sys
import argparse
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_PATH = _BASE_DIR / "video-automation" / "output" / "single0904_promo.mp4"

STREAMING_URL = "https://link-map.jp/links/wKq8wQ9H"

PROMO_TEXTS = [
    f"""【🔥 MVショート公開】
ハンサム判治 feat. デブパレード
新曲『9月4日』大好評配信中！🍖

全員90kg以上の男たちが放つ、
魂のヘヴィメタボ・アンセム！

今すぐ各配信サイトで爆音試聴せよ👇
{STREAMING_URL}

#デブパレード #ハンサム判治 #9月4日 #新曲 #MV""",

    f"""【🎬 爆音リピート推奨】
『9月4日』/ ハンサム判治 feat. デブパレード

「重い音楽は、重い奴が鳴らす。」
15年の沈黙を破り、伝説のバンドが再び動き出す。

Spotify / Apple Music / LINE MUSIC等で配信中👇
{STREAMING_URL}

#デブパレード #DEVPARADE #9月4日 #邦ロック""",

    f"""【🍖 デブたちの本気のラブソング】
『9月4日』配信スタート！

体重90kg超の男たちが絞り出す愛の叫び。
誰よりも深くて重いメロディを聴いてくれ。

ストリーミングはこちらから👇
{STREAMING_URL}

#デブパレード #ハンサム判治 #9月4日 #ポジデブ"""
]


def main():
    parser = argparse.ArgumentParser(description="新曲動画プロモツイート投稿")
    parser.add_argument("--pattern", type=int, default=0, choices=[0, 1, 2], help="投稿文パターン (0, 1, 2)")
    parser.add_argument("--dry-run", action="store_true", help="DRY RUNテスト")
    args = parser.parse_args()

    try:
        from x_client import post_tweet
    except ImportError:
        try:
            from scripts.x_client import post_tweet
        except ImportError:
            print("❌ x_client が見つかりません")
            return

    video_file = str(VIDEO_PATH) if VIDEO_PATH.exists() else None
    if not video_file:
        print(f"⚠️ 動画ファイルが見つかりません ({VIDEO_PATH})。テキストのみで投稿します。")

    tweet_text = PROMO_TEXTS[args.pattern]
    print("=" * 60)
    print("🎬 『9月4日』動画付きプロモツイート送信開始")
    print(f"   動画: {video_file or 'なし'}")
    print("=" * 60)
    print(tweet_text)
    print("-" * 60)

    if args.dry_run:
        print("🔍 [DRY RUN] 投稿をスキップしました")
        return "dry_run"

    tweet_id = post_tweet(tweet_text, media_path=video_file)
    if tweet_id and tweet_id != "dry_run":
        print(f"🎉 投稿完了! URL: https://x.com/dev_parade/status/{tweet_id}")
        return tweet_id
    else:
        print("❌ 投稿に失敗しました")
        return None


if __name__ == "__main__":
    main()
