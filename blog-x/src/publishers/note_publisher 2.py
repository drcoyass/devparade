"""
COYASS Auto-Posting System - Note Publisher
Playwright によるnote.comへの自動投稿
"""

import os
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class NotePublisher:
    """Playwright を使った note.com への自動投稿"""

    def __init__(self, config: dict):
        self.config = config.get("note", {})
        self.base_url = self.config.get("base_url", "https://note.com")
        self.publish_mode = self.config.get("publish_mode", "draft")
        self.retry_attempts = self.config.get("retry_attempts", 3)
        self.retry_delay = self.config.get("retry_delay_seconds", 30)
        self.screenshot_dir = Path("playwright-screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.browser = None
        self.page = None

    async def initialize(self):
        """Playwright ブラウザを初期化"""
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox"]
            )
            self.state_file = Path("data/note_state.json")
            context_args = {
                "viewport": {"width": 1280, "height": 800},
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            if self.state_file.exists():
                context_args["storage_state"] = str(self.state_file)
                
            self.context = await self.browser.new_context(**context_args)
            self.page = await self.context.new_page()
            logger.info("✅ Playwright browser initialized")
        except Exception as e:
            logger.error(f"❌ Playwright init failed: {e}")
            raise

    async def login(self) -> bool:
        """note.com にログイン"""
        try:
            # 1. 保存されたセッション（Googleログイン等）の確認
            await self.page.goto(self.base_url, wait_until="networkidle")
            await self._human_delay()
            
            # トップページに「ログイン」ボタンがないか、プロフィール画像があるかで判定
            login_buttons = await self.page.query_selector_all('a[href*="/login"]')
            if not login_buttons:
                logger.info("✅ note.com already logged in via saved session state")
                return True
                
            # 2. セッションがない場合、環境変数のメール/パスワードを試す
            email = os.getenv("NOTE_EMAIL")
            password = os.getenv("NOTE_PASSWORD")

            if not email or not password:
                logger.error("❌ NOTE_EMAIL / NOTE_PASSWORD not set and no valid session state found.")
                logger.error("💡 Googleログインを使用する場合は、先に `python3 setup_note_login.py` を実行してログイン状態を保存してください。")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Session check failed: {e}")

        try:
            await self.page.goto(f"{self.base_url}/login", wait_until="networkidle")
            await self._human_delay()

            await self.page.fill('input[name="login"]', email)
            await self._human_delay(0.5, 1.5)

            await self.page.fill('input[name="password"]', password)
            await self._human_delay(0.5, 1.0)

            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state("networkidle")
            await self._human_delay(2.0, 4.0)

            if "/login" not in self.page.url:
                logger.info("✅ note.com login successful")
                await self._save_screenshot("login_success")
                return True
            else:
                logger.error("❌ note.com login failed")
                await self._save_screenshot("login_failed")
                return False

        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            await self._save_screenshot("login_error")
            return False

    async def publish_article(self, title: str, body: str,
                               hashtags: str = None, image_path: str = None) -> Optional[dict]:
        """note に記事を投稿する"""
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"📝 Publishing to note (attempt {attempt + 1})...")

                await self.page.goto(f"{self.base_url}/n/new", wait_until="networkidle")
                await self._human_delay(2.0, 3.0)

                # タイトル入力
                title_input = await self.page.wait_for_selector(
                    'textarea[placeholder*="タイトル"], textarea[data-testid="title-input"]',
                    timeout=10000
                )
                if title_input:
                    await title_input.click()
                    await self._human_type(title_input, title)
                    await self._human_delay()

                # 見出し画像のアップロード
                if image_path and os.path.exists(image_path):
                    try:
                        logger.info(f"🖼️ Uploading cover image: {image_path}")
                        # ファイル入力を探して画像をセット
                        file_inputs = await self.page.query_selector_all('input[type="file"]')
                        for file_input in file_inputs:
                            await file_input.set_input_files(image_path)
                            await self._human_delay(3.0, 5.0)
                            logger.info("✅ Cover image uploaded")
                            break
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to upload cover image: {e}")

                # 本文入力
                body_area = await self.page.wait_for_selector(
                    'div[contenteditable="true"], div[data-testid="body-editor"]',
                    timeout=10000
                )
                if body_area:
                    await body_area.click()
                    paragraphs = body.split("\n\n")
                    for i, para in enumerate(paragraphs):
                        await body_area.type(para)
                        if i < len(paragraphs) - 1:
                            await self.page.keyboard.press("Enter")
                            await self.page.keyboard.press("Enter")
                        await self._human_delay(0.2, 0.5)

                await self._human_delay(1.0, 2.0)
                await self._save_screenshot("article_written")

                # ハッシュタグ
                if hashtags:
                    await self._set_hashtags(hashtags)

                # 下書き保存 or 公開
                if self.publish_mode == "draft":
                    result = await self._save_as_draft()
                else:
                    result = await self._publish()

                if result:
                    logger.info(f"✅ Article posted: {title}")
                    return result

            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                await self._save_screenshot(f"publish_error_{attempt}")
                if attempt < self.retry_attempts - 1:
                    await self._human_delay(self.retry_delay, self.retry_delay + 10)

        return None

    async def _set_hashtags(self, hashtags: str):
        try:
            tags = [t.strip().lstrip("#") for t in hashtags.split() if t.startswith("#")]
            for tag in tags[:5]:
                tag_input = await self.page.query_selector(
                    'input[placeholder*="タグ"], input[data-testid="tag-input"]'
                )
                if tag_input:
                    await tag_input.fill(tag)
                    await self.page.keyboard.press("Enter")
                    await self._human_delay(0.3, 0.8)
        except Exception as e:
            logger.warning(f"⚠️ Hashtag setting failed: {e}")

    async def _save_as_draft(self) -> Optional[dict]:
        try:
            draft_btn = await self.page.query_selector(
                'button:has-text("下書き"), button[data-testid="save-draft"]'
            )
            if draft_btn:
                await draft_btn.click()
                await self.page.wait_for_load_state("networkidle")
                await self._human_delay(2.0, 3.0)
                await self._save_screenshot("draft_saved")
                return {
                    "status": "draft",
                    "url": self.page.url,
                    "published_at": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"❌ Draft save failed: {e}")
        return None

    async def _publish(self) -> Optional[dict]:
        try:
            publish_btn = await self.page.query_selector(
                'button:has-text("公開"), button:has-text("投稿")'
            )
            if publish_btn:
                await publish_btn.click()
                await self.page.wait_for_load_state("networkidle")
                await self._human_delay(3.0, 5.0)

                confirm_btn = await self.page.query_selector(
                    'button:has-text("公開する"), button:has-text("投稿する")'
                )
                if confirm_btn:
                    await confirm_btn.click()
                    await self.page.wait_for_load_state("networkidle")
                    await self._human_delay(2.0, 3.0)

                await self._save_screenshot("published")
                return {
                    "status": "published",
                    "url": self.page.url,
                    "published_at": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")
        return None

    async def _human_type(self, element, text: str):
        for char in text:
            await element.type(char, delay=random.randint(30, 100))

    async def _human_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    async def _save_screenshot(self, name: str):
        if self.page:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = self.screenshot_dir / f"{name}_{timestamp}.png"
            await self.page.screenshot(path=str(path))
            logger.debug(f"📸 Screenshot: {path}")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("🔒 Browser closed")
