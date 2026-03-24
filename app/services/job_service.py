from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.job import Job

def get_total_jobs(db: Session) -> int:
    return db.query(Job).count()

def get_jobs_by_seniority(db: Session) -> dict:
    result = db.query(Job.seniority, func.count(Job.id))\
               .group_by(Job.seniority)\
               .order_by(desc(func.count(Job.id)))\
               .all()
    return {row[0] if row[0] else "Not Specified": row[1] for row in result}

def get_top_companies(db: Session, limit: int = 5) -> dict:
    result = db.query(Job.company, func.count(Job.id))\
               .group_by(Job.company)\
               .order_by(desc(func.count(Job.id)))\
               .limit(limit).all()
    return {row[0]: row[1] for row in result}

def get_top_technologies(db: Session, limit: int = 10, remote_only: bool = False) -> dict:
    query = db.query(Job.technology)
    if remote_only:
        query = query.filter(Job.location.ilike('%remote%'))
        
    all_techs = query.all()
    tech_counter = {}
    
    for (tech_str,) in all_techs:
        if tech_str and tech_str != "Not Specified":
            techs = [t.strip() for t in tech_str.split(',')]
            for t in techs:
                tech_counter[t] = tech_counter.get(t, 0) + 1
                
    top_techs = dict(sorted(tech_counter.items(), key=lambda item: item[1], reverse=True)[:limit])
    return top_techs

def get_top_locations(db: Session, limit: int = 10) -> dict:
    result = db.query(Job.location, func.count(Job.id))\
               .group_by(Job.location)\
               .order_by(desc(func.count(Job.id)))\
               .limit(limit).all()
    return {row[0]: row[1] for row in result if row[0]}

def get_remote_percentage(db: Session) -> dict:
    total = db.query(Job).count()
    if total == 0:
        return {"remote": 0, "on_site": 0, "remote_percentage": "0%"}
    
    remote_count = db.query(Job).filter(Job.location.ilike('%remote%')).count()
    on_site_count = total - remote_count
    percentage = round((remote_count / total) * 100, 1)
    
    return {
        "remote_jobs": remote_count,
        "on_site_jobs": on_site_count,
        "remote_percentage": f"{percentage}%"
    }

def get_junior_friendly_companies(db: Session, limit: int = 5) -> dict:
    result = db.query(Job.company, func.count(Job.id))\
               .filter(Job.seniority.ilike('%junior%') | Job.seniority.ilike('%entry%'))\
               .group_by(Job.company)\
               .order_by(desc(func.count(Job.id)))\
               .limit(limit).all()
    return {row[0]: row[1] for row in result}