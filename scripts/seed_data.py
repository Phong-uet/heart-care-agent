import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(BACKEND_DIR))

from passlib.hash import bcrypt

import app.models
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.patient_profile import PatientProfile
from app.models.threshold import Threshold
from app.models.bp_reading import BPReading
from app.models.bp_classification import BPClassification, ClassificationLevel


def run():
    db = SessionLocal()
    try:
        # 1. Tạo bác sĩ
        doctor = User(
            email="doctor@example.com",
            hashed_password=bcrypt.hash("doctor123"),
            full_name="BS. Nguyễn Văn A",
            role=UserRole.doctor,
        )
        db.add(doctor)
        db.flush()  # để lấy được doctor.id trước khi commit

        # 2. Tạo bệnh nhân
        patient_user = User(
            email="patient@example.com",
            hashed_password=bcrypt.hash("patient123"),
            full_name="Trần Thị B",
            role=UserRole.patient,
        )
        db.add(patient_user)
        db.flush()

        patient_profile = PatientProfile(
            user_id=patient_user.id,
            assigned_doctor_id=doctor.id,
        )
        db.add(patient_profile)
        db.flush()

        # 3. Tạo threshold mặc định cho bệnh nhân, do bác sĩ thiết lập
        threshold = Threshold(
            patient_id=patient_profile.id,
            set_by_doctor_id=doctor.id,
            is_active=True,
        )
        db.add(threshold)
        db.flush()

        # 4. Tạo vài phép đo mẫu (3 ngày gần nhất)
        sample_readings = [
            {"systolic": 118, "diastolic": 76, "heart_rate": 72, "days_ago": 2},
            {"systolic": 132, "diastolic": 84, "heart_rate": 78, "days_ago": 1},
            {"systolic": 145, "diastolic": 92, "heart_rate": 80, "days_ago": 0},
        ]

        for sample in sample_readings:
            measured_at = datetime.now(timezone.utc) - timedelta(days=sample["days_ago"])
            reading = BPReading(
                patient_id=patient_profile.id,
                systolic=sample["systolic"],
                diastolic=sample["diastolic"],
                heart_rate=sample["heart_rate"],
                context={
                    "posture": "sitting",
                    "arm_at_heart_level": True,
                    "talked_during": False,
                    "rested_before_minutes": 5,
                },
                measured_at=measured_at,
            )
            db.add(reading)
            db.flush()

            # phân loại thủ công đơn giản cho dữ liệu seed (logic thật sẽ ở Giai đoạn 4)
            if sample["systolic"] >= 140 or sample["diastolic"] >= 90:
                level = ClassificationLevel.stage2
            elif sample["systolic"] >= 130 or sample["diastolic"] >= 80:
                level = ClassificationLevel.stage1
            else:
                level = ClassificationLevel.normal

            classification = BPClassification(
                reading_id=reading.id,
                threshold_id=threshold.id,
                level=level,
                is_emergency=False,
            )
            db.add(classification)

        db.commit()
        print("Seed data đã được tạo thành công.")
        print(f"Bác sĩ: doctor@example.com / doctor123")
        print(f"Bệnh nhân: patient@example.com / patient123")

    except Exception as e:
        db.rollback()
        print(f"Lỗi khi seed data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()