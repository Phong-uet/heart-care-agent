from fastapi import FastAPI

app = FastAPI(title="BP Agent System")

@app.get("/health")
def health_check():
    return {"status": "ok"}