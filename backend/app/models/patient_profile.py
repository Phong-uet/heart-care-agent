import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    medical_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )