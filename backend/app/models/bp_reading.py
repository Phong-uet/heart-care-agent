import uuid
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class BPReading(Base):
    __tablename__ = "bp_readings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False, index=True
    )
    systolic: Mapped[int] = mapped_column(Integer, nullable=False)
    diastolic: Mapped[int] = mapped_column(Integer, nullable=False)
    heart_rate: Mapped[int] = mapped_column(Integer, nullable=False)

    # Bối cảnh đo: tư thế, có vận động trước đó, có nói chuyện khi đo...
    context: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )