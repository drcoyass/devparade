#!/bin/bash
# =============================================================
# 🎵 Devparade「夏の終わりに」リリック動画 ワンコマンド生成スクリプト
# =============================================================
# 使い方:
#   cd video-automation
#   bash generate_natsunoowarini.sh
#
# 依存関係:
#   pip install moviepy whisper yt-dlp
#   ffmpeg (homebrew: brew install ffmpeg)
# =============================================================

set -e  # エラーで即停止

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🎵 Devparade「夏の終わりに」リリック動画生成スクリプト"
echo "======================================================="

# 仮想環境チェック
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 仮想環境を有効化しました"
else
    echo "⚠️  venv が見つかりません。グローバル Python を使用します。"
fi

SONG_ID="06_夏の終わりに"
AUDIO_DIR="assets"
AUDIO_FILE="${AUDIO_DIR}/natsu_no_owari_ni.mp3"
OUTPUT_NAME="natsu_no_owari_ni_lyric.mp4"

echo ""
echo "📋 設定:"
echo "   曲ID: ${SONG_ID}"
echo "   出力: output/${OUTPUT_NAME}"
echo ""

# 背景画像の確認
BG_IMAGE="assets/natsu_bg.png"
if [ ! -f "$BG_IMAGE" ]; then
    echo "🖼️  背景画像が見つかりません。デフォルト画像を生成します..."
    python3 - <<'PYEOF'
from PIL import Image, ImageDraw, ImageFilter
import random, math

# 夏の終わり・哀愁をテーマにした夕暮れグラデーション背景
W, H = 1080, 1920
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

# 夕暮れグラデーション (上: 深い青紫 → 下: オレンジピンク)
colors = [
    (15, 10, 40),    # 上端: 深夜ブルー
    (40, 20, 80),    # 上部: 濃い紫
    (120, 40, 80),   # 中上部: マゼンタ
    (200, 80, 50),   # 中央: 深いオレンジ
    (230, 130, 60),  # 中下部: サンセットオレンジ
    (240, 180, 100), # 下部: 黄金色
    (250, 220, 150), # 下端: 淡い黄色
]

for y in range(H):
    ratio = y / H
    # 色の補間
    segment = ratio * (len(colors) - 1)
    idx = int(segment)
    t = segment - idx
    if idx >= len(colors) - 1:
        r, g, b = colors[-1]
    else:
        c1, c2 = colors[idx], colors[idx+1]
        r = int(c1[0] + (c2[0]-c1[0]) * t)
        g = int(c1[1] + (c2[1]-c1[1]) * t)
        b = int(c1[2] + (c2[2]-c1[2]) * t)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# ノイズでテクスチャを追加（夕焼けの雰囲気）
import os
import numpy as np
img_arr = np.array(img, dtype=np.float32)
noise = np.random.normal(0, 8, img_arr.shape)
img_arr = np.clip(img_arr + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(img_arr)

# 軽くぼかしてなめらかに
img = img.filter(ImageFilter.GaussianBlur(radius=1))

os.makedirs("assets", exist_ok=True)
img.save("assets/natsu_bg.png")
print("✅ 背景画像を生成しました: assets/natsu_bg.png")
PYEOF
fi

# Pillowがない場合のフォールバック
if [ ! -f "$BG_IMAGE" ]; then
    echo "⚠️  Pillow が必要です: pip install Pillow"
    echo "   または手動で assets/natsu_bg.png を用意してください"
    # シンプルな単色画像をffmpegで作成
    ffmpeg -f lavfi -i color=c=0x1a0a3a:size=1080x1920 -frames:v 1 "$BG_IMAGE" -y 2>/dev/null && \
        echo "✅ ffmpeg でシンプル背景を生成しました" || \
        echo "❌ 背景画像の生成に失敗しました。手動で assets/natsu_bg.png を用意してください。"
fi

echo ""

# 音源チェック
if [ ! -f "$AUDIO_FILE" ]; then
    echo "🎵 音源ファイルが見つかりません: ${AUDIO_FILE}"
    echo ""
    echo "音源を用意する方法:"
    echo "  1. 手動: ${AUDIO_FILE} に mp3 ファイルをコピー"
    echo "  2. SoundCloud URL から自動DL (yt-dlp 使用):"
    echo "     yt-dlp -x --audio-format mp3 -o '${AUDIO_FILE}' 'https://on.soundcloud.com/j1noHG1GjdyFiHtHsg'"
    echo ""
    read -p "  SoundCloud から自動ダウンロードしますか? [y/N]: " yn
    if [[ "$yn" =~ ^[Yy] ]]; then
        mkdir -p "$AUDIO_DIR"
        yt-dlp -x --audio-format mp3 \
            -o "${AUDIO_DIR}/natsu_no_owari_ni.%(ext)s" \
            "https://on.soundcloud.com/j1noHG1GjdyFiHtHsg"
        echo "✅ 音源をダウンロードしました"
    else
        echo "⚠️  音源なしでは動画生成できません。"
        echo "   ${AUDIO_FILE} を用意してから再実行してください。"
        exit 1
    fi
fi

echo ""
echo "🎬 動画生成を開始します..."
echo "   ※ Whisper による音声解析は数分かかる場合があります"
echo ""

# 動画生成実行
python3 generate_video.py \
    --song-id "${SONG_ID}" \
    --audio "${AUDIO_FILE}" \
    --image "${BG_IMAGE}" \
    --output "${OUTPUT_NAME}"

echo ""
echo "=============================================="
echo "✅ 完了！"
echo "   出力ファイル: output/${OUTPUT_NAME}"
echo ""
echo "📱 投稿先:"
echo "   TikTok    → 動画をそのままアップロード"
echo "   Instagram → Reels としてアップロード"
echo "   YouTube   → Shorts として「#Shorts」タグ付きでアップロード"
echo "   X(Twitter)→ 動画添付ツイートで投稿"
echo ""
echo "🎵 推奨キャプション (コピペ用):"
echo "---------------------------------------------"
echo '「夏の終わりに」/ Devparade'
echo ''
echo '夏の終わりのリズムが、また僕を惑わせた。'
echo '15年ぶりに鳴らす、デブたちのラブソング。'
echo ''
echo '配信中👇'
echo 'https://link-map.jp/links/t7J6lCsV'
echo ''
echo '#デブパレード #夏の終わりに #NARUTO #バッチコイ #ロックバンド'
echo "=============================================="
