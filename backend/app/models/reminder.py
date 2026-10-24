import uuid
import enum
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class ReminderType(str, enum.Enum):
    measurement = "measurement"
    medication = "medication"


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False, index=True
    )
    reminder_type: Mapped[ReminderType] = mapped_column(
        Enum(ReminderType, name="reminder_type"), nullable=False
    )
    # "08:00", "20:00" — giờ nhắc trong ngày, lặp lại hàng ngày
    scheduled_time: Mapped[str] = mapped_column(String(5), nullable=False)

    related_medication_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("medications.id"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )