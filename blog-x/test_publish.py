#!/usr/bin/env python3
"""
テスト用スクリプト: 記事生成から画像生成までの一連の流れをテスト
"""

import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()


def main():
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    from src.content.generator import ContentGenerator
    from src.content.image_generator import ImageGenerator
    
    print("=" * 60)
    print("🎨 COYASS Auto-Posting System - 画像＆記事生成テスト")
    print("=" * 60)
    
    # Generate Text
    print("\n🔄 記事テキストを生成中...")
    text_generator = ContentGenerator(config)
    article = text_generator.generate_note_article(category="career")
    
    if not article:
        print("❌ 記事の生成に失敗しました。")
        return
        
    print(f"✅ 記事生成成功: {article['title']}")
    
    # Generate Image
    print("\n🖼️ 見出し画像を生成中...")
    image_generator = ImageGenerator()
    
    # Create an image prompt
    image_prompt = f"Professional dental care concept, high quality, 16:9 aspect ratio. Theme: {article['title']}. Minimalist and modern."
    
    image_path = image_generator.generate_cover_image(image_prompt, category="career")
    
    if image_path:
        print(f"✅ 画像生成成功: {image_path}")
        print("この画像をNoteの見出し画像として使用できます。")
    else:
        print("❌ 画像の生成に失敗しました。")

if __name__ == "__main__":
    main()
