import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Use Seaborn whitegrid style if available, else default
try:
    sns.set_style("whitegrid")
except:
    plt.style.use("default")

# ---------- 1. Load Datasets ----------
df_load = pd.read_csv("TotalLoad_DayAhead_Hourly.csv", parse_dates=["datetime"])
df_gen = pd.read_csv("TotalGen_Hourly.csv", parse_dates=["Hourly_Time_Start"])
df_gen_types = pd.read_csv("generation_hourly_all_types.csv", parse_dates=["Time_Interval"])

# ---------- 2. Rename Columns for Consistency ----------
df_gen.rename(columns={"Hourly_Time_Start": "datetime", "Average_Hourly_Generation": "Total_Generation"}, inplace=True)
df_gen_types.rename(columns={"Time_Interval": "datetime"}, inplace=True)

# ---------- 3. Actual vs Forecasted Load ----------
plt.figure(figsize=(12, 5))
plt.plot(df_load["datetime"], df_load["Actual Total Load (MW)"], label="Actual Load", linewidth=1.5)
plt.plot(df_load["datetime"], df_load["Day-ahead Total Load Forecast (MW)"], label="Forecasted Load", linestyle="--", alpha=0.7)
plt.title("Actual vs Forecasted Load")
plt.xlabel("Date")
plt.ylabel("Load (MW)")
plt.legend()
plt.tight_layout()
plt.show()

# ---------- 4. Total Hourly Generation ----------
plt.figure(figsize=(12, 5))
plt.plot(df_gen["datetime"], df_gen["Total_Generation"], color="green", label="Total Generation")
plt.title("Total Hourly Generation")
plt.xlabel("Date")
plt.ylabel("Generation (MW)")
plt.legend()
plt.tight_layout()
plt.show()

# ---------- 5. Stacked Area Plot of Generation by Type ----------
df_gen_types.set_index("datetime", inplace=True)
generation_cols = df_gen_types.select_dtypes(include='number').columns

df_gen_types[generation_cols].plot.area(stacked=True, figsize=(14, 6), alpha=0.85)
plt.title("Hourly Generation by Type (Stacked Area Plot)")
plt.xlabel("Date")
plt.ylabel("MW")
plt.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
plt.tight_layout()
plt.show()

# ---------- 6. Individual Generation Type Trends ----------
plt.figure(figsize=(14, 6))
for col in generation_cols:
    plt.plot(df_gen_types.index, df_gen_types[col], label=col, linewidth=1)

plt.title("Individual Generation Type Trends")
plt.xlabel("Date")
plt.ylabel("MW")
plt.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
plt.tight_layout()
plt.show()

# ---------- Reset index (if needed for further processing) ----------
df_gen_types.reset_index(inplace=True)
