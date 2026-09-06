#!/usr/bin/env python3
"""
🍗 Devparade SNSショート動画自動生成ジェネレーター (TikTok / Shorts / Reels 向け)
========================================================================

背景画像（スライドショー）、BGM、美しい日本語テロップ（Pillow描画）を合成し、
バズる縦型ショート動画（1080x1920, 9:16）を自動生成します。

【主な機能】
1. ライブカウントダウンモード (--mode countdown):
   7/12の復活ライブまでの日数を自動計算し、告知動画を作成。
2. アルバム告知モード (--mode album):
   8/19発売の1stアルバム「全ての武器をお箸に」の告知動画を作成。
3. AIバイラル台本モード (--mode viral --topic <お題>):
   AI（OpenAI）でバズるポジデブ台本を自動生成し、それをテロップ化した動画を作成。
4. カスタムモード (--mode custom --texts "テキスト1,テキスト2"):
   自由なテキストを一定間隔で表示する動画を作成。

【依存環境】
- moviepy, Pillow, numpy, requests (AI連携時)
- ffmpeg (PCにインストールされている必要があります)
"""

import os
import sys
import json
import argparse
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# moviepyのインポート (エラーハンドリング付き)
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
    import moviepy.video.fx.all as vfx
except ImportError:
    print("Error: moviepy is not installed. Run: pip install moviepy")
    sys.exit(1)

# yt-dlpのインポート
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# パスの定義
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DEFAULT_BGM_DIR = os.path.join(BASE_DIR, 'assets')
GLOBAL_ASSETS_DIR = os.path.join(PROJECT_DIR, 'assets')

# 日本語フォント候補 (Mac優先)
FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/System/Library/Fonts/Supplemental/ヒラギノ角ゴ Pro W3.otf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Microsoft/MS Gothic.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",  # Linux fallback
    "Arial"
]

def get_font(font_size):
    """システムに存在するフォントをロードする"""
    for font_path in FONT_CANDIDATES:
        if os.path.exists(font_path) or font_path == "Arial":
            try:
                if font_path == "Arial":
                    return ImageFont.load_default()
                return ImageFont.truetype(font_path, font_size)
            except Exception:
                continue
    return ImageFont.load_default()

def download_default_bgm(output_path):
    """バッチコイ!!! の音源をYouTubeからダウンロードしてデフォルトBGMにする"""
    if not yt_dlp:
        print("⚠️ Warning: yt_dlp is not installed. Skipping audio download.")
        return False
    
    # バッチコイ!!! の候補URLリスト（1つ目がダメなら2つ目を試す）
    urls = [
        "https://www.youtube.com/watch?v=F_fV35D92-U",
        "https://www.youtube.com/watch?v=kUz8D1D1e90"
    ]
    
    for url in urls:
        print(f"🎵 デフォルトBGMをダウンロード中: {url}...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path.replace('.mp3', ''),  # yt-dlp adds extension
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"✅ デフォルトBGMダウンロード成功: {output_path}")
            return True
        except Exception as e:
            print(f"⚠️ このURLでのダウンロードに失敗しました: {e}")
            continue
            
    print("❌ すべての候補URLでのBGMダウンロードに失敗しました。")
    return False

def download_fallback_free_bgm(output_path):
    """YouTubeがダメな場合、インターネット上のテスト用MP3を直接ダウンロードしてBGMにする"""
    url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    print(f"🎵 テスト用BGM（SoundHelix）を直接ダウンロード中: {url}...")
    try:
        import urllib.request
        # User-Agentを設定してアクセス拒否を回避
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"✅ テスト用BGMのダウンロードに成功: {output_path}")
        return True
    except Exception as e:
        print(f"⚠️ テスト用BGMのダウンロードに失敗: {e}")
        return False

