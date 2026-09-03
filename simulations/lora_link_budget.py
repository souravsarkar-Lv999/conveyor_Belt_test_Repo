"""
lora_link_budget.py — LoRa RSSI vs distance, with rock-wall penalty

Plots the received-signal-strength indicator (RSSI) of the LoRa link
between the belt pod and the maintenance-cabin gateway at 868 MHz,
with TX power +14 dBm, 3 dBi antenna gain at both ends, 1.5 dB cable
loss, and sensitivity -137 dBm (SF12, BW 125 kHz).

Three scenarios:
  - free space (open-pit mine, line of sight)
  - one rock wall (mine portal, ~12 dB penalty)
  - two rock walls (deep mine, ~24 dB penalty)

Output: lora_link_budget.png in ./output/
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# ---- Constants ----
FREQ_HZ    = 868e6
TX_P_DBM   = 14
TX_GAIN    = 3
RX_GAIN    = 3
CABLE_LOSS = 1.5
SENS_DBM   = -137
ROCK_LOSS_1 = 12     # dB for 1 rock wall
ROCK_LOSS_2 = 24     # dB for 2 rock walls

def fspl_db(d_km, freq_hz=FREQ_HZ):
    """Free-space path loss in dB."""
    return 32.45 + 20*np.log10(d_km) + 20*np.log10(freq_hz/1e6)

def rssi(d_km, rock_loss):
    """Received signal strength in dBm."""
    path = fspl_db(d_km)
    return TX_P_DBM + TX_GAIN + RX_GAIN - CABLE_LOSS - path - rock_loss

d = np.linspace(0.1, 10, 500)   # 100 m to 10 km

rssi_free = rssi(d, 0)
rssi_1    = rssi(d, ROCK_LOSS_1)
rssi_2    = rssi(d, ROCK_LOSS_2)

# Find maximum usable distance (where RSSI = sensitivity).
# In free space at SF12 the link budget really does give huge range, but
# in practice the relevant range is site-specific (under 10 km for a mine).
# We report the real free-space limit and also clip to 200 km for plotting.
def max_dist(rock_loss):
    lo, hi = 0.05, 5000.0
    if rssi(5000, rock_loss) >= SENS_DBM:
        return 5000.0
    while hi - lo > 0.01:
        mid = (lo + hi) / 2
        if rssi(mid, rock_loss) < SENS_DBM:
            hi = mid
        else:
            lo = mid
    return lo

md_free = max_dist(0)
md_1    = max_dist(ROCK_LOSS_1)
md_2    = max_dist(ROCK_LOSS_2)

# ---- Plot ----
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(d, rssi_free, label="Free space (open-pit LOS)", color="C2", lw=2)
ax.plot(d, rssi_1,    label="1 rock wall (portal)",     color="C1", lw=2)
ax.plot(d, rssi_2,    label="2 rock walls (deep mine)", color="C3", lw=2)
ax.axhline(SENS_DBM, color="k", ls="--", lw=1, label=f"Sensitivity {SENS_DBM} dBm (SF12/BW125)")

# Mark maximum usable distance
for md, color, name in [(md_free, "C2", "Free"),
                        (md_1,    "C1", "1 wall"),
                        (md_2,    "C3", "2 walls")]:
    if md < 10:
        ax.axvline(md, color=color, ls=":", lw=1, alpha=0.7)
        ax.annotate(f"{md:.1f} km", xy=(md, SENS_DBM), xytext=(md+0.2, SENS_DBM+5),
                    color=color, fontsize=9)

ax.set_xlabel("Distance (km)")
ax.set_ylabel("Received Signal Strength (dBm)")
ax.set_title(f"LoRa 868 MHz link budget  (TX {TX_P_DBM} dBm, 3 dBi antennas, 1.5 dB cable)")
ax.grid(True, alpha=0.3)
ax.legend(loc="lower left")
ax.set_ylim(-160, -60)
ax.set_xlim(0, 10)

fig.tight_layout()
fig.savefig(OUT / "lora_link_budget.png", dpi=120)
plt.close()

# ---- Summary ----
print("LoRa link-budget simulation complete.")
print(f"  Free space max range:      {md_free:.2f} km")
print(f"  1 rock wall max range:     {md_1:.2f} km")
print(f"  2 rock walls max range:    {md_2:.2f} km")
print(f"  RSSI @ 2 km, free space:   {rssi(2.0, 0):.1f} dBm  (margin {rssi(2.0,0)-SENS_DBM:.0f} dB)")
print(f"  RSSI @ 1 km, 1 rock wall:  {rssi(1.0, ROCK_LOSS_1):.1f} dBm  (margin {rssi(1.0,ROCK_LOSS_1)-SENS_DBM:.0f} dB)")
print(f"  Output: {OUT / 'lora_link_budget.png'}")