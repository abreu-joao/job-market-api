from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.services.job_service import get_total_jobs, get_jobs_by_location
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobCreate
from datetime import datetime

router = APIRouter()

@router.get("/jobs", response_model=List[JobResponse])
def read_jobs(db: Session = Depends(get_db)):
    
    jobs = db.query(Job).all()
    return jobs

@router.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    
    new_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        technology=job.technology,
        seniority=job.seniority,
        salary=job.salary,
        posted_at=datetime.utcnow()
    )
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    return new_job

@router.get("/jobs/stats")
def get_job_statistics(db: Session = Depends(get_db)):
    total = get_total_jobs(db)
    locations = get_jobs_by_location(db)
    
    return {
        "status": "success",
        "data": {
            "total_jobs": total,
            "jobs_by_location": locations
        }
    }