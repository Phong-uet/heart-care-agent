from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.db.session import get_db
from app.models.bp_reading import BPReading
from app.models.patient_profile import PatientProfile
from app.schemas.reading import ReadingCreate, ReadingOut, TrendPoint

router = APIRouter(prefix="/readings", tags=["readings"])


@router.post("", response_model=ReadingOut, status_code=status.HTTP_201_CREATED)
def create_reading(
    data: ReadingCreate,
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    reading = BPReading(
        patient_id=patient.id,
        systolic=data.systolic,
        diastolic=data.diastolic,
        heart_rate=data.heart_rate,
        context=data.context,
        measured_at=data.measured_at or datetime.now(timezone.utc),
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


@router.get("", response_model=list[ReadingOut])
def list_readings(
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    stmt = select(BPReading).where(BPReading.patient_id == patient.id)
    if start:
        stmt = stmt.where(BPReading.measured_at >= start)
    if end:
        stmt = stmt.where(BPReading.measured_at <= end)
    stmt = stmt.order_by(BPReading.measured_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.get("/trend", response_model=list[TrendPoint])
def reading_trend(
    days: int = Query(7, ge=1, le=90),
    patient: PatientProfile = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    day = func.date(BPReading.measured_at).label("day")
    stmt = (
        select(
            day,
            func.avg(BPReading.systolic),
            func.avg(BPReading.diastolic),
            func.avg(BPReading.heart_rate),
            func.count(),
        )
        .where(BPReading.patient_id == patient.id, BPReading.measured_at >= since)
        .group_by(day)
        .order_by(day)
    )
    rows = db.execute(stmt).all()
    return [
        TrendPoint(
            day=r[0],
            avg_systolic=round(float(r[1]), 1),
            avg_diastolic=round(float(r[2]), 1),
            avg_heart_rate=round(float(r[3]), 1),
            count=r[4],
        )
        for r in rows
    ]