from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.services.job_service import (
    get_total_jobs, 
    get_jobs_by_seniority, 
    get_top_companies, 
    get_top_technologies,
    get_top_locations,
    get_remote_percentage,
    get_junior_friendly_companies
)
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobCreate

router = APIRouter()

@router.get("/jobs", response_model=List[JobResponse])
def read_jobs(
    tech: Optional[str] = Query(None, description="Filter by technology (ex: Python)"),
    seniority: Optional[str] = Query(None, description="Filter by seniority (ex: Junior)"),
    location: Optional[str] = Query(None, description="Filter by location (ex: Remote)"),
    title: Optional[str] = Query(None, description="Filter by job title (ex: Engineer)"),
    company: Optional[str] = Query(None, description="Filter by company (ex: Google)"),
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    
    if tech:
        query = query.filter(Job.technology.ilike(f"%{tech}%"))
    if seniority:
        query = query.filter(Job.seniority.ilike(f"%{seniority}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
        
    return query.all()

@router.get("/jobs/stats")
def get_job_statistics(db: Session = Depends(get_db)):
    return {
        "status": "success",
        "data": {
            "overview": {
                "total_jobs": get_total_jobs(db),
                "remote_work_metrics": get_remote_percentage(db)
            },
            "market_distribution": {
                "jobs_by_seniority": get_jobs_by_seniority(db),
                "top_10_locations": get_top_locations(db, limit=10),
            },
            "companies": {
                "top_5_hiring_companies": get_top_companies(db, limit=5),
                "top_5_junior_friendly": get_junior_friendly_companies(db, limit=5)
            },
            "technologies": {
                "top_10_overall": get_top_technologies(db, limit=10),
                "top_5_for_remote": get_top_technologies(db, limit=5, remote_only=True)
            }
        }
    }