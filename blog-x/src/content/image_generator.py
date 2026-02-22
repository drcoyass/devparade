"""
COYASS Auto-Posting System - Image Generator
記事のテーマに合わせた画像（見出し画像・挿絵）を自動生成するモジュール
"""

import os
import time
import urllib.parse
import urllib.request
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageGenerator:
    """AIを使った画像生成システム"""
    
    def __init__(self, config: dict = None):
        if config is None:
            config = {}
        self.image_dir = Path("data/images")
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def generate_image_prompt(self, article_title: str, category: str) -> str:
        """記事タイトルとカテゴリから英語の画像生成プロンプトを作成"""
        # Noteの見出し画像に使えるような、おしゃれでキャッチーなプロンプトのベース
        base_prompt = "A high-quality, cinematic, stylish flat illustration or photography suitable for a blog header image. "
        
        if category == "dental_tips":
            concept = f"Modern dentistry, beautiful white teeth, clean clinic, futuristic. Concept: {article_title}"
        elif category == "music_review":
            concept = f"Hip-hop music, microphone, DJ turntable, neon lights, cool vibe. Concept: {article_title}"
        elif category == "food_health":
            concept = f"Healthy and delicious food, orthomolecular medicine, vibrant colors, fresh ingredients. Concept: {article_title}"
        elif category == "career":
            concept = f"Success, dual career, dentist and musician, motivation, professional atmosphere. Concept: {article_title}"
        elif category == "parenting":
            concept = f"Warm family moment, children playing, heartwarming, soft lighting. Concept: {article_title}"
        elif category == "industry":
            concept = f"Medical technology, future of dentistry, professional networking, abstract tech background. Concept: {article_title}"
        else:
            concept = f"Abstract stylish background, creative vibe, lifestyle. Concept: {article_title}"
            
        return base_prompt + concept

    def generate_cover_image(self, article_title: str, category: str, output_filename: str = None) -> str:
        """
        見出し画像を生成して保存し、そのパスを返す。
        OpenAI APIキーがあればDALL-E 3を使い、なければ無料のPollinations AIを使用する。
        """
        prompt = self.generate_image_prompt(article_title, category)
        
        if not output_filename:
            timestamp = int(time.time())
            output_filename = f"cover_{category}_{timestamp}.jpg"
            
        output_path = self.image_dir / output_filename
        
        # 1. DALL-E 3 を試行 (APIキーがある場合)
        if self.openai_api_key and self.openai_api_key != "sk-xxxxxxxxxxxxxxxxxxxx":
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                
                logger.info(f"🎨 Generating image with DALL-E 3 for: {article_title}")
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",  # DALL-E 3は16:9(1024x1792等)も可能だが基本サイズで生成
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                
                # 画像をダウンロードして保存
                urllib.request.urlretrieve(image_url, str(output_path))
                logger.info(f"✅ Image downloaded successfully: {output_path}")
                return str(output_path)
                
            except Exception as e:
                logger.warning(f"⚠️ DALL-E 3 generation failed: {e}. Falling back to free API...")

        # 2. 無料のプロンプトベース画像生成API (Pollinations AI) へフォールバック
        # Noteの見出し推奨サイズ(1280x670)に合わせて生成
        try:
            logger.info(f"🎨 Generating image with Free API for: {article_title}")
            encoded_prompt = urllib.parse.quote(prompt)
            # seedをランダムにして毎回違う画像を生成
            seed = int(time.time())
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=670&nologo=true&seed={seed}"
            
            # APIの呼び出し（UA設定）
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                with open(output_path, 'wb') as f:
                    f.write(response.read())
                    
            logger.info(f"✅ Image generated and saved successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Free API image generation failed: {e}")
            return ""
