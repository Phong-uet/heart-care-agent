from fastapi import FastAPI

import app.models  # noqa: F401
from app.api import auth, doctor, readings

app = FastAPI(title="BP Agent System")

app.include_router(auth.router)
app.include_router(readings.router)
app.include_router(doctor.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}