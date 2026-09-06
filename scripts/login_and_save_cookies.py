#!/usr/bin/env python3
"""
🍪 X (Twitter) セッションクッキー生成＆GitHub Secrets自動登録スクリプト
========================================================================
Xの最新仕様変更により、ID/パスワードでの自動ログインが遮断され、
セッションCookie（auth_token / ct0）による認証が必須となりました。

このスクリプトは、ブラウザから取得した2つのCookie値を元に
twikit / twifork 用の cookies.json を生成し、GitHub Secrets に自動登録します。

【Cookieの取得方法 (約1分)】
1. Chromeなどのブラウザで https://x.com にログイン
2. F12（Mac: Cmd+Option+I）で「デベロッパーツール」を開く
3. 「アプリケーション (Application)」タブ → 「Cookie」 → 「https://x.com」を開く
4. 一覧から以下の2つの値をコピー：
   - auth_token
   - ct0
"""

import sys
import json
import subprocess
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
COOKIES_FILE = _BASE_DIR / "data" / "twikit_cookies.json"


def main():
    print("=" * 60)
    print("🍪 X (Twitter) クッキー登録ウィザード")
    print("=" * 60)
    print("ブラウザのデベロッパーツールから取得した値を入力してください。\n")

    auth_token = input("🔑 auth_token を入力してください: ").strip()
    if not auth_token:
        print("❌ auth_token が空です。中止します。")
        return

    ct0 = input("🔑 ct0 を入力してください: ").strip()
    if not ct0:
        print("❌ ct0 が空です。中止します。")
        return

    # twikit / twifork が期待するCookie辞書構造
    cookies_data = {
        "auth_token": auth_token,
        "ct0": ct0
    }

    # ローカルの data/twikit_cookies.json に保存
    COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies_data, f, indent=2)

    print(f"\n✅ ローカルにクッキーを保存しました: {COOKIES_FILE}")

    # JSON文字列にして GitHub Secrets に登録
    cookies_json_str = json.dumps(cookies_data)
    print("📡 GitHub Secrets (X_COOKIES_JSON) に登録中...")
    try:
        proc = subprocess.run(
            ["gh", "secret", "set", "X_COOKIES_JSON", "--repo", "drcoyass/devparade"],
            input=cookies_json_str,
            text=True,
            capture_output=True,
            cwd=str(_BASE_DIR)
        )
        if proc.returncode == 0:
            print("🎉 GitHub Secrets への登録が成功しました！")
            print("これでGitHub Actionsからの自動投稿が100%動作するようになります！")
        else:
            print(f"⚠️ gh secret set エラー: {proc.stderr}")
            print(f"手動で以下のJSONを GitHub Secrets の 'X_COOKIES_JSON' に設定してください:\n{cookies_json_str}")
    except Exception as e:
        print(f"⚠️ 登録エラー: {e}")


if __name__ == "__main__":
    main()
