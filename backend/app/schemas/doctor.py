import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.hitl_approval import HITLRequestType, HITLStatus


class PatientSummary(BaseModel):
    patient_id: uuid.UUID
    full_name: str
    email: str
    latest_systolic: int | None = None
    latest_diastolic: int | None = None
    latest_measured_at: datetime | None = None


class ThresholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stage1_systolic: int
    stage1_diastolic: int
    stage2_systolic: int
    stage2_diastolic: int
    emergency_systolic: int
    emergency_diastolic: int
    set_by_doctor_id: uuid.UUID
    created_at: datetime


class ThresholdProposal(BaseModel):
    stage1_systolic: int = Field(ge=80, le=300)
    stage1_diastolic: int = Field(ge=40, le=200)
    stage2_systolic: int = Field(ge=80, le=300)
    stage2_diastolic: int = Field(ge=40, le=200)
    emergency_systolic: int = Field(ge=80, le=300)
    emergency_diastolic: int = Field(ge=40, le=200)
    reason: str = Field(min_length=3, max_length=500)

    @model_validator(mode="after")
    def check_order(self):
        if not (self.stage1_systolic < self.stage2_systolic < self.emergency_systolic):
            raise ValueError("Ngưỡng tâm thu phải tăng dần: độ 1 < độ 2 < cấp cứu")
        if not (self.stage1_diastolic < self.stage2_diastolic < self.emergency_diastolic):
            raise ValueError("Ngưỡng tâm trương phải tăng dần: độ 1 < độ 2 < cấp cứu")
        return self


class HITLOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: uuid.UUID
    request_type: HITLRequestType
    proposed_payload: dict
    status: HITLStatus
    requested_by: str
    created_at: datetime
    reviewed_at: datetime | None = None