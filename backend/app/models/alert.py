import uuid
import enum
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class AlertSeverity(str, enum.Enum):
    warning = "warning"
    urgent = "urgent"
    emergency = "emergency"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False, index=True
    )
    reading_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bp_readings.id"), nullable=True
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity"), nullable=False
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    is_acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    acknowledged_by_doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )