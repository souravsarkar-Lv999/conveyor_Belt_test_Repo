"""
strain_calibration.py — HX711 + strain-gauge calibration curve

Models the HX711 24-bit ADC front-end and the BF350-3AA strain gauge
in a full Wheatstone bridge. Plots the HX711 output code (in raw ADC
counts) vs belt tension in N, for a typical conveyor belt take-up
frame.

Output: strain_calibration.png in ./output/
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# ---- Strain-gauge & HX711 model ----
GAUGE_FACTOR = 2.0          # BF350-3AA
GAUGE_RESISTANCE = 350.0    # ohm
EXCITATION_V     = 5.0      # V (HX711 internal regulator)
BRIDGE_SENSITIVITY = 1.0    # mV/V per strain (full-bridge gives 1 mV/V per microstrain? we use a simplified model)

# Take-up frame stiffness: 1 N of belt tension -> 1 microstrain on frame
# (highly site-specific; this is a representative value)
MICROSTRAIN_PER_N = 1.0

# HX711 gain = 128 (channel A), full-scale ±20 mV at 5 V
# With 24-bit ADC, full-scale code = 2^23 = 8 388 608 (signed)
HX711_FSR = 20e-3           # V
HX711_CODE_FSR = 2**23      # 8.39 M
HX711_NOISE_RMS = 50e-9     # 50 nV RMS noise

def hx711_output_counts(tension_n):
    """Return signed HX711 code counts for a given belt tension in N."""
    microstrain  = tension_n * MICROSTRAIN_PER_N
    bridge_delta_v = EXCITATION_V * BRIDGE_SENSITIVITY * microstrain * 1e-6
    return bridge_delta_v / HX711_FSR * HX711_CODE_FSR

def noise_floor_counts():
    """RMS noise in code counts."""
    return HX711_NOISE_RMS / HX711_FSR * HX711_CODE_FSR

# Sweep tension from 0 to 10 000 N
tension = np.linspace(0, 10000, 1000)
counts  = hx711_output_counts(tension)

# Noise floor
nf = noise_floor_counts()
counts_with_noise = counts + np.random.normal(0, nf, len(counts))

# Effective resolution at low end
resolution_n = (nf / HX711_CODE_FSR) * HX711_FSR / (EXCITATION_V * BRIDGE_SENSITIVITY * 1e-6 * MICROSTRAIN_PER_N)

# ---- Plot ----
fig, axes = plt.subplots(1, 2, figsize=(13, 6))

ax = axes[0]
ax.plot(tension, counts, color="C0", lw=2, label="HX711 ideal")
ax.plot(tension, counts_with_noise, color="C0", alpha=0.3, lw=0.5, label="HX711 + noise")
ax.axhline(nf, color="red", ls="--", lw=1, label=f"Noise floor ({nf:.0f} counts)")
ax.axhline(-nf, color="red", ls="--", lw=1)
ax.set_xlabel("Belt tension (N)")
ax.set_ylabel("HX711 ADC code (counts)")
ax.set_title("HX711 calibration curve")
ax.grid(True, alpha=0.3)
ax.legend()

ax = axes[1]
# Plot the noise zoomed in: 0-500 N region
mask = tension < 500
ax.plot(tension[mask], counts[mask], color="C0", lw=2, label="HX711 ideal")
ax.plot(tension[mask], counts_with_noise[mask], "o", color="C0", alpha=0.4, markersize=2, label="HX711 + noise")
ax.axhline(nf, color="red", ls="--", lw=1, label=f"Noise floor ({nf:.0f} counts)")
ax.axhline(-nf, color="red", ls="--", lw=1)
ax.axvline(resolution_n, color="green", ls=":", lw=1, label=f"Resolution ≈ {resolution_n:.1f} N")
ax.set_xlabel("Belt tension (N)")
ax.set_ylabel("HX711 ADC code (counts)")
ax.set_title("Low-tension detail (0 – 500 N)")
ax.grid(True, alpha=0.3)
ax.legend()

fig.suptitle("Belt-tension sensor — HX711 + BF350 strain-gauge model", fontsize=13, y=1.02)
fig.tight_layout()
fig.savefig(OUT / "strain_calibration.png", dpi=120, bbox_inches="tight")
plt.close()

# Summary
print("Strain-gauge calibration complete.")
print(f"  HX711 code full-scale:     ±{HX711_CODE_FSR:,}")
print(f"  HX711 noise floor:         {nf:.1f} counts  (= {HX711_NOISE_RMS*1e9:.0f} nV)")
print(f"  Effective tension resolution: ~ {resolution_n:.2f} N")
print(f"  Code at 1000 N tension:    {hx711_output_counts(1000):,.0f} counts")
print(f"  Code at 5000 N tension:    {hx711_output_counts(5000):,.0f} counts")
print(f"  Output: {OUT / 'strain_calibration.png'}")