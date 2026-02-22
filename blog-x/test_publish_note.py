#!/usr/bin/env python3
"""
テスト用スクリプト: 記事生成、画像生成、そして実際にNoteへ下書き保存するまでの一連の流れをテスト
"""

import os
import sys
import yaml
import asyncio
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

async def main():
    try:
        from src.publishers.note_publisher import NotePublisher
        from src.content.generator import ContentGenerator
        from src.content.image_generator import ImageGenerator
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("必要なライブラリがインストールされているか確認してください。")
        return

    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("=" * 60)
    print("🚀 COYASS Auto-Posting System - Note本番投稿（下書き）テスト")
    print("=" * 60)

    # 1. 認証状態の確認 (Googleログイン等のセッションが data/note_state.json にあれば不要)
    state_file = Path("data/note_state.json")
    if not state_file.exists():
        email = os.getenv("NOTE_EMAIL")
        password = os.getenv("NOTE_PASSWORD")
        if not email or not password:
            print("⚠️ 警告: ログイン情報がありません。")
            print("Googleログインを使用するには、先に `python3 setup_note_login.py` を実行してください。")
            return
    else:
        print("✅ 保存されたログインセッション (data/note_state.json) を使用します。")

    # 2. 記事テキストを生成
    print("\n[1/3] 🔄 記事テキストを生成中...")
    text_generator = ContentGenerator(config)
    article = text_generator.generate_note_article(category="career")
    
    if not article:
        print("❌ 記事の生成に失敗しました。")
        return
    print(f"✅ 記事生成成功: {article['title']}")
    
    # 3. 見出し画像を生成
    print("\n[2/3] 🖼️ 見出し画像を生成中...")
    image_generator = ImageGenerator()
    image_prompt = f"Professional dental care concept, high quality, 16:9 aspect ratio. Theme: {article['title']}. Minimalist and modern."
    image_path = image_generator.generate_cover_image(image_prompt, category="career")
    
    if image_path:
        print(f"✅ 画像生成成功: {image_path}")
    else:
        print("⚠️ 画像の生成に失敗しました（画像なしで投稿に進みます）。")

    # 4. Noteに下書き投稿
    print("\n[3/3] 📝 Noteへ下書き投稿を開始...")
    publisher = NotePublisher()
    
    try:
        # 下書きモード（強制的に下書きとして保存）
        success = await publisher.publish(
            title=article["title"],
            body=article["body"],
            tags=article.get("hashtags", []),
            image_path=image_path,
            mode="draft"  # 安全のため強制的にdraft
        )
        
        if success:
            print("\n🎉 成功！Noteの下書きに保存されました！")
            print("実際のブラウザでNoteの下書き一覧（ https://note.com/notes ）を確認してください。")
        else:
            print("\n❌ Noteへの下書き投稿に失敗しました。")
    except Exception as e:
        print(f"\n❌ Noteへの下書き投稿中にエラーが発生しました: {e}")

if __name__ == "__main__":
    asyncio.run(main())
