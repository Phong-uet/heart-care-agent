import uuid
import enum
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class HITLRequestType(str, enum.Enum):
    threshold_change = "threshold_change"
    medication_change = "medication_change"


class HITLStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class HITLApproval(Base):
    __tablename__ = "hitl_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patient_profiles.id"), nullable=False, index=True
    )
    request_type: Mapped[HITLRequestType] = mapped_column(
        Enum(HITLRequestType, name="hitl_request_type"), nullable=False
    )
    proposed_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    # ví dụ nội dung: {"stage1_systolic": 135, "stage1_diastolic": 85, "reason": "..."}

    status: Mapped[HITLStatus] = mapped_column(
        Enum(HITLStatus, name="hitl_status"), nullable=False, default=HITLStatus.pending
    )
    requested_by: Mapped[str] = mapped_column(String(50), nullable=False)
    # "agent" hoặc "doctor" — ai là người khởi tạo đề xuất

    reviewed_by_doctor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )