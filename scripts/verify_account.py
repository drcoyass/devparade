#!/usr/bin/env python3
"""
アカウント検証スクリプト
現在設定されているCookieがどのアカウント（@ユーザー名）として認識されているかを表示します。
投稿は一切行いません。
"""

import os
import sys
import asyncio
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BASE_DIR / "scripts"))

from x_client import _get_twikit_client

async def main():
    print("=" * 60)
    print("🔍 Xアカウント ログイン検証テスト")
    print("=" * 60)
    
    client = await _get_twikit_client()
    if not client:
        print("❌ クライアント初期化失敗（Cookieが無効か、アカウント不一致ガードでブロックされました）")
        return

    try:
        user = await client.user()
        print(f"🎉 ログイン認証成功！")
        print(f"ユーザー名: @{user.screen_name}")
        print(f"表示名: {user.name}")
        print(f"ユーザーID: {user.id}")
        
        if user.screen_name.lower() == "dev_parade":
            print("✅ デブパレード公式アカウント (@dev_parade) と一致しました！")
        else:
            print(f"⚠️ 注意: 公式アカウントではありません (@{user.screen_name})")
    except Exception as e:
        print(f"❌ ユーザー情報取得失敗: {e}")

if __name__ == "__main__":
    asyncio.run(main())
