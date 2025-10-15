import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("ggplot")

# 1. Load datasets
df_load = pd.read_csv("TotalLoad_DayAhead_Hourly.csv", parse_dates=["datetime"])
df_gen = pd.read_csv("TotalGen_Hourly.csv", parse_dates=["Hourly_Time_Start"])
df_types = pd.read_csv("generation_hourly_all_types.csv", parse_dates=["Time_Interval"])

# 2. Rename + clean
df_gen.rename(columns={"Hourly_Time_Start": "datetime"}, inplace=True)
df_types.rename(columns={"Time_Interval": "datetime"}, inplace=True)

# Drop useless string columns
for df in [df_load, df_gen, df_types]:
    df.drop(columns=["Country_Area", "Area"], errors="ignore", inplace=True)

# 3. Set index and resample
df_load.set_index("datetime", inplace=True)
df_gen.set_index("datetime", inplace=True)
df_types.set_index("datetime", inplace=True)

daily_load = df_load.resample('D').mean(numeric_only=True)
daily_gen = df_gen.resample('D').mean(numeric_only=True)
daily_types = df_types.resample('D').mean(numeric_only=True)


# -----------------------------
# 📊 1. Plot daily Load & Generation
# -----------------------------
plt.figure(figsize=(14, 5))
plt.plot(daily_load.index, daily_load["Actual Total Load (MW)"], label="Actual Load")
plt.plot(daily_load.index, daily_load["Day-ahead Total Load Forecast (MW)"], label="Forecast Load", linestyle='--')
plt.plot(daily_gen.index, daily_gen["Average_Hourly_Generation"], label="Total Generation", alpha=0.7)
plt.title("Daily Load vs Forecast vs Total Generation")
plt.xlabel("Date")
plt.ylabel("Power (MW)")
plt.legend()
plt.tight_layout()
plt.savefig("plots/daily_load_vs_gen.png", dpi=300, bbox_inches='tight')
plt.show()

# -----------------------------
# 📊 2. Generation by type (stacked area chart)
# -----------------------------
daily_types_sorted = daily_types[daily_types.columns.sort_values()]  # optional sort
daily_types_sorted.plot.area(stacked=True, figsize=(14, 6), alpha=0.85)
plt.title("Daily Generation by Type (Stacked Area)")
plt.xlabel("Date")
plt.ylabel("Power (MW)")
plt.tight_layout()
plt.savefig("plots/gen_type.png", dpi=300, bbox_inches='tight')
plt.show()

# -----------------------------
# 📊 3. Monthly average (bar chart)
# -----------------------------
monthly_load = df_load.resample('M').mean()
monthly_gen = df_gen.resample('M').mean()

monthly = pd.DataFrame({
    "Actual Load": monthly_load["Actual Total Load (MW)"],
    "Forecast Load": monthly_load["Day-ahead Total Load Forecast (MW)"],
    "Total Generation": monthly_gen["Average_Hourly_Generation"]
})

monthly.plot(kind='bar', figsize=(14, 6))
plt.title("Monthly Average: Load and Generation")
plt.ylabel("Power (MW)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("plots/monthly_gen_load.png", dpi=300, bbox_inches='tight')
plt.show()

# -----------------------------
# 📊 4. Peak Hour Analysis (mean by hour)
# -----------------------------
df_load["hour"] = df_load.index.hour
df_gen["hour"] = df_gen.index.hour

load_by_hour = df_load.groupby("hour")[["Actual Total Load (MW)"]].mean()
gen_by_hour = df_gen.groupby("hour")[["Average_Hourly_Generation"]].mean()

plt.figure(figsize=(10, 5))
plt.plot(load_by_hour.index, load_by_hour["Actual Total Load (MW)"], label="Load by Hour")
plt.plot(gen_by_hour.index, gen_by_hour["Average_Hourly_Generation"], label="Generation by Hour", linestyle="--")
plt.title("Average Load and Generation by Hour of Day")
plt.xlabel("Hour")
plt.ylabel("Power (MW)")
plt.xticks(range(0, 24))
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/Peak_analysis.png", dpi=300, bbox_inches='tight')
plt.show()

# -----------------------------
# 📊 5. Correlation heatmap
# -----------------------------
plt.figure(figsize=(12, 10))
corr = daily_types.corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap: Generation Types")
plt.tight_layout()
plt.savefig("plots/correlation_matrix.png", dpi=300, bbox_inches='tight')
plt.show()
