import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.content.image_generator import ImageGenerator
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("🎨 Testing ImageGenerator...")
    gen = ImageGenerator()
    path = gen.generate_cover_image("最新のデンタルケア", "dental_tips")
    print(f"✅ Image generated at: {path}")
    if os.path.exists(path):
        print(f"📦 Size: {os.path.getsize(path)} bytes")
