import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class MeasurementQualityFlag(Base):
    __tablename__ = "measurement_quality_flags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reading_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bp_readings.id"), nullable=False, index=True
    )
    flag_code: Mapped[str] = mapped_column(String(100), nullable=False)
    # ví dụ flag_code: "posture_invalid", "talked_during_measurement",
    # "no_rest_before_measurement", "abnormal_deviation_from_history"
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )