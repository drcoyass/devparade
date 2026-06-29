"""
COYASS Auto-Posting System - Dashboard
Flask製の管理ダッシュボード
"""

import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def create_app(config: dict = None) -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "coyass-dashboard-secret"

    # Repository（遅延初期化）
    repo = None

    def get_repo():
        nonlocal repo
        if repo is None:
            from src.data.repository import Repository
            db_path = (config or {}).get("database", {}).get("path", "data/coyass.db")
            repo = Repository(db_path)
        return repo

    @app.route("/")
    def index():
        r = get_repo()
        stats = r.get_stats_summary(30)
        recent_posts = r.get_recent_posts(limit=20)
        return render_template("index.html",
                               stats=stats,
                               recent_posts=recent_posts,
                               now=datetime.now())

    @app.route("/api/stats")
    def api_stats():
        r = get_repo()
        return jsonify(r.get_stats_summary(30))

    @app.route("/api/posts")
    def api_posts():
        r = get_repo()
        platform = request.args.get("platform")
        posts = r.get_recent_posts(limit=50, platform=platform)
        return jsonify([{
            "id": p.id,
            "platform": p.platform,
            "status": p.status,
            "scheduled_at": str(p.scheduled_at) if p.scheduled_at else None,
            "published_at": str(p.published_at) if p.published_at else None,
            "url": p.platform_url
        } for p in posts])

    @app.route("/input", methods=["GET", "POST"])
    def input_data():
        r = get_repo()
        if request.method == "POST":
            r.save_input(
                category=request.form.get("category", "daily_doc"),
                body=request.form.get("body", ""),
                data_type=request.form.get("data_type", "memo"),
                title=request.form.get("title")
            )
            return redirect(url_for("input_data"))
        inputs = r.get_unused_inputs()
        return render_template("input.html", inputs=inputs)

    return app
