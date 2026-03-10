from fastapi import FastAPI
from app.api.routes import jobs

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Job Market API running"}

app.include_router(jobs.router)