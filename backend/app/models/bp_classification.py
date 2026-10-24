import uuid
import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class ClassificationLevel(str, enum.Enum):
    normal = "normal"
    elevated = "elevated"
    stage1 = "stage1"
    stage2 = "stage2"
    hypertensive_crisis = "hypertensive_crisis"


class BPClassification(Base):
    __tablename__ = "bp_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reading_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bp_readings.id"), unique=True, nullable=False
    )
    threshold_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("thresholds.id"), nullable=False
    )
    level: Mapped[ClassificationLevel] = mapped_column(
        Enum(ClassificationLevel, name="classification_level"), nullable=False
    )
    is_emergency: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )