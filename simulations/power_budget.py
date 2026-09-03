"""
power_budget.py — Battery State-of-Charge over 7 days

Simulates the 12 V 20 Ah LiFePO4 battery powering the smart-belt pod,
under three scenarios:
  - normal mode (5 Wh/day)
  - alarm mode (30 Wh/day)
  - mixed (normal 5 d, alarm 2 d)

Compares against the autonomy claims made in POWER_SYSTEM.md.

Output: power_budget.png  in  ./output/
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# ---- Constants (from POWER_SYSTEM.md §1) ----
BATTERY_WH    = 256         # 12 V × 20 Ah
USABLE_WH     = 205         # 80% DoD
NORMAL_WH_D   = 5
ALARM_WH_D    = 30
HOURS         = 24 * 7      # 7 days
DT            = 1           # 1-hour steps

t = np.arange(0, HOURS + DT, DT)

def simulate(load_wh_per_day, label):
    load_w = load_wh_per_day / 24.0  # average W
    # pretend load is constant for simplicity (worst case)
    e = USABLE_WH                       # start full
    soc = np.zeros_like(t, dtype=float)
    for i, ti in enumerate(t):
        soc[i] = max(0, e / USABLE_WH)
        # discharge by 1 hour of load
        e -= load_w * DT
        if e < 0:
            e = 0
    return soc

# Three scenarios
soc_normal  = simulate(NORMAL_WH_D, "Normal 5 Wh/day")
soc_alarm   = simulate(ALARM_WH_D,  "Alarm 30 Wh/day")

# Mixed scenario: 5 d normal + 2 d alarm
mixed_load = np.zeros_like(t)
mixed_load[t < 5*24]  = NORMAL_WH_D / 24
mixed_load[t >= 5*24] = ALARM_WH_D / 24
e = USABLE_WH
soc_mixed = np.zeros_like(t)
for i in range(len(t)):
    soc_mixed[i] = max(0, e / USABLE_WH)
    e -= mixed_load[i] * DT
    if e < 0:
        e = 0

# ---- Plot ----
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(t/24, soc_normal*100, label=f"Normal mode ({NORMAL_WH_D} Wh/day)", lw=2)
ax.plot(t/24, soc_alarm*100,  label=f"Alarm mode ({ALARM_WH_D} Wh/day)", lw=2)
ax.plot(t/24, soc_mixed*100,  label="Mixed: 5 d normal + 2 d alarm", lw=2, ls="--")

ax.axhline(20, color="red", ls=":", lw=1, label="BMS low-voltage cutoff (20 %)")
ax.axhline(0,  color="black", lw=0.5)

ax.set_xlabel("Days")
ax.set_ylabel("Battery State of Charge (%)")
ax.set_title("Smart-belt pod — 12 V 20 Ah LiFePO4 autonomy (no solar)")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper right")
ax.set_ylim(-5, 105)
ax.set_xlim(0, 7)

# Annotate key days
for d, label in [(41/24*5, ""), (6.8, "alarm-cutoff\n6.8 d")]:
    pass

ax.annotate("41 days normal-mode autonomy", xy=(6.5, 80), xytext=(5.5, 55),
            arrowprops=dict(arrowstyle="->", color="C0"), color="C0")
ax.annotate("6.8 days alarm-mode autonomy", xy=(6.5, 8), xytext=(4, 30),
            arrowprops=dict(arrowstyle="->", color="C1"), color="C1")

fig.tight_layout()
fig.savefig(OUT / "power_budget.png", dpi=120)
plt.close()

# ---- Print summary ----
def hours_to_pct_drop(soc, drop_pct):
    below = np.where(soc*100 < drop_pct)[0]
    return int(below[0]) if below.size else None

nh = hours_to_pct_drop(soc_normal, 20)
ah = hours_to_pct_drop(soc_alarm,  20)
mh = hours_to_pct_drop(soc_mixed,  20)

print("Power-budget simulation complete.")
if nh is not None:
    print(f"  Normal mode reaches 20 % SoC at {nh/24:.1f} days  (claim: 41 d)")
else:
    print("  Normal mode: did NOT reach 20 % SoC in 7-day window (consistent with 41-day claim)")
if ah is not None:
    print(f"  Alarm  mode reaches 20 % SoC at {ah/24:.1f} days  (claim: 6.8 d)")
else:
    print("  Alarm  mode: did NOT reach 20 % SoC in 7-day window")
if mh is not None:
    print(f"  Mixed  scenario reaches 20 % SoC at {mh/24:.1f} days")
else:
    print("  Mixed  scenario: did NOT reach 20 % SoC in 7-day window")
print(f"  Output: {OUT / 'power_budget.png'}")
