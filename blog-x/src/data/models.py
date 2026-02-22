"""
COYASS Auto-Posting System - Database Models
SQLAlchemy ORM models for content, posts, and analytics.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, Enum,
    create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

Base = declarative_base()


class ContentCategory(enum.Enum):
    """コンテンツカテゴリ"""
    DENTAL_TIPS = "dental_tips"
    MUSIC_REVIEW = "music_review"
    FOOD_HEALTH = "food_health"
    CAREER = "career"
    PARENTING = "parenting"
    INDUSTRY = "industry"
    DAILY_DOC = "daily_doc"


class Platform(enum.Enum):
    """投稿プラットフォーム"""
    NOTE = "note"
    X = "x"


class PostStatus(enum.Enum):
    """投稿ステータス"""
    QUEUED = "queued"          # 投稿キューに入っている
    GENERATING = "generating"  # AI生成中
    REVIEW = "review"          # レビュー待ち
    APPROVED = "approved"      # 承認済み
    PUBLISHING = "publishing"  # 投稿中
    PUBLISHED = "published"    # 投稿完了
    FAILED = "failed"          # 投稿失敗
    DRAFT = "draft"            # 下書き保存


class Content(Base):
    """生成されたコンテンツ"""
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    summary = Column(Text)  # X投稿用の要約
    hashtags = Column(Text)  # カンマ区切り
    image_path = Column(String(500))
    ai_provider = Column(String(20))  # "openai" or "gemini"
    ai_model = Column(String(50))
    word_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title[:30]}...', category='{self.category}')>"


class Post(Base):
    """投稿レコード"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, nullable=False)
    platform = Column(String(10), nullable=False)  # "note" or "x"
    status = Column(String(20), default="queued")
    scheduled_at = Column(DateTime)
    published_at = Column(DateTime)
    platform_post_id = Column(String(200))  # noteの記事URLやXのツイートID
    platform_url = Column(String(500))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Post(id={self.id}, platform='{self.platform}', status='{self.status}')>"


class Analytics(Base):
    """分析データ"""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, nullable=False)
    platform = Column(String(10), nullable=False)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)  # X のみ
    comments = Column(Integer, default=0)
    followers_at_time = Column(Integer)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class InputData(Base):
    """COYASSからの手動入力データ"""
    __tablename__ = "input_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    data_type = Column(String(50))  # "memo", "photo", "music", "meal"
    title = Column(String(200))
    body = Column(Text)
    image_path = Column(String(500))
    used = Column(Boolean, default=False)  # コンテンツ生成に使用済みフラグ
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db(db_path: str = "data/coyass.db"):
    """データベースを初期化する"""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session


if __name__ == "__main__":
    engine, Session = init_db()
    print("✅ Database initialized successfully!")
