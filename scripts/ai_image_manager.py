#!/usr/bin/env python3
"""
🎨 デブパレード AI画像マネージャー & 自動添付エンジン
===================================================
1. 事前生成された面白いAI画像ストック (data/ai_images/) から
   ツイート内容（ラーメン、焼肉、ロック、宇宙など）に最適な画像を自動選択。
2. OpenAI DALL-E 3 を使った新しい面白いAI画像の自動生成＆ストック拡充。
"""

import os
import sys
import time
import random
import requests
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
AI_IMAGE_DIR = _BASE_DIR / "data" / "ai_images"

# テーマ別画像マッチングキーワード
THEME_MAPPINGS = {
    "galaxy_ramen_warrior.jpg": ["ラーメン", "麺", "宇宙", "夜食", "スープ", "銀河", "深夜"],
    "rice_mountain_rocker.jpg": ["白米", "米", "焼肉", "肉", "大盛り", "特盛", "丼", "富士山", "ステーキ"],
    "meat_guitar_rocker.jpg": ["ロック", "ギター", "ライブ", "ステージ", "バンド", "シャウト", "骨付き肉", "90kg", "メジャー"]
}

# DALL-E 3 新規生成用のおもしろプロンプト集
AI_IMAGE_PROMPTS = [
    "A funny, high-energy comic illustration of a giant 95kg rockstar using huge barbecue tongs to flip giant sizzling burgers on a flaming amplifier. Rock concert BBQ, smoke, fire, energetic manga style, detailed.",
    "A humorous retro-manga illustration of heavyweight sumo-style rock musicians having a gigantic pizza party inside a space station orbiting Earth. Zero gravity floating pizza slices, rock instruments, colorful.",
    "An epic and hilarious Japanese manga poster of an overweight rock band eating bowls of ramen together after a concert, with golden radiant light shining upon them, anime style, emotional and funny.",
    "A funny illustration of an ultra-charismatic heavyweight rock bassist standing in front of a giant towering stack of golden fried chicken, vintage anime aesthetic, comical and triumphant."
]


def get_random_ai_image(tweet_text=""):
    """
    ツイート内容に最も適したAI画像をストックから取得。
    マッチしない場合はランダムに1枚選択。
    """
    if not AI_IMAGE_DIR.exists():
        return None

    existing_images = list(AI_IMAGE_DIR.glob("*.jpg")) + list(AI_IMAGE_DIR.glob("*.png"))
    if not existing_images:
        return None

    # キーワードマッチング
    if tweet_text:
        text_lower = tweet_text.lower()
        for filename, keywords in THEME_MAPPINGS.items():
            img_path = AI_IMAGE_DIR / filename
            if img_path.exists():
                for kw in keywords:
                    if kw in text_lower:
                        return str(img_path)

    # マッチしない場合はランダム
    selected = random.choice(existing_images)
    return str(selected)


def generate_dalle_image(prompt=None):
    """
    OpenAI DALL-E 3 を呼び出して新しい面白い画像を生成し、ストックに追加する
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-xxxx"):
        print("⚠️ OPENAI_API_KEY が未設定のため、DALL-E 生成をスキップします")
        return None

    AI_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    selected_prompt = prompt or random.choice(AI_IMAGE_PROMPTS)
    print(f"🎨 DALL-E 3 で新しいAI画像を生成中...")
    print(f"   プロンプト: {selected_prompt[:60]}...")

    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "dall-e-3",
        "prompt": selected_prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard"
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        if res.status_code == 200:
            data = res.json()
            image_url = data["data"][0]["url"]
            img_res = requests.get(image_url, timeout=30)
            if img_res.status_code == 200:
                filename = f"dalle_debu_{int(time.time())}.jpg"
                filepath = AI_IMAGE_DIR / filename
                with open(filepath, "wb") as f:
                    f.write(img_res.content)
                print(f"✅ 新しいAI画像を保存しました: {filepath}")
                return str(filepath)
        else:
            print(f"⚠️ DALL-E 3 エラー: {res.status_code} {res.text[:200]}")
    except Exception as e:
        print(f"❌ DALL-E 3 生成失敗: {e}")

    return None


if __name__ == "__main__":
    img = get_random_ai_image("焼肉食べたい！")
    print(f"マッチ画像: {img}")