def crop_and_resize_to_9_16(img_path, target_w=1080, target_h=1920, blur_bg=True):
    """
    画像を縦横比9:16に綺麗にリサイズ＆クロップする。
    画像が横長の場合、中央を切り取るか、
    blur_bg=True の場合は、画像を背景にぼかして引き伸ばし、手前にアスペクト比を維持した画像を重ねる。
    """
    try:
        img = Image.open(img_path)
    except Exception as e:
        print(f"Error opening image {img_path}: {e}")
        # 代替として黒い画像を生成
        return Image.new('RGB', (target_w, target_h), (15, 15, 15))

    img_w, img_h = img.size
    target_ratio = target_w / target_h
    img_ratio = img_w / img_h

    # アスペクト比がほぼ9:16なら、そのままリサイズして中央クロップ
    if not blur_bg or abs(img_ratio - target_ratio) < 0.1:
        # 中央クロップ
        if img_ratio > target_ratio:
            # 横長なので高さを合わせて幅を削る
            new_h = target_h
            new_w = int(img_w * (target_h / img_h))
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            return img_resized.crop((left, 0, left + target_w, target_h))
        else:
            # 縦長すぎるので幅を合わせて高さを削る
            new_w = target_w
            new_h = int(img_h * (target_w / img_w))
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            top = (new_h - target_h) // 2
            return img_resized.crop((0, top, target_w, top + target_h))
    
    # 横長画像を縦型に美しく見せるための「ぼかし背景＋手前縮小表示」
    else:
        # 1. ぼかし背景の作成 (全体を埋めるように拡大してぼかす)
        if img_ratio > target_ratio:
            bg_w = int(target_h * img_ratio)
            bg_h = target_h
        else:
            bg_w = target_w
            bg_h = int(target_w / img_ratio)
        
        bg_img = img.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
        left = (bg_w - target_w) // 2
        top = (bg_h - target_h) // 2
        bg_img = bg_img.crop((left, top, left + target_w, top + target_h))
        bg_img = bg_img.filter(ImageFilter.GaussianBlur(30)) # 強いぼかし
        
        # 暗くするフィルターを重ねる
        dark = Image.new('RGB', (target_w, target_h), (0, 0, 0))
        bg_img = Image.blend(bg_img, dark, 0.4)

        # 2. 手前のメイン画像の作成 (アスペクト比維持で幅いっぱいにフィット)
        main_w = target_w
        main_h = int(target_w / img_ratio)
        if main_h > target_h - 200: # 縦に大きすぎる場合は高さを制限
            main_h = target_h - 200
            main_w = int(main_h * img_ratio)
            
        main_img = img.resize((main_w, main_h), Image.Resampling.LANCZOS)
        
        # 3. 合成
        offset_x = (target_w - main_w) // 2
        offset_y = (target_h - main_h) // 2
        bg_img.paste(main_img, (offset_x, offset_y))
        return bg_img

def create_text_clip_image(text, width=1080, height=1920, font_size=64, text_color=(255, 255, 255), stroke_color=(0, 0, 0), stroke_width=6, bg_box=True):
    """
    Pillowを使って日本語のテロップ用透過PNG画像を生成し、
    それをMoviePyのImageClip（マスク付き）に変換して返す。
    ImageMagick不要で日本語を完全にレンダリング可能。
    """
    # 1. 透過画像を作成
    txt_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(txt_img)
    font = get_font(font_size)

    # 2. テキストを改行ごとに分解して描画サイズを計算
    lines = text.split('\n')
    line_heights = []
    total_h = 0
    max_w = 0
    
    # 各行のサイズ計算
    for line in lines:
        # draw.textbbox は Pillow 9.2+ で利用可能、非互換対策も考慮
        try:
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
            w = right - left
            h = bottom - top
        except AttributeError:
            w, h = draw.textsize(line, font=font)
        
        w = max(w, 1)
        h = max(h, font_size)
        line_heights.append(h)
        total_h += h + 15
        max_w = max(max_w, w)

    # 3. テロップ用の「半透明の黒帯（座布団）」を背景に描画（オプション）
    if bg_box:
        box_padding_x = 40
        box_padding_y = 30
        box_w = min(max_w + box_padding_x * 2, width - 80)
        box_h = total_h + box_padding_y
        
        box_left = (width - box_w) // 2
        box_top = (height - box_h) // 2 + 100 # 少し下に配置
        
        # 半透明黒の角丸長方形
        draw.rounded_rectangle(
            [box_left, box_top, box_left + box_w, box_top + box_h],
            radius=15,
            fill=(0, 0, 0, 160)
        )
        
        # テキストの描画開始位置（座布団の中央）
        curr_y = box_top + box_padding_y // 2
    else:
        # 画面中央やや下に直接配置
        curr_y = (height - total_h) // 2 + 200

    # 4. 文字を縁取り（ストローク）付きで描画
    for i, line in enumerate(lines):
        try:
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
            w = right - left
        except AttributeError:
            w, _ = draw.textsize(line, font=font)
            
        x = (width - w) // 2
        
        # 縁取り描画（Pillowのstroke_width機能を使用）
        draw.text(
            (x, curr_y), 
            line, 
            font=font, 
            fill=text_color, 
            stroke_fill=stroke_color, 
            stroke_width=stroke_width
        )
        curr_y += line_heights[i] + 15

    # 5. PIL Image から MoviePy ImageClip への変換
    img_np = np.array(txt_img)
    rgb_img = img_np[:, :, :3]
    alpha_mask = img_np[:, :, 3] / 255.0

    # RGBのImageClipを作成し、透過マスクを設定
    clip = ImageClip(rgb_img)
    mask_clip = ImageClip(alpha_mask, ismask=True)
    return clip.set_mask(mask_clip)

