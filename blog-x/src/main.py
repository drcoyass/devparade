"""
COYASS Auto-Posting System - Main Entry Point
メインアプリケーション
"""

import os
import sys
import yaml
import asyncio
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.content.generator import ContentGenerator
from src.content.editor import ContentEditor
from src.publishers.note_publisher import NotePublisher
from src.publishers.x_publisher import XPublisher
from src.data.repository import Repository
from src.scheduler import PostScheduler

console = Console()

# ログ設定
def setup_logging(config: dict):
    log_config = config.get("logging", {})
    log_file = log_config.get("file", "logs/app.log")
    Path(log_file).parent.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_config.get("level", "INFO")),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """設定ファイルを読み込む"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def show_banner():
    """起動バナーを表示"""
    banner = """
╔══════════════════════════════════════════╗
║   🦷 COYASS Auto-Posting System 🎤     ║
║   歯科医師 × ラッパー × 自動投稿       ║
╚══════════════════════════════════════════╝
    """
    console.print(Panel(banner, style="bold cyan"))


async def run_scheduler(config: dict):
    """スケジューラモードで起動"""
    show_banner()
    console.print("[bold green]🟢 Starting scheduler mode...[/]")

    # コンポーネント初期化
    repo = Repository(config.get("database", {}).get("path", "data/coyass.db"))
    generator = ContentGenerator(config)
    editor = ContentEditor()

    note_pub = NotePublisher(config)
    x_pub = XPublisher(config)

    # Note: Playwrightの初期化
    if not config.get("app", {}).get("dry_run", True):
        await note_pub.initialize()
        await note_pub.login()
        x_pub.initialize()

    # スケジューラ
    scheduler = PostScheduler(config, generator, note_pub, x_pub, repo)
    scheduler.load_schedules()
    scheduler.start()

    # ジョブ一覧を表示
    jobs = scheduler.get_scheduled_jobs()
    table = Table(title="📅 Scheduled Jobs")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Next Run", style="yellow")
    for job in jobs:
        table.add_row(job["id"], job["name"], job["next_run"])
    console.print(table)

    console.print(f"\n[bold]Dry Run: {'✅ ON' if config.get('app', {}).get('dry_run') else '❌ OFF'}[/]")
    console.print("[dim]Press Ctrl+C to stop[/]\n")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
        await note_pub.close()
        console.print("[bold red]🔴 System stopped[/]")


async def generate_single(config: dict, platform: str, category: str):
    """単発でコンテンツを生成する（テスト用）"""
    show_banner()
    console.print(f"[bold]📝 Generating {platform} content (category: {category})[/]\n")

    generator = ContentGenerator(config)
    editor = ContentEditor()

    if platform == "note":
        article = generator.generate_note_article(category=category)
        if article:
            # 品質チェック
            quality = editor.check_quality(article["body"], platform="note")

            console.print(Panel(f"[bold]{article['title']}[/]", title="📝 Title"))
            console.print(f"\n{article['body'][:500]}...\n")
            console.print(f"[dim]({article['word_count']} chars, AI: {article['ai_provider']})[/]")
            console.print(f"\n🏷️ Tags: {article['hashtags']}")

            # 品質レポート
            console.print(f"\n📊 Quality Score: {quality['score']}/100")
            for issue in quality["issues"]:
                console.print(f"   {issue}")
        else:
            console.print("[red]❌ Generation failed[/]")

    elif platform == "x":
        post = generator.generate_x_post(category=category)
        if post:
            console.print(Panel(post["text"], title="🐦 X Post"))
            console.print(f"[dim]({len(post['text'])} chars, AI: {post['ai_provider']})[/]")
        else:
            console.print("[red]❌ Generation failed[/]")


def run_dashboard(config: dict):
    """ダッシュボードを起動"""
    from src.dashboard.app import create_app
    app = create_app(config)
    dash_config = config.get("dashboard", {})
    app.run(
        host=dash_config.get("host", "127.0.0.1"),
        port=dash_config.get("port", 5000),
        debug=dash_config.get("debug", False)
    )


def main():
    parser = argparse.ArgumentParser(description="COYASS Auto-Posting System")
    parser.add_argument("command", choices=["run", "generate", "dashboard", "init-db"],
                        help="Command to execute")
    parser.add_argument("--platform", choices=["note", "x"], default="note",
                        help="Target platform (for generate)")
    parser.add_argument("--category", default="dental_tips",
                        help="Content category (for generate)")
    parser.add_argument("--config", default="config/settings.yaml",
                        help="Path to config file")
    args = parser.parse_args()

    # 環境変数読み込み
    load_dotenv()

    # 設定読み込み
    config = load_config(args.config)
    setup_logging(config)

    if args.command == "run":
        asyncio.run(run_scheduler(config))
    elif args.command == "generate":
        asyncio.run(generate_single(config, args.platform, args.category))
    elif args.command == "dashboard":
        run_dashboard(config)
    elif args.command == "init-db":
        from src.data.models import init_db
        db_path = config.get("database", {}).get("path", "data/coyass.db")
        init_db(db_path)
        console.print(f"[green]✅ Database initialized: {db_path}[/]")


if __name__ == "__main__":
    main()
