#!/usr/bin/env python3
"""
COYASS Quick Test - 依存パッケージ不要のGemini APIテスト
標準ライブラリのみ使用
"""

import json
import urllib.request
import urllib.error
import ssl
import os

API_KEY = "AIzaSyDUUbsUqJLJ5jg7lfaS54sCnY3-rbukCoc"

COYASS_PROMPT = """あなたはCOYASS（小安正洋）として文章を書きます。

【プロフィール】
- 歯科医師（中目黒コヤス歯科 院長）、歯学博士（審美歯科）
- ラッパー（MIC BANDITZ, デブパレード, E.P.O）
- 2児の父

【文体ルール】
- 専門知識を持ちつつもフランクで親しみやすい口調
- 「〜だ。」「〜だよな。」というラッパー的なリズム感
- 読者への問いかけを入れる
- AI臭い定型表現（「いかがでしたか？」「〜について解説します」等）は絶対に使わない
- 医療広告ガイドラインを遵守（「確実に治る」等の断定表現は使わない）
"""

def generate_note_article():
    """Gemini APIでNote記事を生成"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

    prompt = f"""{COYASS_PROMPT}

以下のテーマでNote記事を書いてください。
2000〜3000文字程度。見出し（##）を3〜4個入れてください。

テーマ: 歯磨きの常識を覆す話 — 食後すぐ磨くのは実はNGかもしれない

最後に以下の形式でハッシュタグを付けてください:
#COYASS #中目黒コヤス歯科 #予防歯科"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 4096
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    # SSL設定
    ctx = ssl.create_default_context()

    print("=" * 60)
    print("🦷🎤 COYASS Auto-Posting System - Gemini テスト")
    print("=" * 60)
    print("\n🔄 Gemini API に接続中...\n")

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        # レスポンス解析
        text = result["candidates"][0]["content"]["parts"][0]["text"]

        # 文字数カウント
        char_count = len(text)

        print(f"✅ 生成成功！\n")
        print(f"📊 文字数: {char_count}")
        print(f"🤖 モデル: Gemini 2.0 Flash")
        print("=" * 60)
        print(f"\n{text}\n")
        print("=" * 60)

        # 簡易品質チェック
        print("\n📋 簡易品質チェック:")
        issues = []
        ai_patterns = ["いかがでしたか", "について解説", "まとめると", "本記事では"]
        for p in ai_patterns:
            if p in text:
                issues.append(f"  ⚠️ AI定型表現を検出: '{p}'")
        forbidden = ["確実に治ります", "絶対に", "100%", "必ず治る"]
        for w in forbidden:
            if w in text:
                issues.append(f"  ❌ 医療ガイドライン違反の可能性: '{w}'")
        if issues:
            for i in issues:
                print(i)
        else:
            print("  ✅ 問題なし！")

        # ファイルに保存
        out_path = "data/test_article.md"
        os.makedirs("data", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n💾 保存先: {out_path}")

        return text

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"❌ API Error ({e.code}):")
        print(error_body[:500])
    except urllib.error.URLError as e:
        print(f"❌ 接続エラー: {e.reason}")
        print("   ネットワークに接続されていますか？")
    except Exception as e:
        print(f"❌ エラー: {e}")

    return None


if __name__ == "__main__":
    generate_note_article()
