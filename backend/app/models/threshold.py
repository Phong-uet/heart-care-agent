import uuid
from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Threshold(Base):
    __tablename__ = "thresholds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False, index=True
    )
    set_by_doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Ngưỡng tâm thu/tâm trương cho từng mức phân loại
    stage1_systolic: Mapped[int] = mapped_column(Integer, nullable=False, default=130)
    stage1_diastolic: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    stage2_systolic: Mapped[int] = mapped_column(Integer, nullable=False, default=140)
    stage2_diastolic: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    emergency_systolic: Mapped[int] = mapped_column(Integer, nullable=False, default=180)
    emergency_diastolic: Mapped[int] = mapped_column(Integer, nullable=False, default=120)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )