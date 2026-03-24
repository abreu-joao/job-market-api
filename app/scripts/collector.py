import pandas as pd
from app.database import SessionLocal, engine, Base
from app.models.job import Job
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def extract_data() -> pd.DataFrame:
    print("Starting mass data extraction via The Muse API...")
    raw_jobs = []
    
    for page in range(1, 15):
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

                description_html = job.get("contents", "")

                pub_date = job.get("publication_date")
                
                raw_jobs.append({
                    "title": job.get("name", "No Title"),
                    "company": company_name,
                    "location": location_name,
                    "salary": "0",
                    "posted_at": pub_date,
                    "description": description_html
                })
        else:
            print(f"Error reading page {page}. Status Code: {response.status_code}")
            
    df = pd.DataFrame(raw_jobs)
    print(f"Success! {len(df)} jobs extracted from the API.")
    return df

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print("Starting data transformation: whitelist, technology, seniority, and title cleaning...")
    df['title'] = df['title'].str.strip().str.title()
    df['company'] = df['company'].str.strip()
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce').fillna(0.0)
    df['posted_at'] = pd.to_datetime(df['posted_at'], errors='coerce').dt.tz_localize(None)
    
    valid_words = [
        'software', 'developer', 'backend', 'frontend', 'fullstack', 
        'data', 'machine learning', 'cyber', 'security', 'devops', 
        'cloud', 'network', 'qa', 'system', 'artificial intelligence',
        'ios', 'android', 'mobile'
    ]
    df = df[df['title'].str.lower().str.contains('|'.join(valid_words), na=False)]

    def clean_html(html_text):
        if not html_text:
            return ""
        return BeautifulSoup(str(html_text), "html.parser").get_text(separator=" ").lower()

    df['clean_desc'] = df['description'].apply(clean_html)

    def extract_tech(row):
        text_to_search = str(row['title']).lower() + " " + str(row['clean_desc'])
        techs = []
        if 'python' in text_to_search: techs.append('Python')
        if 'java ' in text_to_search or 'spring' in text_to_search: techs.append('Java')
        if 'javascript' in text_to_search or 'react' in text_to_search: techs.append('JavaScript/React')
        if 'node' in text_to_search: techs.append('Node.js')
        if 'c#' in text_to_search or '.net' in text_to_search: techs.append('C#/.NET')
        if 'data ' in text_to_search or 'machine learning' in text_to_search: techs.append('Data/ML')
        if 'ruby' in text_to_search: techs.append('Ruby')
        if 'go ' in text_to_search or 'golang' in text_to_search: techs.append('Go')
        if 'aws' in text_to_search: techs.append('AWS')
        if 'sql' in text_to_search: techs.append('SQL')
        if 'docker' in text_to_search: techs.append('Docker')
        
        return ", ".join(techs) if techs else 'Not Specified'
        
    df['technology'] = df.apply(extract_tech, axis=1)

    def extract_seniority(title):
        t = str(title).lower()
        t_clean = t.replace(',', ' ').replace('-', ' ').replace('/', ' ')
        words = set(t_clean.split())
        
        if words.intersection({'senior', 'sr', 'principal', 'lead', 'staff', 'manager', 'iii'}):
            return 'Senior / Lead'
        elif words.intersection({'junior', 'jr', 'entry', 'intern', 'internship', 'i'}):
            return 'Junior / Entry'
        elif words.intersection({'mid', 'ii'}) or 'mid level' in t:
            return 'Mid-Level'
        else:
            return 'Not Specified'

    df['seniority'] = df['title'].apply(extract_seniority)
    
    def clean_title(title):
        t = title.split('(')[0].strip()
        
        t_normalized = t.replace(' - ', ',').replace(' / ', ',')
        
        if ',' in t_normalized:
            parts = [p.strip() for p in t_normalized.split(',')]
            if len(parts[0]) <= 12 and len(parts) > 1:
                t = parts[1]
            else:
                t = parts[0]
        else:
            t = t_normalized
                
        return t

    df['title'] = df['title'].apply(clean_title)
    
    print(f"Transformation completed. {len(df)} jobs kept after filtering.")
    return df

def load_data(df: pd.DataFrame) -> None:
    print("Starting data load to database...")
    db = SessionLocal()
    try:
        for _, row in df.iterrows():
            new_job = Job(
                title=row['title'],
                company=row['company'],
                location=row['location'],
                technology=row['technology'],
                seniority=row['seniority'],  
                salary_min=float(row['salary']),
                salary_max=0.0,
                posted_at=row['posted_at']
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