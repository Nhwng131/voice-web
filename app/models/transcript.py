from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, Numeric, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base


class Transcript(Base):
    __tablename__ = "transcript"
    __table_args__ = (
        Index("ix_transcript_file_start", "file_id", "start_ms"),
        Index("ix_transcript_file_speaker_start", "file_id", "speaker_label", "start_ms"),
        Index("uq_transcript_file_start_order", "file_id", "start_ms", "order", unique=True),
    )

    segment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("file_ingest.file_id", ondelete="CASCADE"), nullable=False, index=True
    )

    start_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    end_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    # "order" là tên cột trong DB; dùng key Python là order_
    order_: Mapped[int | None] = mapped_column("order", Integer, nullable=True)

    speaker_label: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    is_overlap: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    file = relationship("FileIngest", back_populates="transcripts")
