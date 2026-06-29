#!/usr/bin/env python3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
VIDEO_PATH = os.path.join(PROJECT_DIR, "video-automation", "output", "countdown_promo.mp4")
OUTPUT_IMG = os.path.join(PROJECT_DIR, "video-automation", "output", "verify_frame.png")
ARTIFACT_DIR = "/Users/coyass/.gemini/antigravity-ide/brain/ff6bebce-7688-4d50-bf79-497dee290386"
ARTIFACT_IMG = os.path.join(ARTIFACT_DIR, "verify_frame.png")

# moviepy仮想環境のPythonを使う
sys.path.append(os.path.join(PROJECT_DIR, "video-automation"))

def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video file not found at {VIDEO_PATH}")
        sys.exit(1)
        
    try:
        from moviepy.editor import VideoFileClip
        print(f"Loading video: {VIDEO_PATH}")
        clip = VideoFileClip(VIDEO_PATH)
        
        # 5秒目（2つ目のテキストが表示されているはずの時間）のフレームを保存
        print(f"Extracting frame at t=5.0s...")
        clip.save_frame(OUTPUT_IMG, t=5.0)
        print(f"✅ Frame saved to {OUTPUT_IMG}")
        
        # 成果物ディレクトリにコピーしてユーザーに表示できるようにする
        import shutil
        os.makedirs(ARTIFACT_DIR, exist_ok=True)
        shutil.copy2(OUTPUT_IMG, ARTIFACT_IMG)
        print(f"✅ Copied to artifact: {ARTIFACT_IMG}")
        
    except Exception as e:
        print(f"❌ Error extracting frame: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
