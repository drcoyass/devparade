#!/usr/bin/env python3
"""
🎵 ハンサム判治 feat. デブパレード「9月4日」リリース告知・自動ポストスクリプト
===================================================================
使い方:
    python3 scripts/release_0904_poster.py --dry-run      # 投稿内容をプレビュー（投稿しない）
    python3 scripts/release_0904_poster.py                # Xに即座にメイン告知を投稿
    python3 scripts/release_0904_poster.py --slot story   # エピソード深掘りスレッドを投稿
    python3 scripts/release_0904_poster.py --all          # 全パターンの文面を表示
"""

import os
import sys
import argparse
from pathlib import Path

# scripts/x_client をインポートできるように設定
_BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BASE_DIR / "scripts"))

try:
    from x_client import post_tweet
except ImportError:
    post_tweet = None

LINKMAP_URL = "https://link-map.jp/links/VTzWyFH6"

POSTS = {
    "main": {
        "title": "【メイン告知】9月4日 リリース",
        "text": f"""【魂の新曲、解禁】
ハンサム判治 feat. デブパレード
「9月4日」配信リリース！

15年前、ugazinと作った宮ちゃんへの追悼の歌。
ワシ史上最高の唄がうたえた。
ぜひ聴いてください。

🎧配信ストア👇
{LINKMAP_URL}

#デブパレード #ハンサム判治 #9月4日"""
    },
    "story": {
        "title": "【エピソード深掘り】9月4日という日",
        "text": f"""【9月4日という日】
「判治、お前がメジャーでやってるだけで最高だと思うぜ！」
そう言ってくれた親友・宮ちゃんが旅立った日。

15年ぶりの復活。
この忘れ物を取りに来た。

あの日見た夢は今も終わっとらんだら？

🎧配信中👇
{LINKMAP_URL}

#デブパレード #9月4日"""
    },
    "replay": {
        "title": "【リマインド・夜告知】",
        "text": f"""デブパレードが15年ぶりに復活した理由。
この忘れ物を取りに来たかった。

ハンサム判治 feat. デブパレード
「9月4日」

泣いて歌えんかったレコーディング。
でも最高の唄になった。
静かな夜に聴いてほしい。

🎧配信中👇
{LINKMAP_URL}

#デブパレード #9月4日"""
    }
}


def main():
    parser = argparse.ArgumentParser(description="「9月4日」リリース告知ポスト")
    parser.add_argument("--slot", choices=["main", "story", "replay"], default="main", help="投稿スロット")
    parser.add_argument("--all", action="store_true", help="全スロットの文面を表示")
    parser.add_argument("--dry-run", action="store_true", help="実際の投稿を行わず文面を確認")
    args = parser.parse_args()

    if args.all:
        print("=" * 60)
        print("🎵 「9月4日」リリース告知 全スロット一覧")
        print("=" * 60)
        for key, post in POSTS.items():
            print(f"\n--- [{key}] {post['title']} ---")
            print(post["text"])
            print(f"文字数: {len(post['text'])}文字")
        return

    selected = POSTS.get(args.slot)
    if not selected:
        print(f"❌ 不明なスロット: {args.slot}")
        return

    text = selected["text"]
    print(f"📋 選択された投稿: {selected['title']}")
    print("-" * 50)
    print(text)
    print("-" * 50)
    print(f"文字数: {len(text)}文字")

    if args.dry_run:
        print("\n🔍 DRY RUN モード: 投稿は行われませんでした。")
        return

    if post_tweet is None:
        print("⚠️ x_client.py が見つからないため投稿できませんでした。")
        return

    print("\n🚀 Xへの自動投稿を開始します...")
    result = post_tweet(text)
    if result:
        print(f"✅ 投稿成功！ Tweet ID: {result}")
    else:
        print("❌ 投稿に失敗しました。x_clientのログを確認してください。")


if __name__ == "__main__":
    main()
