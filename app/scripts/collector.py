import pandas as pd

def extract_data():
    print("Starting data extraction...")
    raw_jobs = [
        {"title": "Python Developer", "company": "Tech Corp", "location": "Remote", "salary": "5000"},
        {"title": "Data Engineer", "company": "Data Inc", "location": "São Paulo", "salary": "7000"},
        {"title": "Machine Learning Engineer", "company": "AI Solutions", "location": "Remote", "salary": "8500"},
        {"title": "Backend Developer", "company": "Cloud Systems", "location": "Curitiba", "salary": "not informed"},
    ]
    return pd.DataFrame(raw_jobs)

def transform_data(df):
    """Cleans and formats data for database standards"""
    print("Starting data transformation...")

    # Convert salary to numeric, filling invalid values with 0.0
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce').fillna(0.0)

    # Standardize text fields
    df['title'] = df['title'].str.strip().str.title()
    df['company'] = df['company'].str.strip()

    print("Transformation completed.")
    return df

if __name__ == "__main__":
    raw_df = extract_data()
    clean_df = transform_data(raw_df)
    print("\n--- Transformed Data ---")
    print(clean_df)