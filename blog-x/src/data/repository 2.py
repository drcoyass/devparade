"""
COYASS Auto-Posting System - Data Repository
Database access layer for CRUD operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import Content, Post, Analytics, InputData, init_db


class Repository:
    """データアクセスリポジトリ"""

    def __init__(self, db_path: str = "data/coyass.db"):
        self.engine, self.SessionClass = init_db(db_path)

    def get_session(self) -> Session:
        return self.SessionClass()

    # === Content ===
    def save_content(self, content: Content) -> Content:
        with self.get_session() as session:
            session.add(content)
            session.commit()
            session.refresh(content)
            return content

    def get_content(self, content_id: int) -> Optional[Content]:
        with self.get_session() as session:
            return session.query(Content).filter_by(id=content_id).first()

    def get_unused_content(self, category: str = None, platform: str = None) -> List[Content]:
        """まだ投稿に使用されていないコンテンツを取得"""
        with self.get_session() as session:
            query = session.query(Content)
            if category:
                query = query.filter(Content.category == category)
            # 既にPostと紐づいているcontent_idを除外
            posted_ids = [p.content_id for p in session.query(Post.content_id).all()]
            if posted_ids:
                query = query.filter(~Content.id.in_(posted_ids))
            return query.order_by(Content.created_at.desc()).all()

    # === Post ===
    def create_post(self, content_id: int, platform: str, scheduled_at: datetime = None) -> Post:
        with self.get_session() as session:
            post = Post(
                content_id=content_id,
                platform=platform,
                status="queued",
                scheduled_at=scheduled_at or datetime.utcnow()
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            return post

    def update_post_status(self, post_id: int, status: str, **kwargs) -> Post:
        with self.get_session() as session:
            post = session.query(Post).filter_by(id=post_id).first()
            if post:
                post.status = status
                post.updated_at = datetime.utcnow()
                for key, value in kwargs.items():
                    if hasattr(post, key):
                        setattr(post, key, value)
                session.commit()
                session.refresh(post)
            return post

    def get_pending_posts(self, platform: str = None) -> List[Post]:
        """キューに入っている投稿を取得"""
        with self.get_session() as session:
            query = session.query(Post).filter(
                Post.status.in_(["queued", "approved"]),
                Post.scheduled_at <= datetime.utcnow()
            )
            if platform:
                query = query.filter(Post.platform == platform)
            return query.order_by(Post.scheduled_at).all()

    def get_recent_posts(self, limit: int = 50, platform: str = None) -> List[Post]:
        """最近の投稿を取得"""
        with self.get_session() as session:
            query = session.query(Post)
            if platform:
                query = query.filter(Post.platform == platform)
            return query.order_by(Post.created_at.desc()).limit(limit).all()

    def get_today_post_count(self, platform: str) -> int:
        """今日の投稿数を取得"""
        with self.get_session() as session:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            return session.query(Post).filter(
                Post.platform == platform,
                Post.status == "published",
                Post.published_at >= today
            ).count()

    # === Input Data ===
    def save_input(self, category: str, body: str, data_type: str = "memo",
                   title: str = None, image_path: str = None) -> InputData:
        with self.get_session() as session:
            input_data = InputData(
                category=category,
                data_type=data_type,
                title=title,
                body=body,
                image_path=image_path
            )
            session.add(input_data)
            session.commit()
            session.refresh(input_data)
            return input_data

    def get_unused_inputs(self, category: str = None) -> List[InputData]:
        with self.get_session() as session:
            query = session.query(InputData).filter_by(used=False)
            if category:
                query = query.filter(InputData.category == category)
            return query.order_by(InputData.created_at.desc()).all()

    # === Analytics ===
    def get_stats_summary(self, days: int = 30) -> dict:
        """指定期間の統計サマリーを取得"""
        with self.get_session() as session:
            since = datetime.utcnow() - timedelta(days=days)
            posts = session.query(Post).filter(
                Post.status == "published",
                Post.published_at >= since
            ).all()
            return {
                "total_posts": len(posts),
                "note_posts": sum(1 for p in posts if p.platform == "note"),
                "x_posts": sum(1 for p in posts if p.platform == "x"),
                "period_days": days
            }
