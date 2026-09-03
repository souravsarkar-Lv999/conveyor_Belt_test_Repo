"""
solar_harvest.py — 7-day solar harvest vs load simulation

Simulates the 20 W solar panel + MPPT + 12 V 20 Ah LiFePO4 battery
across a 7-day monsoon week (low sun) and a 7-day clear-sky week.

Compares daily solar harvest to daily load (5 Wh normal, 30 Wh alarm)
and shows when the battery falls below 30 % SoC.

Output: solar_harvest.png in ./output/
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# ---- Constants ----
PANEL_W     = 20          # W peak
USABLE_WH   = 205
HOURS       = 24 * 7
DT          = 1           # hour
NORMAL_WH_D = 5
ALARM_WH_D  = 30

# ---- Weather profiles (sun-hours per day, 0..1 fraction of full) ----
clear_week = np.array([0.95, 1.0, 1.0, 0.95, 0.9, 0.85, 0.9])
monsoon    = np.array([0.25, 0.15, 0.10, 0.05, 0.20, 0.30, 0.40])

def simulate(weather, panel_w, load_wh_per_day, label):
    """Returns soc_pct, harvest_wh, load_wh arrays for 7 days, 1-hour resolution."""
    n = 24 * 7
    soc = np.zeros(n+1)
    e = USABLE_WH
    load_w = load_wh_per_day / 24.0
    hourly_harvest = np.zeros(n+1)
    hourly_load    = np.zeros(n+1)
    soc[0] = 100

    # sun-hours per day distributed as 0.5 * sin(...) from 6 to 18 hr
    for day in range(7):
        cloud = weather[day]
        for h in range(24):
            i = day*24 + h
            # solar irradiance profile (sine from 6 to 18 hr, peak at noon)
            if 6 <= h <= 18:
                profile = np.sin(np.pi * (h - 6) / 12)  # 0 to 1 to 0
            else:
                profile = 0.0
            wh_this_hour = panel_w * profile * cloud  # watts × 1 hour = Wh
            hourly_harvest[i+1] = wh_this_hour
            hourly_load[i+1]    = load_w
            e += wh_this_hour - load_w
            if e > USABLE_WH:
                e = USABLE_WH
            if e < 0:
                e = 0
            soc[i+1] = 100 * e / USABLE_WH
    return soc, hourly_harvest, hourly_load

soc_clear, h_clear, l_clear = simulate(clear_week, PANEL_W, NORMAL_WH_D, "clear")
soc_monsoon_norm,  h_m1, l1 = simulate(monsoon,    PANEL_W, NORMAL_WH_D, "monsoon-normal")
soc_monsoon_alarm, h_m2, l2 = simulate(monsoon,    PANEL_W, ALARM_WH_D,  "monsoon-alarm")

# Daily totals
def daily(x):
    return x[1:].reshape(7, 24).sum(axis=1)

days = np.arange(1, 8)

fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

ax = axes[0]
width = 0.27
ax.bar(days - width, daily(h_clear),    width, label="Solar harvest — clear week", color="C2")
ax.bar(days,         daily(h_m1),       width, label="Solar harvest — monsoon week (normal load)", color="C2", alpha=0.4)
ax.bar(days + width, daily(h_m1) - daily(l1), width, label="Net (harvest – load) monsoon normal", color="C3")
ax.axhline(NORMAL_WH_D, color="k", ls="--", lw=1, label=f"Daily load ({NORMAL_WH_D} Wh)")
ax.set_ylabel("Wh / day")
ax.set_title("Solar harvest vs load — 7-day scenarios")
ax.legend(loc="upper right", fontsize=9)
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.plot(days, 100 - soc_clear[:-1:24], "o-", label="Clear sky, normal load", color="C2")
ax.plot(days, 100 - soc_monsoon_norm[:-1:24], "s-", label="Monsoon, normal load", color="C0")
ax.plot(days, 100 - soc_monsoon_alarm[:-1:24], "^-", label="Monsoon, alarm load", color="C3")
ax.axhline(30, color="red", ls=":", label="30 % SoC (BMS warning)")
ax.axhline(20, color="darkred", ls=":", label="20 % SoC (BMS cutoff)")
ax.set_ylabel("Battery depth-of-discharge (%)")
ax.set_xlabel("Day")
ax.set_ylim(0, 105)
ax.set_title("Battery depth-of-discharge (lower = healthier)")
ax.legend(loc="upper left", fontsize=9)
ax.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig(OUT / "solar_harvest.png", dpi=120)
plt.close()

# Summary
print("Solar-harvest simulation complete.")
print(f"  Clear sky weekly harvest:    {daily(h_clear).sum():.1f} Wh")
print(f"  Monsoon weekly harvest:      {daily(h_m1).sum():.1f} Wh")
print(f"  Normal load weekly need:     {NORMAL_WH_D * 7} Wh")
print(f"  Alarm  load weekly need:     {ALARM_WH_D * 7} Wh")
print(f"  DoD after monsoon normal:    peak {100 - soc_monsoon_norm[-1]:.0f} %")
print(f"  DoD after monsoon alarm:     peak {100 - soc_monsoon_alarm[-1]:.0f} %")
print(f"  Output: {OUT / 'solar_harvest.png'}")