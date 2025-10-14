import pandas as pd
import matplotlib.pyplot as plt

# --- Muted color palette centered on #75896b ---
palette = {
    "primary": "#75896b",  # your key color
    "blue":    "#6b7d91",
    "red":     "#a06b6b",
    "purple":  "#8a6b91",
    "amber":   "#b09b6b"
}

# Update global Matplotlib style
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Georgia", "DejaVu Serif", "Garamond"],
    "font.size": 12,
    "axes.titlesize": 15,
    "axes.labelsize": 12,
    "axes.edgecolor": "#3f4739",
    "axes.labelcolor": "#3f4739",
    "xtick.color": "#3f4739",
    "ytick.color": "#3f4739",
    "text.color": "#3f4739",
    "axes.titlepad": 10,
    "grid.color": "#c8d1bd",
    "grid.alpha": 0.6,
    "grid.linestyle": "--",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

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
print("Hourly resampling completed successfully.")
print(df_hourload.info())
print(df_hourload.head())

# Ensure the two series exist and are numeric
cols_actual = 'Actual Total Load (MW)'
cols_da = 'Day-ahead Total Load Forecast (MW)'

# Build a plotting copy for the hourly file WITHOUT modifying the CSV on disk
df_plot_hour = df_hourload.copy()
# Your hourly CSV shows 'datetime' like "01/01/2024 00:00"
df_plot_hour['datetime'] = pd.to_datetime(df_plot_hour['datetime'], dayfirst=True, errors='coerce')
df_plot_hour.dropna(subset=['datetime'], inplace=True)
df_plot_hour.set_index('datetime', inplace=True)

# Coerce numeric (safe even if already numeric)
df_plot_hour[cols_actual] = pd.to_numeric(df_plot_hour[cols_actual], errors='coerce')
df_plot_hour[cols_da] = pd.to_numeric(df_plot_hour[cols_da], errors='coerce')

# Quick sanity prints (optional)
print("Hourly rows parsed:", len(df_plot_hour))
print(df_plot_hour[[cols_actual, cols_da]].notna().sum())

from pathlib import Path

cols_actual = 'Actual Total Load (MW)'
cols_da = 'Day-ahead Total Load Forecast (MW)'

out_raw   = Path("raw_plot.png")
out_hour  = Path("hourly_plot.png")

# --- Build figures explicitly ---
fig_raw, ax_raw = plt.subplots(figsize=(12, 5))
df_minload[cols_actual].plot(ax=ax_raw, color=palette["primary"], linewidth=1.2, label="Actual Load (MW)")
df_minload[cols_da].plot(ax=ax_raw, color=palette["purple"], linewidth=1, label="Day-ahead Forecast (MW)")
ax_raw.set_title("Total Load — RAW (Quarter-hour)")
ax_raw.set_xlabel("Datetime")
ax_raw.set_ylabel("Load [MW]")
ax_raw.legend(frameon=False)
ax_raw.grid(True, alpha=0.4)
fig_raw.tight_layout()

fig_hr, ax_hr = plt.subplots(figsize=(12, 5))
df_plot_hour[cols_actual].plot(ax=ax_hr, color=palette["primary"], linewidth=1.2, label="Actual Load (MW)")
df_plot_hour[cols_da].plot(ax=ax_hr, color=palette["purple"], linewidth=1, label="Day-ahead Forecast (MW)")
ax_hr.set_title("Total Load — HOURLY (from TotalLoad_DayAhead_Hourly.csv)")
ax_hr.set_xlabel("Datetime")
ax_hr.set_ylabel("Load [MW]")
ax_hr.legend(frameon=False)
ax_hr.grid(True, alpha=0.4)
fig_hr.tight_layout()

# Align x-limits for both raw and hourly
xmin = df_plot_hour.index.min()
xmax = df_plot_hour.index.max()

ax_raw.set_xlim(xmin, xmax)
ax_hr.set_xlim(xmin, xmax)

# --- Save first (no GUI required to save) ---
fig_raw.savefig(out_raw, dpi=300, bbox_inches="tight")
fig_hr.savefig(out_hour, dpi=300, bbox_inches="tight")
print(f"Saved plots: {out_raw.resolve()}  |  {out_hour.resolve()}")

# --- Compute first 3-month window based on RAW data index ---
start = df_minload.index.min()
if pd.isna(start):
    raise ValueError("No timestamps found in df_minload.")
start = start.normalize().replace(day=1)          # align to first day of that month
end = start + pd.DateOffset(months=3)

# --- Filter both datasets to the window ---
raw_3m   = df_minload.loc[(df_minload.index >= start) & (df_minload.index < end), [cols_actual, cols_da]].copy()
hour_3m  = df_plot_hour.loc[(df_plot_hour.index >= start) & (df_plot_hour.index < end), [cols_actual, cols_da]].copy()

print(f"Plotting window: {start:%Y-%m-%d %H:%M}  to  {end:%Y-%m-%d %H:%M}")
print("RAW points:", len(raw_3m), " | HOURLY points:", len(hour_3m))

# --- Build figures (save first, then show) ---
fig_raw, ax_raw = plt.subplots(figsize=(12, 5))
raw_3m[cols_actual].plot(ax=ax_raw, color=palette["primary"], linewidth=1.2, label="Actual Load (MW)")
raw_3m[cols_da].plot(ax=ax_raw,    color=palette["purple"],    linewidth=1, label="Day-ahead Forecast (MW)")
ax_raw.set_title("Total Load — RAW (First 3 Months)")
ax_raw.set_xlabel("Datetime"); ax_raw.set_ylabel("Load [MW]")
ax_raw.grid(True, alpha=0.4); ax_raw.legend(frameon=False)
fig_raw.tight_layout()

fig_hr, ax_hr = plt.subplots(figsize=(12, 5))
hour_3m[cols_actual].plot(ax=ax_hr, color=palette["primary"], linewidth=1.2, label="Actual Load (MW)")
hour_3m[cols_da].plot(ax=ax_hr,    color=palette["purple"],    linewidth=1, label="Day-ahead Forecast (MW)")
ax_hr.set_title("Total Load — HOURLY (First 3 Months)")
ax_hr.set_xlabel("Datetime"); ax_hr.set_ylabel("Load [MW]")
ax_hr.grid(True, alpha=0.4); ax_hr.legend(frameon=False)
fig_hr.tight_layout()

# Align x-limits for both raw and hourly
start = df_minload.index.min()
end = start + pd.DateOffset(months=3)

ax_raw.set_xlim(start, end)
ax_hr.set_xlim(start, end)

# Save + show
out_raw  = Path("raw_plot_3months.png")
out_hour = Path("hourly_plot_3months.png")
fig_raw.savefig(out_raw, dpi=300, bbox_inches="tight")
fig_hr.savefig(out_hour, dpi=300, bbox_inches="tight")
print(f"Saved: {out_raw.resolve()}  |  {out_hour.resolve()}")

# --- Then display (pick ONE style) ---

# A) Blocking (simplest & most stable)
plt.show()

# B) Non-blocking (if you really need the script to continue)
#plt.show(block=False)
#plt.pause(0.1)  # allow windows to render
#input("Press Enter to close plots...")  # keep open until you press Enter
#plt.close('all')
