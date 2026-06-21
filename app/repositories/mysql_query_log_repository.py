from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from app.models.query_log import QueryLog


class Base(DeclarativeBase):
    pass


class QueryLogRecord(Base):
    __tablename__ = "query_logs"

    query_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_query: Mapped[str] = mapped_column(Text)
    detected_language: Mapped[str] = mapped_column(String(16))
    rewritten_query: Mapped[str] = mapped_column(Text)
    retrieval_routes: Mapped[str] = mapped_column(Text)
    retrieved_doc_ids: Mapped[str] = mapped_column(Text)
    final_answer: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[int] = mapped_column(Integer)
    llm_model: Mapped[str] = mapped_column(String(128))
    embedding_model: Mapped[str] = mapped_column(String(128))
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class MySQLQueryLogRepository:
    def __init__(self, mysql_url: str) -> None:
        self._engine = create_engine(mysql_url, future=True)
        Base.metadata.create_all(self._engine)

    @property
    def engine(self):
        return self._engine

    def save(self, query_log: QueryLog) -> None:
        with Session(self._engine) as session:
            session.merge(
                QueryLogRecord(
                    query_id=query_log.query_id,
                    user_query=query_log.user_query,
                    detected_language=query_log.detected_language,
                    rewritten_query=query_log.rewritten_query,
                    retrieval_routes=",".join(query_log.retrieval_routes),
                    retrieved_doc_ids=",".join(query_log.retrieved_doc_ids),
                    final_answer=query_log.final_answer,
                    latency_ms=query_log.latency_ms,
                    llm_model=query_log.llm_model,
                    embedding_model=query_log.embedding_model,
                    cache_hit=query_log.cache_hit,
                    created_at=query_log.created_at,
                )
            )
            session.commit()

    def list_recent(self, limit: int = 20) -> list[QueryLog]:
        with Session(self._engine) as session:
            stmt = select(QueryLogRecord).order_by(QueryLogRecord.created_at.desc()).limit(limit)
            rows = session.execute(stmt).scalars().all()
            return [
                QueryLog(
                    query_id=row.query_id,
                    user_query=row.user_query,
                    detected_language=row.detected_language,
                    rewritten_query=row.rewritten_query,
                    retrieval_routes=[item for item in row.retrieval_routes.split(",") if item],
                    retrieved_doc_ids=[item for item in row.retrieved_doc_ids.split(",") if item],
                    final_answer=row.final_answer,
                    latency_ms=row.latency_ms,
                    llm_model=row.llm_model,
                    embedding_model=row.embedding_model,
                    cache_hit=row.cache_hit,
                    created_at=row.created_at,
                )
                for row in rows
            ]

    def stats(self) -> dict[str, int]:
        with Session(self._engine) as session:
            count = session.query(QueryLogRecord).count()
            return {"total_queries": int(count)}
