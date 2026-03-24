from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    location = Column(String)
    technology = Column(String, index=True)
    seniority = Column(String) 
    salary = Column(Float, nullable=True)
    posted_at = Column(DateTime)