import pandas as pd
from sqlalchemy import create_engine

# Database connection details
db_user = "postgres"
db_password = "ashwin999"
db_host = "localhost:5432"
db_name = "postgres"
db_schema = "insight_data" 

# Create a connection to PostgreSQL
engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}")

# Load the CSV file
csv_file = "climate-data-cali.csv"
df = pd.read_csv(csv_file)

# Ensure column names match your table schema
df.rename(columns={
    "STATION": "station_id",
    "DATE": "date",
    "DLY-CLDD-BASE40": "cooling_degree_days",
    "DLY-HTDD-BASE60": "heating_degree_days",
    "DLY-PRCP-20PCTL": "precip_20th_percentile",
    "DLY-PRCP-80PCTL": "precip_80th_percentile",
    "DLY-TMAX-NORMAL": "temp_max_normal",
    "DLY-TMIN-NORMAL": "temp_min_normal"
}, inplace=True)

# Fix date column (assuming MM-DD format, adding a default year)
df["date"] = "2023-" + df["date"]  # Add year manually
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")  # Ensure correct conversion

# Check for invalid date values
if df["date"].isnull().sum() > 0:
    print("Warning: Some date values could not be parsed!")

# Fill missing values (forward fill for continuity)
df.fillna(method="ffill", inplace=True)

# Convert numerical columns to correct data type
for col in df.columns:
    if col not in ["station_id", "date"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Upload cleaned data to PostgreSQL
# print("First 5 rows of the dataset:")
# print(df.head())

# print(f"Total rows loaded: {len(df)}")

df.to_sql("climate_data", engine, schema=db_schema, if_exists="append", index=False, method="multi")

# df.to_sql("climate_data", engine, if_exists="append", index=False)

print("Data cleaned and uploaded successfully!")
