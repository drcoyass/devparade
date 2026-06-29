#!/usr/bin/env python3
"""
🍖 Devparade プロモーション動画 一括自動生成スクリプト
=================================================

このスクリプトを実行すると、SNS投稿用の縦型ショート動画（9:16）を
複数のパターンで一気に自動生成します。

【生成される動画パターン】
1. ライブカウントダウン動画 (countdown_promo.mp4)
   - 7/12のライブまでのカウントダウンテキストとBGMを合成
2. アルバム告知動画 (album_release_promo.mp4)
   - 8/19発売の1stアルバム告知とジャケット画像、BGMを合成
3. バイラル格言動画（テーマ: 「深夜のラーメン」） (viral_ramen.mp4)
   - ポジデブ格言（AI台本）とメンバー写真、BGMを合成
4. バイラル格言動画（テーマ: 「デブの美学」） (viral_big_beauty.mp4)
   - 「太っていることは才能」をテーマにした格言動画

【実行方法】
python auto_generate_all.py
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATOR_SCRIPT = os.path.join(BASE_DIR, "generate_promo_shorts.py")
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python")

def run_video_generator(args):
    """generatorスクリプトを仮想環境のPythonで実行する"""
    cmd = [VENV_PYTHON, GENERATOR_SCRIPT] + args
    print(f"Executing: {' '.join(cmd)}")
    try:
        # 出力をリアルタイムで表示
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing generator with args {args}: {e}")
        return False

def main():
    global VENV_PYTHON
    # 1. 仮想環境の存在確認
    if not os.path.exists(VENV_PYTHON):
        # グローバルな python3 にフォールバック
        VENV_PYTHON = "python3"
        print("⚠️ Warning: Virtual environment not found. Using system python3.")

    print("==================================================")
    print("🍗 Devparade SNS Video Auto-Generation Batch")
    print("==================================================")

    # 生成するタスクの定義
    tasks = [
        {
            "name": "1. 7/12 下北沢CLUB Que ライブカウントダウン動画",
            "args": ["--mode", "countdown", "--output", "countdown_promo.mp4"]
        },
        {
            "name": "2. 8/19 1stアルバム『全ての武器をお箸に』告知動画",
            "args": ["--mode", "album", "--output", "album_release_promo.mp4"]
        },
        {
            "name": "3. ポジデブ格言バイラル動画 (テーマ: 深夜のラーメン)",
            "args": ["--mode", "viral", "--topic", "深夜のラーメン", "--output", "viral_ramen.mp4"]
        },
        {
            "name": "4. ポジデブ格言バイラル動画 (テーマ: デブの美学)",
            "args": ["--mode", "viral", "--topic", "デブの美学", "--output", "viral_big_beauty.mp4"]
        }
    ]

    success_count = 0
    for task in tasks:
        print(f"\n🚀 Starting: {task['name']}")
        print("-" * 40)
        success = run_video_generator(task['args'])
        if success:
            print(f"✅ Finished: {task['name']}")
            success_count += 1
        else:
            print(f"❌ Failed: {task['name']}")

    print("\n==================================================")
    print(f"🎉 バッチ処理完了: {success_count}/{len(tasks)} 個の動画が成功")
    print(f"出力先ディレクトリ: {os.path.join(BASE_DIR, 'output')}")
    print("==================================================")

if __name__ == "__main__":
    main()
