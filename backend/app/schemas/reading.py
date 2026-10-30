import uuid
from datetime import date, datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ReadingCreate(BaseModel):
    systolic: int = Field(ge=50, le=300)
    diastolic: int = Field(ge=30, le=200)
    heart_rate: int = Field(ge=20, le=250)
    # Bối cảnh đo: posture, arm_at_heart_level, talked_during, rested_before_minutes...
    context: dict = Field(default_factory=dict)
    measured_at: datetime | None = None

    @field_validator("measured_at")
    @classmethod
    def normalize_measured_at(cls, v: datetime | None):
        if v is None:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("Thời điểm đo không được ở tương lai")
        return v

    @model_validator(mode="after")
    def check_pressure_order(self):
        if self.systolic <= self.diastolic:
            raise ValueError("Huyết áp tâm thu phải lớn hơn tâm trương")
        return self


class ReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    systolic: int
    diastolic: int
    heart_rate: int
    context: dict
    measured_at: datetime


class TrendPoint(BaseModel):
    day: date
    avg_systolic: float
    avg_diastolic: float
    avg_heart_rate: float
    count: int