#!/usr/bin/env python3
"""
クイックテスト: AI記事生成の動作確認
APIキーが設定されていればAI生成、なければサンプル出力
"""

import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

def main():
    # 設定読み込み
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("=" * 60)
    print("🦷🎤 COYASS Auto-Posting System - テスト生成")
    print("=" * 60)

    # AI APIキーの確認
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    has_openai = openai_key and openai_key != "sk-xxxxxxxxxxxxxxxxxxxx"
    has_gemini = gemini_key and gemini_key != "AIzaxxxxxxxxxxxxxxxxxxxxxxx"

    print(f"\n📡 API Status:")
    print(f"   OpenAI: {'✅ 設定済み' if has_openai else '❌ 未設定'}")
    print(f"   Gemini: {'✅ 設定済み' if has_gemini else '❌ 未設定'}")

    if not has_openai and not has_gemini:
        print("\n⚠️ APIキーが設定されていません。")
        print("   .env ファイルに OPENAI_API_KEY または GEMINI_API_KEY を設定してください。")
        print("\n📝 サンプル出力を表示します:\n")
        show_sample()
        return

    # AI生成テスト
    from src.content.generator import ContentGenerator
    from src.content.editor import ContentEditor
    from src.content.fact_checker import FactChecker

    generator = ContentGenerator(config)
    editor = ContentEditor()
    fact_checker = FactChecker()

    category = "dental_tips"
    print(f"\n🔄 Note記事を生成中... (カテゴリ: {category})")

    article = generator.generate_note_article(category=category)
    if article:
        print(f"\n{'='*60}")
        print(f"📝 タイトル: {article['title']}")
        print(f"📊 文字数: {article['word_count']}")
        print(f"🤖 AI: {article['ai_provider']} ({article['ai_model']})")
        print(f"🏷️ タグ: {article['hashtags']}")
        print(f"{'='*60}")
        print(f"\n{article['body'][:800]}")
        if article['word_count'] > 800:
            print(f"\n... (残り {article['word_count'] - 800} 文字)")

        # 品質チェック
        quality = editor.check_quality(article["body"], platform="note")
        print(f"\n📊 品質スコア: {quality['score']}/100")
        for issue in quality["issues"]:
            print(f"   {issue}")

        # ファクトチェック
        passed, issues = fact_checker.check_content(article["body"])
        if issues:
            print(f"\n🔍 ファクトチェック:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print(f"\n✅ ファクトチェック: 問題なし")
    else:
        print("❌ 生成に失敗しました。")


def show_sample():
    """サンプル出力"""
    print("=" * 60)
    print("📝 タイトル: 歯磨きの常識、実は間違ってるかもしれない話")
    print("📊 文字数: 2,847")
    print("🤖 AI: (サンプル)")
    print("��️ タグ: #COYASS #中目黒コヤス歯科 #予防歯科 #美容歯科")
    print("=" * 60)
    print("""
よう、COYASSだ。

今日は俺が日々の診療で「マジでこれ知らない人多いな...」って
思ってることを話す。

歯磨き、毎日してるよな？
当たり前だ。でもな、その「当たり前」のやり方が
実は歯を痛めてる可能性があるって知ってたか？

## 食後すぐ磨くのは実はNG

これ、マジで衝撃受ける人多いんだけど——
食後すぐの歯磨きは、場合によっては逆効果なんだ。

なぜかって言うと、食事の直後は口の中が酸性に傾いてる。
この状態でゴシゴシ磨くと、エナメル質が削れやすくなる。

俺がおすすめしてるのは、食後30分待ってから磨くこと。
その間に唾液が中和してくれるから、安全に磨ける。

... (残り 2,200 文字)

📊 品質スコア: 85/100
✅ ファクトチェック: 問題なし
""")


if __name__ == "__main__":
    main()
