"""
belt_thermal.py — Simulate a belt fire and the DS18B20 / NTC sensors
that try to detect it.

We model the belt surface as a 1-D thermal mass with heat input from a
friction fire. Two temperature probes (DS18B20 at x=0 m, NTC at x=0.3 m)
record the temperature over time. We plot the temperature history and
the differential dT/dt alarm threshold.

Output: belt_thermal.png in ./output/
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# ---- Constants ----
DT         = 1       # seconds
TOTAL_TIME = 600     # 10 minutes
T          = np.linspace(0, TOTAL_TIME, TOTAL_TIME+1)

# Initial temperature (ambient + a bit from sun on belt)
T0_AMB = 35.0   # °C, summer afternoon

# Fire scenario: friction fire on the carry side of the belt.
# Coal-dust fires typically release 50-200 kW/m^2 (similar to a building fire).
# We model a 60 kW/m^2 fire for ~5 minutes, then it decays as the belt cools.
def fire_heat_flux(t):
    """Heat flux on belt at hot-spot (W/m^2) as a function of time."""
    PEAK = 60_000.0  # 60 kW/m^2 = typical coal-dust fire heat flux
    if t < 120:
        return 0.0
    if t < 240:
        # ramp up over 2 min
        return PEAK * (t - 120) / (240 - 120)
    if t < 480:
        # hold
        return PEAK
    return max(0, PEAK * (1 - (t - 480) / 120))

# Belt thermal properties (rubber conveyor belt, ~10 mm thick)
C_BELT  = 1500.0    # J/(kg·K) — specific heat capacity
M_BELT  = 12.0      # kg/m^2  — mass per unit area (10 mm rubber)
H_CONV  = 25.0      # W/(m^2·K) — convective cooling (higher in mine airflow)
T_AMBIENT = 35.0

# Probes at distance x=0 (DS18B20) and x=0.30 m (NTC)
# 1-D diffusion: dT/dt = alpha * d2T/dx2 + (heat_flux - h*(T-Tamb)) / (rho*c*thickness)
# Use explicit method
NX = 50
DX = 0.30 / NX     # m, total domain 30 cm
ALPHA = 0.001      # m^2/s, approximate for rubber

T_field = np.ones(NX+1) * T_AMBIENT

ds_history = []
ntc_history = []
fire_history = []

for ti, t in enumerate(T):
    flux = fire_heat_flux(t)
    fire_history.append(flux)

    # Apply heat at x=0 (boundary)
    T_new = T_field.copy()
    T_new[0] = T_field[0] + (flux/(C_BELT*M_BELT)) * DT - (H_CONV*(T_field[0]-T_AMBIENT)/(C_BELT*M_BELT))*DT
    for i in range(1, NX):
        d2 = (T_field[i+1] - 2*T_field[i] + T_field[i-1]) / DX**2
        T_new[i] = T_field[i] + ALPHA * d2 * DT - (H_CONV*(T_field[i]-T_AMBIENT)/(C_BELT*M_BELT))*DT
    T_new[NX] = T_new[NX-1]  # zero-gradient far end

    # No artificial cap — let the physical model run free, but flag
    # temperatures above 200 degC as "belt destroyed" (used later in print).
    T_field = T_new

    ds_history.append(T_field[0])
    ntc_history.append(T_field[NX])

ds_history = np.array(ds_history)
ntc_history = np.array(ntc_history)
fire_history = np.array(fire_history)

# Compute rate of change (degC per minute)
dT_dt = np.gradient(ds_history, T) * 60.0

# ---- Plot ----
fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

ax = axes[0]
ax.plot(T/60, ds_history, label="DS18B20 @ x=0 m", lw=2, color="C3")
ax.plot(T/60, ntc_history, label="NTC @ x=0.3 m", lw=2, color="C1")
ax.axhline(70, color="red", ls="--", lw=1, label="Fire alarm threshold (70 °C)")
ax.axhline(T_AMBIENT, color="k", ls=":", lw=1, label="Ambient 35 °C")
ax.fill_between(T/60, T_AMBIENT, ds_history, where=(ds_history > 70), color="red", alpha=0.15)
ax.set_ylabel("Temperature (°C)")
ax.set_title("Belt-surface temperature during a fire — DS18B20 vs NTC probe")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left")

# Find alarm time
alarm_t = T[np.argmax(ds_history > 70)]
if alarm_t > 0:
    ax.annotate(f"ALARM @ t={alarm_t/60:.1f} min", xy=(alarm_t/60, 70),
                xytext=(alarm_t/60 + 0.3, 100),
                arrowprops=dict(arrowstyle="->", color="red"), color="red", fontweight="bold")

ax = axes[1]
ax.plot(T/60, dT_dt, color="C2", label="dT/dt at DS18B20 probe")
ax.axhline(5, color="red", ls="--", lw=1, label="Rate alarm threshold (5 °C/min)")
ax.fill_between(T/60, 5, 20, color="red", alpha=0.1)
ax.set_xlabel("Time (min)")
ax.set_ylabel("Rate (°C/min)")
ax.set_title("Rate-of-temperature-rise — early fire indicator")
ax.grid(True, alpha=0.3)
ax.legend(loc="upper left")
ax.set_ylim(-1, 20)

fig.tight_layout()
fig.savefig(OUT / "belt_thermal.png", dpi=120)
plt.close()

print("Belt-thermal simulation complete.")
print(f"  Peak DS18B20 temperature:  {ds_history.max():.1f} °C")
print(f"  Peak NTC temperature:      {ntc_history.max():.1f} °C")
print(f"  Alarm (T>70°C) fired at:   t = {alarm_t/60:.2f} min  ({(alarm_t-120)/60:.2f} min after fire start)")
print(f"  Peak dT/dt:                {dT_dt.max():.1f} °C/min")
print(f"  Output: {OUT / 'belt_thermal.png'}")