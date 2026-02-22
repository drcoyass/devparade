#!/usr/bin/env python3
"""
Note ログインセッション保存スクリプト (Googleログイン対応用)

このスクリプトを実行すると、画面にブラウザが表示されます。
手動でNoteにログイン（Googleログイン等）してください。
ログイン完了後、自動的にセッション情報が保存され、ブラウザが閉じます。
以降の自動投稿では、この保存されたセッションが使われます。
"""

import sys
import asyncio
from pathlib import Path

# src モジュールをインポートできるようにパスを追加
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright

async def main():
    print("=" * 60)
    print("🔑 COYASS Auto-Posting System - Note ログイン連携")
    print("=" * 60)
    print("これからブラウザが立ち上がります。")
    print("Noteのログイン画面が表示されたら、手動でGoogleログイン等を行ってください。")
    print("ログインが完了してトップページに戻ると、自動的に状態を保存して終了します。")
    print("-" * 60)

    # データを保存するフォルダの作成
    Path("data").mkdir(exist_ok=True)
    state_file = "data/note_state.json"

    async with async_playwright() as p:
        # headless=False にして、実際に画面を表示する
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Noteログイン画面へ
        await page.goto("https://note.com/login")

        print("\n⏳ ブラウザでログイン操作を行ってください...")
        print("💡 注: ログイン完了後、元の画面に戻るまでブラウザを開いたままにしてください。")

        # ログイン後、URLがトップページ（または特定のパス）に変わるのを待つ
        # タイムアウトを長め（5分）に設定
        try:
            # Noteの場合、ログインするとホーム等の画面に遷移するので、URLが変わるのを待つ
            # CSPエラー（unsafe-eval）を避けるため、wait_for_function ではなく wait_for_url を使用
            print("  （ログインが完了してURLが変わるのを待機しています...）")
            
            # "/login" 以外のURLになるのを待つ（最大5分）
            import time
            start_time = time.time()
            logged_in = False
            
            while time.time() - start_time < 300:
                if "/login" not in page.url:
                    logged_in = True
                    break
                await asyncio.sleep(1)
                
            if not logged_in:
                raise TimeoutError("ログイン待機時間が5分を超えました。")
            
            # 少し待ってステートを安定させる
            await page.wait_for_timeout(3000)
            
            # 状態（Cookie, LocalStorage）を保存
            await context.storage_state(path=state_file)
            print(f"\n✅ ログイン完了！セッション情報を保存しました: {state_file}")
            print("これで `test_publish_note.py` などの自動投稿がパスワードなしで実行可能になります。")

        except Exception as e:
            print(f"\n❌ エラーが発生したか、タイムアウトしました: {e}")
            print("もう一度実行して、5分以内にログインを完了させてください。")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
