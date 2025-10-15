import pandas as pd

# Step 1: Load the CSV file
df_minload = pd.read_csv("TotalLoad_DayAhead.csv")
df_minload.rename(columns={'MTU (CET/CEST)': 'datetime'}, inplace=True)

df_minload['datetime'] = (
    df_minload['datetime']
    .str.replace(r'\s*\(CET\)|\s*\(CEST\)', '', regex=True)
    .str.split(' - ').str[0]
    .str.strip()
)

df_minload['datetime'] = pd.to_datetime(df_minload['datetime'], format='%d/%m/%Y %H:%M', errors='coerce')
df_minload.dropna(subset=['datetime'], inplace=True)
df_minload.set_index('datetime', inplace=True)

# Step 7: Ensure all other columns are numeric (drop non-numeric strings like country names)
for col in df_minload.columns:
    df_minload[col] = pd.to_numeric(df_minload[col], errors='coerce')

df_hourload = df_minload.resample('h').mean().reset_index()
df_hourload.to_csv("TotalLoad_DayAhead_Hourly.csv", index=False)

# Step 10: Display summary of result
print("✅ Hourly resampling completed successfully.")
print(df_hourload.info())
print(df_hourload.head())
