import pandas as pd
from app.database import SessionLocal, engine, Base
from app.models.job import Job
from datetime import datetime
import requests

def extract_data():
    print("Starting mass data extraction via The Muse API...")
    raw_jobs = []
    
    for page in range(1, 25):
        print(f"Downloading page {page}...")
        url = f"https://www.themuse.com/api/public/jobs?category=Software%20Engineering&page={page}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            jobs_list = data.get("results", [])
            
            for job in jobs_list:
                locations = job.get("locations", [])
                location_name = locations[0].get("name") if locations else "Remote / Not specified"
                
                company_data = job.get("company", {})
                company_name = company_data.get("name", "Unknown")
                
                raw_jobs.append({
                    "title": job.get("name", "No Title"),
                    "company": company_name,
                    "location": location_name,
                    "salary": "0" 
                })
        else:
            print(f"Error reading page {page}. Status Code: {response.status_code}")
            
    df = pd.DataFrame(raw_jobs)
    print(f"Success! {len(df)} jobs extracted from the API.")
    return df

def transform_data(df):
    print("Starting data transformation...")
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce').fillna(0.0)
    df['title'] = df['title'].str.strip().str.title()
    df['company'] = df['company'].str.strip()
    print("Transformation completed.")
    return df

def load_data(df):
    print("Starting data load to database...")
    db = SessionLocal()
    try:
        for _, row in df.iterrows():
            new_job = Job(
                title=row['title'],
                company=row['company'],
                location=row['location'],
                technology="Python",
                salary_min=float(row['salary']),
                salary_max=0.0,
                posted_at=datetime.now()
            )
            db.add(new_job)
        
        db.commit()
        print(f"Success: {len(df)} jobs saved to the database!")
    except Exception as e:
        print(f"Error loading data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Checking database structure...")
    Base.metadata.create_all(bind=engine)
    
    raw_df = extract_data()
    clean_df = transform_data(raw_df)
    load_data(clean_df)