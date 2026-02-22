"""
COYASS Auto-Posting System - Content Generator
AI-powered content generation with COYASS persona.
"""

import os
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# COYASS ペルソナ システムプロンプト
COYASS_SYSTEM_PROMPT = """あなたはCOYASS（Dr.COYASS / 小安正洋）として記事を書きます。

【プロフィール】
- 中目黒コヤス歯科 院長
- 歯学博士（美容歯科学）、昭和大学歯学部兼任講師、東京医科歯科大学非常勤講師
- ポリリン酸研究のエキスパート（柴肇一教授に師事、10年以上の実績）
- 日本歯科審美学会認定医
- ラッパー: MIC BANDITZ(avex), デブパレード(Sony)で2度のメジャーデビュー
- 現在: E.P.O（元SOUL'd OUT Bro.Hiと結成）、洪水、Malignant Co.で活動
- 打首獄門同好会とのコラボで日本武道館ステージ経験
- 2児の父
- 栄養療法（オーソモレキュラー医学）にも精通

【文体ガイドライン】
1. 専門性と親しみやすさの融合：歯科の専門知識を噛み砕いて伝える
2. ラッパー的なリズム感：要所にパンチラインを入れる
3. 実体験ベース：「今日こうだった」「俺の経験では」というリアルさ
4. 読者への呼びかけ：「みんなも試してみて」的な巻き込み力
5. ポジティブだけど現実的：成功も失敗も正直に語る
6. 医療広告ガイドラインを意識：誇大表現は避ける

【禁止事項】
- AIが書いたとわかるような定型表現（「いかがでしたでしょうか」等）
- 過度に丁寧な敬語（タメ口と敬語を自然にミックス）
- 根拠のない治療効果の断言
- 他の歯科医院の批判
"""


