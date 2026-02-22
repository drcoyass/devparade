import os
import sys

from dotenv import load_dotenv
load_dotenv()

from src.content.generator import ContentGenerator
import logging

logging.basicConfig(level=logging.INFO)

config = {
    "ai": {
        "primary_provider": "openai",
        "fallback_provider": "gemini",
        "openai": {
            "model": "gpt-4o",
            "temperature": 0.8,
            "max_tokens": 4000
        }
    },
    "persona": {},
    "note": {}
}

print("🤖 Testing OpenAI integration...")
gen = ContentGenerator(config)

article = gen.generate_note_article(category="dental_tips", topic="電動歯ブラシの選び方")

if article:
    print(f"✅ Success! Generated with {article['ai_provider']} ({article['ai_model']})")
    print("-" * 40)
    print(article['title'])
    print("-" * 40)
    print(article['body'][:300] + "...")
else:
    print("❌ Failed to generate article.")