def get_countdown_days():
    """2026年7月12日までの残り日数を取得"""
    target_date = datetime(2026, 7, 12)
    today = datetime.now()
    delta = target_date - today
    return max(0, delta.days)

def load_ai_viral_script(topic):
    """multi_platform_viral_engineを呼び出して台本を生成する"""
    sys.path.append(PROJECT_DIR)
    try:
        from scripts.multi_platform_viral_engine import ViralEngine, API_KEY
        if not API_KEY:
            # .envから直接ロードを試みる
            import os
            from pathlib import Path
            env_paths = [Path(".env"), Path("../.env"), Path("blog-x/.env")]
            for p in env_paths:
                if p.exists():
                    with open(p, "r") as f:
                        for line in f:
                            if "=" in line:
                                k, v = line.strip().split("=", 1)
                                if k == "OPENAI_API_KEY":
                                    API_KEY = v
                                    break
        
        if not API_KEY:
            print("⚠️ Warning: OPENAI_API_KEY が見つかりません。デフォルトの台本を使用します。")
            return get_fallback_script(topic)
            
        print(f"🤖 AI (GPT-4o) でお題『{topic}』に基づくTikTok用台本を生成中...")
        engine = ViralEngine(API_KEY)
        response = engine.generate(topic)
        
        # 台本からテロップ部分（ナレーション部分）を抽出
        lines = []
        for line in response.split('\n'):
            line = line.strip()
            # 「テロップ:」や「セリフ:」「ナレーション:」などのプレフィックスを取り除く
            if any(line.startswith(p) for p in ["テロップ:", "ナレーション:", "X:", "Instagram:", "TikTok:"]):
                continue
            if not line or line.startswith("【") or line.startswith("#"):
                continue
            # テロップテキストを抽出
            if "テロップ" in line or "画面" in line:
                cleaned = line.split(":")[-1].replace('"', '').strip()
                if cleaned:
                    lines.append(cleaned)
            elif ":" in line:
                cleaned = line.split(":")[-1].replace('"', '').strip()
                if len(cleaned) > 5 and len(cleaned) < 50:
                    lines.append(cleaned)
            elif len(line) > 5 and len(line) < 40:
                lines.append(line)
                
        if len(lines) >= 3:
            return lines[:5] # 最大5フレーズ
        else:
            # 解析がうまくいかなかった場合は適当に分割
            clean_lines = [l for l in response.split('\n') if len(l) > 10 and not l.startswith("http")]
            return clean_lines[:5]
            
    except Exception as e:
        print(f"⚠️ AI台本生成エラー: {e}。デフォルト台本にフォールバックします。")
        return get_fallback_script(topic)

def get_fallback_script(topic):
    """AIが動かなかった場合の代替台本"""
    return [
        f"テーマ：{topic}について！",
        "デブパレード流の極意を伝授するぜ！",
        "細かいことは気にするな！肉を食え！",
        "7/12 下北沢CLUB Queで待ってる！",
        "15年ぶりの復活ライブ、絶対来いよ！"
    ]