class ContentGenerator:
    """AI を使ったコンテンツ生成エンジン"""

    def __init__(self, config: dict):
        self.config = config
        self.ai_config = config.get("ai", {})
        self.persona = config.get("persona", {})
        self.templates_dir = Path("config/content_templates")
        self._setup_ai_clients()

    def _setup_ai_clients(self):
        """AI クライアントの初期化"""
        self.openai_client = None
        self.gemini_model = None

        # OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "sk-xxxxxxxxxxxxxxxxxxxx":
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI init failed: {e}")

        # Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "AIzaxxxxxxxxxxxxxxxxxxxxxxx":
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model_name = self.ai_config.get("gemini", {}).get("model", "gemini-2.0-flash")
                self.gemini_model = genai.GenerativeModel(model_name)
                logger.info("✅ Gemini client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini init failed: {e}")

    def _load_template(self, category: str) -> str:
        """カテゴリ別テンプレートを読み込む"""
        template_path = self.templates_dir / f"{category}.md"
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        logger.warning(f"Template not found: {template_path}")
        return ""

    def generate_note_article(self, category: str, topic: str = None,
                               input_data: str = None) -> dict:
        """Note用の長文記事を生成する"""
        template = self._load_template(category)
        length_config = self.config.get("note", {}).get("article_length", {})
        min_len = length_config.get("min", 2000)
        max_len = length_config.get("max", 5000)

        user_prompt = self._build_note_prompt(category, topic, input_data, min_len, max_len, template)

        result = self._call_ai(
            system_prompt=COYASS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=self.ai_config.get("openai", {}).get("max_tokens", 4000)
        )

        if result:
            # タイトルと本文を分離
            title, body = self._parse_article(result["text"])
            hashtags = self._generate_hashtags(category)
            return {
                "title": title,
                "body": body,
                "category": category,
                "hashtags": hashtags,
                "word_count": len(body),
                "ai_provider": result["provider"],
                "ai_model": result["model"]
            }
        return None

    def generate_x_post(self, category: str, topic: str = None,
                         input_data: str = None, note_article: str = None) -> dict:
        """X (Twitter) 用の短文投稿を生成する"""
        max_chars = self.config.get("x", {}).get("max_chars", 280)

        if note_article:
            user_prompt = f"""以下のnote記事を元に、X（Twitter）用の投稿を1つ作成してください。

【記事内容】
{note_article[:1500]}

【条件】
- {max_chars}文字以内（ハッシュタグ含む）
- 記事への興味を引く内容
- note記事へのリンクを貼ることを前提に
- COYASSらしい口調で
"""
        else:
            user_prompt = f"""X（Twitter）用の投稿を1つ作成してください。

【カテゴリ】{category}
【トピック】{topic or "今日の話題を自由に"}
{f"【参考情報】{input_data}" if input_data else ""}

【条件】
- {max_chars}文字以内（ハッシュタグ含む）
- COYASSらしい口調で
- 読んだ人が「いいね」したくなる内容
"""

        result = self._call_ai(
            system_prompt=COYASS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=500
        )

        if result:
            text = result["text"].strip().strip('"').strip("'")
            hashtags = self._generate_hashtags(category, for_x=True)
            # ハッシュタグを付加（文字数制限内で）
            if len(text) + len(hashtags) + 2 <= max_chars:
                text = f"{text}\n\n{hashtags}"
            return {
                "text": text[:max_chars],
                "category": category,
                "ai_provider": result["provider"],
                "ai_model": result["model"]
            }
        return None

    def _build_note_prompt(self, category: str, topic: str, input_data: str,
                            min_len: int, max_len: int, template: str) -> str:
        """Note記事生成用のプロンプトを組み立てる"""
        prompt = f"""以下の条件でnote記事を1本書いてください。

【カテゴリ】{category}
【トピック】{topic or "今日の話題を自由に選んでください"}
{f"【参考情報・メモ】{input_data}" if input_data else ""}
【文字数】{min_len}〜{max_len}文字
【形式】
- 最初の1行目にタイトル（## は不要、テキストのみ）
- 2行目以降が本文
- 見出しはMarkdown形式（## ）を使用
- 箇条書きも適宜使用
- 最後に読者への呼びかけで締める

{f"【テンプレート参考】{template}" if template else ""}

重要：AIが書いたとわかる定型文は絶対に使わないでください。
COYASSが実際にキーボードを叩いて書いているように、生きた言葉で書いてください。
"""
        return prompt

    def _call_ai(self, system_prompt: str, user_prompt: str,
                  max_tokens: int = 4000) -> Optional[dict]:
        """AIプロバイダーを呼び出す（プライマリ→フォールバック）"""
        primary = self.ai_config.get("primary_provider", "openai")
        fallback = self.ai_config.get("fallback_provider", "gemini")

        # プライマリプロバイダーで試行
        result = self._call_provider(primary, system_prompt, user_prompt, max_tokens)
        if result:
            return result

        # フォールバック
        logger.warning(f"Primary ({primary}) failed, trying fallback ({fallback})")
        return self._call_provider(fallback, system_prompt, user_prompt, max_tokens)

    def _call_provider(self, provider: str, system_prompt: str,
                        user_prompt: str, max_tokens: int) -> Optional[dict]:
        """特定のAIプロバイダーを呼び出す"""
        try:
            if provider == "openai" and self.openai_client:
                model = self.ai_config.get("openai", {}).get("model", "gpt-4o")
                temp = self.ai_config.get("openai", {}).get("temperature", 0.8)
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temp
                )
                return {
                    "text": response.choices[0].message.content,
                    "provider": "openai",
                    "model": model
                }

            elif provider == "gemini" and self.gemini_model:
                model_name = self.ai_config.get("gemini", {}).get("model", "gemini-2.0-flash")
                combined_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"
                response = self.gemini_model.generate_content(combined_prompt)
                return {
                    "text": response.text,
                    "provider": "gemini",
                    "model": model_name
                }

        except Exception as e:
            logger.error(f"AI call failed ({provider}): {e}")
        return None

    def _parse_article(self, raw_text: str) -> tuple:
        """生成テキストからタイトルと本文を分離"""
        lines = raw_text.strip().split("\n")
        title = lines[0].strip().lstrip("#").strip() if lines else "無題"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else raw_text
        return title, body

    def _generate_hashtags(self, category: str, for_x: bool = False) -> str:
        """カテゴリに応じたハッシュタグを生成"""
        tags_config = self.persona.get("hashtags", {})
        tags = list(tags_config.get("always", []))

        category_map = {
            "dental_tips": "dental",
            "music_review": "music",
            "food_health": "lifestyle",
            "career": "lifestyle",
            "parenting": "lifestyle",
            "industry": "dental",
            "daily_doc": "lifestyle"
        }
        extra_key = category_map.get(category, "lifestyle")
        tags.extend(tags_config.get(extra_key, []))

        if for_x:
            # X用は3-4個に絞る
            tags = tags[:4]

        return " ".join(tags)
