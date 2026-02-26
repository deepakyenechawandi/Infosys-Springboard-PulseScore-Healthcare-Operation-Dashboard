import pandas as pd
import os

base_path = os.getcwd()
csv_path = os.path.join(base_path, "dataset", "India_Healthcare_Final_GeoPreserved.csv")

df = pd.read_csv(csv_path)
print(f"Columns: {df.columns.tolist()}")

if "Location_Coordinates" in df.columns:
    coords = df["Location_Coordinates"].str.split(",", expand=True)
    df["lat"] = pd.to_numeric(coords[0], errors="coerce")
    df["lon"] = pd.to_numeric(coords[1], errors="coerce")
    
    print(f"Sample lat: {df['lat'].head().tolist()}")
    print(f"Sample lon: {df['lon'].head().tolist()}")
    print(f"NaN lats: {df['lat'].isna().sum()}")
    print(f"Total rows: {len(df)}")
else:
    print("Location_Coordinates column missing!")
