import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.session import get_db
from app.models.bp_reading import BPReading
from app.models.hitl_approval import HITLApproval, HITLRequestType, HITLStatus
from app.models.patient_profile import PatientProfile
from app.models.threshold import Threshold
from app.models.user import User, UserRole
from app.schemas.doctor import (
    HITLOut,
    PatientSummary,
    ThresholdOut,
    ThresholdProposal,
)
from app.schemas.reading import ReadingOut

router = APIRouter(prefix="/doctor", tags=["doctor"])

doctor_only = require_role(UserRole.doctor)


def get_owned_patient(patient_id: uuid.UUID, doctor: User, db: Session) -> PatientProfile:
    """Chỉ trả về bệnh nhân do chính bác sĩ này phụ trách."""
    patient = db.get(PatientProfile, patient_id)
    if patient is None or patient.assigned_doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bệnh nhân",
        )
    return patient


def get_active_threshold(db: Session, patient_id: uuid.UUID) -> Threshold | None:
    return db.scalar(
        select(Threshold)
        .where(Threshold.patient_id == patient_id, Threshold.is_active.is_(True))
        .order_by(Threshold.created_at.desc())
        .limit(1)
    )


@router.get("/patients", response_model=list[PatientSummary])
def list_patients(
    doctor: User = Depends(doctor_only),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(PatientProfile, User)
        .join(User, User.id == PatientProfile.user_id)
        .where(PatientProfile.assigned_doctor_id == doctor.id)
        .order_by(User.full_name)
    ).all()

    result = []
    for profile, user in rows:
        latest = db.scalar(
            select(BPReading)
            .where(BPReading.patient_id == profile.id)
            .order_by(BPReading.measured_at.desc())
            .limit(1)
        )
        result.append(
            PatientSummary(
                patient_id=profile.id,
                full_name=user.full_name,
                email=user.email,
                latest_systolic=latest.systolic if latest else None,
                latest_diastolic=latest.diastolic if latest else None,
                latest_measured_at=latest.measured_at if latest else None,
            )
        )
    return result


@router.get("/patients/{patient_id}/readings", response_model=list[ReadingOut])
def patient_readings(
    patient_id: uuid.UUID,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    doctor: User = Depends(doctor_only),
    db: Session = Depends(get_db),
):
    patient = get_owned_patient(patient_id, doctor, db)
    stmt = select(BPReading).where(BPReading.patient_id == patient.id)
    if start:
        stmt = stmt.where(BPReading.measured_at >= start)
    if end:
        stmt = stmt.where(BPReading.measured_at <= end)
    stmt = stmt.order_by(BPReading.measured_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.get("/patients/{patient_id}/threshold", response_model=ThresholdOut)
def patient_threshold(
    patient_id: uuid.UUID,
    doctor: User = Depends(doctor_only),
    db: Session = Depends(get_db),
):
    patient = get_owned_patient(patient_id, doctor, db)
    threshold = get_active_threshold(db, patient.id)
    if threshold is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bệnh nhân chưa có ngưỡng nào đang áp dụng",
        )
    return threshold


@router.post(
    "/patients/{patient_id}/thresholds/propose",
    response_model=HITLOut,
    status_code=status.HTTP_201_CREATED,
)
def propose_threshold(
    patient_id: uuid.UUID,
    data: ThresholdProposal,
    doctor: User = Depends(doctor_only),
    db: Session = Depends(get_db),
):
    patient = get_owned_patient(patient_id, doctor, db)
    request = HITLApproval(
        patient_id=patient.id,
        request_type=HITLRequestType.threshold_change,
        proposed_payload=data.model_dump(),
        status=HITLStatus.pending,
        requested_by="doctor",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/hitl", response_model=list[HITLOut])
def list_hitl_requests(
    status_filter: HITLStatus | None = Query(HITLStatus.pending, alias="status"),
    doctor: User = Depends(doctor_only),
    db: Session = Depends(get_db),
):
    stmt = (
        select(HITLApproval)
        .join(PatientProfile, PatientProfile.id == HITLApproval.patient_id)
        .where(PatientProfile.assigned_doctor_id == doctor.id)
    )
    if status_filter:
        stmt = stmt.where(HITLApproval.status == status_filter)
    stmt = stmt.order_by(HITLApproval.created_at.desc())
    return db.scalars(stmt).all()


def load_pending_request(request_id: uuid.UUID, doctor: User, db: Session) -> HITLApproval:
    request = db.get(HITLApproval, request_id, with_for_update=True)
    if request is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy yêu cầu")

    patient = db.get(PatientProfile, request.patient_id)
    if patient is None or patient.assigned_doctor_id != doctor.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy yêu cầu")

    if request.status != HITLStatus.pending:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Yêu cầu này đã được xử lý")
    return request


@router.post("/hitl/{request_id}/approve", response_model=HITLOut)
def approve_request(
    request_id: uuid.UUID,
    doctor: User = Depends(doctor_only),
    db: Session = Depends(get_db),
):
    request = load_pending_request(request_id, doctor, db)

    if request.request_type != HITLRequestType.threshold_change:
        raise HTTPException(
            status.HTTP_501_NOT_IMPLEMENTED, "Loại yêu cầu này chưa được hỗ trợ"
        )

    p = request.proposed_payload

    # Ngưỡng cũ không bị sửa hay xóa, chỉ chuyển sang không còn hiệu lực
    old_thresholds = db.scalars(
        select(Threshold).where(
            Threshold.patient_id == request.patient_id,
            Threshold.is_active.is_(True),
        )
    ).all()
    for old in old_thresholds:
        old.is_active = False

    db.add(
        Threshold(
            patient_id=request.patient_id,
            set_by_doctor_id=doctor.id,
            is_active=True,
            stage1_systolic=p["stage1_systolic"],
            stage1_diastolic=p["stage1_diastolic"],
            stage2_systolic=p["stage2_systolic"],
            stage2_diastolic=p["stage2_diastolic"],
            emergency_systolic=p["emergency_systolic"],
            emergency_diastolic=p["emergency_diastolic"],
        )
    )

    request.status = HITLStatus.approved
    request.reviewed_by_doctor_id = doctor.id
    request.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return request


@router.post("/hitl/{request_id}/reject", response_model=HITLOut)
def reject_request(
    request_id: uuid.UUID,
    doctor: User = Depends(doctor_only),
    db: Session = Depends(get_db),
):
    request = load_pending_request(request_id, doctor, db)
    request.status = HITLStatus.rejected
    request.reviewed_by_doctor_id = doctor.id
    request.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return request