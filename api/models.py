import os
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/celery_results.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class JobResult(Base):
    """ジョブ実行結果を保存するテーブル。"""

    __tablename__ = "job_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(155), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50))
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )


def get_job_result(task_id: str) -> JobResult | None:
    """task_idでジョブ結果を取得する。"""
    with Session(engine) as session:
        return session.query(JobResult).filter_by(task_id=task_id).first()
