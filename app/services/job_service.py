from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.job import Job

def get_total_jobs(db: Session) -> int:
    """Retorna o número total de vagas no banco de dados."""
    return db.query(Job).count()

def get_jobs_by_location(db: Session) -> list:
    """Retorna a contagem de vagas agrupadas por localização."""
    result = db.query(Job.location, func.count(Job.id).label('total')).group_by(Job.location).all()
    
    # Formata o resultado para uma lista de dicionários
    return [{"location": row.location, "total": row.total} for row in result]