def build_promo_video(mode="countdown", topic=None, days=None, custom_texts=None, audio_path=None, output_filename=None):
    """動画をビルドするメイン関数"""
    
    # 1. 出力ファイル名の設定
    if not output_filename:
        output_filename = f"promo_{mode}_{datetime.now().strftime('%m%d_%H%M')}.mp4"
    if not output_filename.endswith('.mp4'):
        output_filename += '.mp4'
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    final_output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # 2. テキストと背景素材、BGMの決定
    texts = []
    image_paths = []
    
    # BGMのデフォルト設定 (assetsから探す、無ければダウンロード)
    if not audio_path:
        # parfait.mp3 または メンバーお勧め曲などを探す
        audio_candidates = [
            os.path.join(DEFAULT_BGM_DIR, "parfait.mp3"),
            os.path.join(DEFAULT_BGM_DIR, "bacchi-koi.mp3"),
            os.path.join(PROJECT_DIR, "assets", "parfait.mp3"),
        ]
        # assets内に他のmp3があるか検索
        if os.path.exists(GLOBAL_ASSETS_DIR):
            for file in os.listdir(GLOBAL_ASSETS_DIR):
                if file.endswith('.mp3'):
                    audio_candidates.append(os.path.join(GLOBAL_ASSETS_DIR, file))
                    
        for path in audio_candidates:
            if os.path.exists(path):
                audio_path = path
                break
        
        # 見つからない場合はバッチコイ!!!をダウンロード
        if not audio_path:
            default_path = os.path.join(DEFAULT_BGM_DIR, "bacchi-koi.mp3")
            os.makedirs(DEFAULT_BGM_DIR, exist_ok=True)
            if download_default_bgm(default_path):
                audio_path = default_path
            elif download_fallback_free_bgm(default_path):
                audio_path = default_path

    # モードに応じたコンテンツ設定
    if mode == "countdown":
        remaining_days = days if days is not None else get_countdown_days()
        texts = [
            "⚠️緊急告知⚠️\nデブパレード 15年ぶりの復活！",
            f"下北沢 CLUB Que ワンマンライブまで\n【 あと {remaining_days} 日 】",
            "メンバー全員90kgオーバーの爆音！\nこの熱量、生で体験せよ！",
            "チケット絶賛発売中！\n売り切れる前に急げ！"
        ]
        # 背景画像（フライヤーやバンド画像）
        image_candidates = ["flyer-20260712.jpg", "flyer-20260614.jpeg", "member-group.jpg", "live-front.jpg", "member-closeup.jpg"]
        for name in image_candidates:
            path = os.path.join(GLOBAL_ASSETS_DIR, name)
            if os.path.exists(path):
                image_paths.append(path)
                
    elif mode == "album":
        texts = [
            "🍖 デブパレード メジャー復活！ 🍖",
            "1st Full Album\n『全ての武器をお箸に』",
            "2026.08.19 (WED)\n待望のリリース決定！",
            "15年の沈黙を破り、\nポジデブ魂が再び日本を揺らす！",
            "詳細は公式サイトをチェック！"
        ]
        # 背景はアルバムジャケット優先
        album_cover = os.path.join(GLOBAL_ASSETS_DIR, "album-hashi.jpg")
        if os.path.exists(album_cover):
            image_paths.append(album_cover)
        # メンバー写真も追加
        group_pic = os.path.join(GLOBAL_ASSETS_DIR, "member-group.jpg")
        if os.path.exists(group_pic):
            image_paths.append(group_pic)

    elif mode == "single0904":
        texts = [
            "15年前、リリースできなかった\n親友への追悼の歌がある。",
            "『お前がメジャーでやってるだけで\n俺は最高だと思うぜ！』",
            "病室の高校生に自慢してくれた友は、\nその年の9月4日に旅立った。",
            "15年ぶりの奇跡の復活。\nこの忘れ物を取りに来た。",
            "『何千曲と歌ってきたが、\nここまで泣いて歌えんかったのは初めてだ』\n― ハンサム判治",
            "ハンサム判治 feat. デブパレード\nDigital Single「9月4日」\n各配信ストアで配信中！"
        ]
        cover_pic = os.path.join(GLOBAL_ASSETS_DIR, "single-0904.jpg")
        if os.path.exists(cover_pic):
            image_paths.append(cover_pic)
        for c in ["member-group.jpg", "member-hanzi.jpg", "live-front.jpg"]:
            path = os.path.join(GLOBAL_ASSETS_DIR, c)
            if os.path.exists(path):
                image_paths.append(path)

    elif mode == "viral":
        if not topic:
            topic = "深夜のラーメン"
        texts = load_ai_viral_script(topic)
        # メンバー写真をスライドショーに使う
        candidates = ["member-group.jpg", "member-coyass.jpg", "member-hanzi.jpg", "member-ugazin.jpg", "member-tah.jpg"]
        for c in candidates:
            path = os.path.join(GLOBAL_ASSETS_DIR, c)
            if os.path.exists(path):
                image_paths.append(path)
                
    elif mode == "royal":
        texts = [
            "🔥 15年の沈黙を破り大復活！ 🔥",
            "NARUTO ED『バッチコイ!!!』でお馴染み\nデブパレードが帰ってきた！",
            "メンバー全員90kgオーバー！\nさらに増した音圧とポジティブ！",
            "8月19日 1stアルバム発売！\n『全ての武器をお箸に』予約受付中！",
            "最新情報はプロフのリンクから！\n#デブパレード #バッチコイ"
        ]
        # 背景画像（アーティスト写真やかっこいいライブ写真）
        image_candidates = ["member-group.jpg", "live-front.jpg", "member-closeup.jpg"]
        for name in image_candidates:
            path = os.path.join(GLOBAL_ASSETS_DIR, name)
            if os.path.exists(path):
                image_paths.append(path)
                
    elif mode == "custom":
        if custom_texts:
            texts = [t.strip().replace('\\n', '\n') for t in custom_texts.split(',')]
        else:
            texts = ["カスタムビデオ作成中", "テキストを入力してください\n(--texts 'あ,い,う')"]
        image_paths = [os.path.join(GLOBAL_ASSETS_DIR, "member-group.jpg")]

    # 画像アセットが見つからなかった場合、デフォルトの黒背景を使用
    if not image_paths:
        # assetsフォルダ全体の画像ファイルを検索
        if os.path.exists(GLOBAL_ASSETS_DIR):
            for file in os.listdir(GLOBAL_ASSETS_DIR):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_paths.append(os.path.join(GLOBAL_ASSETS_DIR, file))
                    break

    # それでも無い場合はダミー
    if not image_paths:
        dummy_bg = os.path.join(BASE_DIR, "temp_dummy_bg.jpg")
        Image.new('RGB', (1080, 1920), (20, 20, 20)).save(dummy_bg)
        image_paths.append(dummy_bg)

    print(f"--- 動画生成パラメータ ---")
    print(f"モード: {mode}")
    print(f"テキスト数: {len(texts)}")
    print(f"背景画像数: {len(image_paths)}")
    print(f"BGM音源: {audio_path}")
    print(f"出力ファイル: {final_output_path}")
    print(f"------------------------")

    # 3. 各素材クリップの組み立て
    duration_per_text = 3.5  # 1枚のテキスト表示時間（秒）
    call_to_action_duration = 3.5 # 最後のCTAスライド表示時間（秒）
    
    total_duration = len(texts) * duration_per_text + call_to_action_duration
    
    # 背景スライドショーの作成
    print("🎬 背景スライドショーを作成中...")
    processed_bg_images = []
    for img_path in image_paths:
        processed_bg_images.append(crop_and_resize_to_9_16(img_path))
    
    # 画像リストが足りない場合はループさせる
    bg_clips = []
    num_bg = len(processed_bg_images)
    time_accumulated = 0
    bg_duration = total_duration / num_bg if num_bg > 0 else total_duration
    
    for i, pil_img in enumerate(processed_bg_images):
        img_np = np.array(pil_img)
        # 各スライド用のImageClipを作成
        c = ImageClip(img_np).set_duration(bg_duration + 0.5) # フェードオーバーラップ用に少し長めに
        c = c.set_start(time_accumulated)
        if i > 0:
            c = c.crossfadein(0.5) # クロスフェードイン
        bg_clips.append(c)
        time_accumulated += bg_duration
        
    bg_composite = CompositeVideoClip(bg_clips, size=(1080, 1920)).set_duration(total_duration)

    # 字幕（テロップ）クリップの作成
    print("✍️ テロップと字幕を合成中...")
    text_clips = []
    
    for idx, text in enumerate(texts):
        start_t = idx * duration_per_text
        end_t = start_t + duration_per_text
        
        # 1行が長い場合は自動で適度な位置で改行する
        formatted_text = text
        if len(text) > 15 and '\n' not in text:
            # 12文字あたりで改行
            formatted_text = text[:12] + '\n' + text[12:]
            
        t_clip = create_text_clip_image(
            formatted_text, 
            font_size=64, 
            text_color=(255, 255, 255), 
            stroke_color=(227, 30, 36), # デブパレードレッドの境界線
            stroke_width=6,
            bg_box=True
        )
        t_clip = t_clip.set_start(start_t).set_end(end_t).set_position('center')
        
        # 微妙なフェードイン・フェードアウト
        t_clip = t_clip.crossfadein(0.3).crossfadeout(0.3)
        text_clips.append(t_clip)
        
    # 最後のスライド (コール・トゥ・アクション / チケットQRなど)
    cta_start = total_duration - call_to_action_duration
    cta_text = "🎫 詳細は公式サイトで！\n🔎 『デブパレード』で検索\n\n8.19 ALBUM RELEASE!\n全ての武器をお箸に"
    cta_clip = create_text_clip_image(
        cta_text, 
        font_size=56, 
        text_color=(255, 235, 59), # 黄色文字で目立たせる
        stroke_color=(0, 0, 0),
        stroke_width=6,
        bg_box=True
    )
    cta_clip = cta_clip.set_start(cta_start).set_end(total_duration).set_position('center')
    cta_clip = cta_clip.crossfadein(0.5)
    text_clips.append(cta_clip)

    # 4. 音声の設定
    final_video = CompositeVideoClip([bg_composite] + text_clips)
    
    if audio_path and os.path.exists(audio_path):
        print(f"🎵 BGMを合成中: {audio_path}")
        try:
            audio = AudioFileClip(audio_path)
            # 音声が短い場合はループ、長い場合はカット
            if audio.duration < total_duration:
                # ループ処理 (簡易的にconcatenate)
                loops = int(np.ceil(total_duration / audio.duration))
                audio = concatenate_videoclips([ImageClip(np.zeros((10,10,3))).set_audio(audio)] * loops).audio
            
            audio = audio.subclip(0, total_duration)
            # 最後はフェードアウト
            audio = audio.audio_fadeout(1.5)
            final_video = final_video.set_audio(audio)
        except Exception as e:
            print(f"⚠️ BGMの読み込みまたは合成に失敗しました: {e}")

    # 5. 書き出し
    print(f"🎥 動画ファイル書き出し開始: {final_output_path} (長さ: {total_duration:.1f}秒)...")
    try:
        final_video.write_videofile(
            final_output_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger='bar'
        )
        print(f"✨ 完了！動画が正常に作成されました: {final_output_path}")
    except Exception as e:
        print(f"❌ 動画の書き出しに失敗しました: {e}")
        print("ヒント: システムの ffmpeg が壊れているか、フォントが見つからない可能性があります。")
        raise e

    # 一時ファイルのクリーンアップ
    dummy_bg = os.path.join(BASE_DIR, "temp_dummy_bg.jpg")
    if os.path.exists(dummy_bg):
        os.remove(dummy_bg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Devparade Promo Video Generator")
    parser.add_argument("--mode", choices=["countdown", "album", "viral", "custom", "royal", "single0904"], default="countdown",
                        help="動画の生成モード (デフォルト: countdown)")
    parser.add_argument("--topic", help="viralモード用のお題 (例: 深夜のラーメン)")
    parser.add_argument("--days", type=int, help="countdownモードの残り日数 (指定しない場合は自動計算)")
    parser.add_argument("--texts", help="customモード用のカンマ区切りテキスト")
    parser.add_argument("--audio", help="使用するBGM音源 (MP3など) へのパス")
    parser.add_argument("--output", help="出力ファイル名 (e.g. countdown_30d.mp4)")

    args = parser.parse_args()
    build_promo_video(
        mode=args.mode,
        topic=args.topic,
        days=args.days,
        custom_texts=args.texts,
        audio_path=args.audio,
        output_filename=args.output
    )
