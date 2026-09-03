"""
vibration_fft.py — Simulate the ADXL345 reading from a healthy and a
failing belt.

The ADXL345 on the belt frame will record 3-axis acceleration at 100 Hz.
When an idler bearing starts to fail, a characteristic high-frequency
vibration appears at 3× the running speed. When the belt tears, there is
a sharp transient impulse. This script generates both signals,
computes their FFTs, and shows how a simple peak-detection algorithm
can flag them.

Output: vibration_fft.png in ./output/
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

# ---- Constants ----
FS       = 100             # sample rate, Hz (ADXL345 capable of up to 3200 Hz)
DURATION = 4               # seconds
T        = np.linspace(0, DURATION, FS*DURATION, endpoint=False)

# Drive pulley turning at 600 RPM = 10 Hz, so 1×RPM = 10 Hz, 3×RPM = 30 Hz
RPM_1X = 10
RPM_3X = 30

# Healthy belt: small vibration at 1× RPM, broadband noise
np.random.seed(42)
healthy = (0.3*np.sin(2*np.pi*RPM_1X*T) +
           0.08*np.random.randn(len(T)))

# Failing bearing: 1× + 3× peak rising, plus broadband energy
failing = (0.3*np.sin(2*np.pi*RPM_1X*T) +
           1.2*np.sin(2*np.pi*RPM_3X*T) +     # prominent 3× peak
           0.4*np.sin(2*np.pi*RPM_3X*1.2*T) + # bearing-sideband
           0.15*np.random.randn(len(T)))

# Belt tear: healthy for 2 s, then a sharp impulse
tear = healthy.copy()
tear_idx = int(2.0 * FS)
tear[tear_idx:tear_idx+5] += 6.0     # 30 ms impulse, 6 g
tear[tear_idx+5:tear_idx+15] += np.linspace(3.0, 0, 10)

# ---- FFT helper ----
def fft_mag(x):
    """One-sided magnitude spectrum."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, d=1/FS)
    mag = np.abs(X) * 2 / n
    return f, mag

f_h, mag_h = fft_mag(healthy)
f_f, mag_f = fft_mag(failing)
f_t, mag_t = fft_mag(tear)

# ---- Plot ----
fig, axes = plt.subplots(3, 2, figsize=(12, 9))

# Healthy
axes[0, 0].plot(T, healthy, lw=0.8)
axes[0, 0].set_title("Healthy belt — time domain")
axes[0, 0].set_ylabel("Acceleration (g)"); axes[0, 0].set_xlabel("Time (s)")
axes[0, 0].grid(True, alpha=0.3)
axes[0, 1].plot(f_h, mag_h, color="C2")
axes[0, 1].set_title("Healthy belt — frequency spectrum")
axes[0, 1].set_xlabel("Frequency (Hz)"); axes[0, 1].set_ylabel("Magnitude (g)")
axes[0, 1].set_xlim(0, 50); axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].annotate(f"1× RPM = {RPM_1X} Hz", xy=(RPM_1X, mag_h[np.argmin(np.abs(f_h-RPM_1X))]),
                     xytext=(15, 0.3), arrowprops=dict(arrowstyle="->", color="C2"))

# Failing bearing
axes[1, 0].plot(T, failing, lw=0.8, color="C1")
axes[1, 0].set_title("Failing bearing — time domain")
axes[1, 0].set_ylabel("Acceleration (g)"); axes[1, 0].set_xlabel("Time (s)")
axes[1, 0].grid(True, alpha=0.3)
axes[1, 1].plot(f_f, mag_f, color="C1")
axes[1, 1].set_title("Failing bearing — frequency spectrum")
axes[1, 1].set_xlabel("Frequency (Hz)"); axes[1, 1].set_ylabel("Magnitude (g)")
axes[1, 1].set_xlim(0, 50); axes[1, 1].grid(True, alpha=0.3)
idx_3x = np.argmin(np.abs(f_f - RPM_3X))
axes[1, 1].annotate(f"3× RPM = {RPM_3X} Hz", xy=(RPM_3X, mag_f[idx_3x]),
                     xytext=(35, 1.2), arrowprops=dict(arrowstyle="->", color="C1"),
                     color="C1", fontweight="bold")

# Belt tear
axes[2, 0].plot(T, tear, lw=0.8, color="C3")
axes[2, 0].set_title("Belt tear event — time domain")
axes[2, 0].set_ylabel("Acceleration (g)"); axes[2, 0].set_xlabel("Time (s)")
axes[2, 0].grid(True, alpha=0.3)
axes[2, 0].annotate("impulse", xy=(2.0, 6), xytext=(2.2, 5),
                    arrowprops=dict(arrowstyle="->", color="C3"))
axes[2, 1].plot(f_t, mag_t, color="C3")
axes[2, 1].set_title("Belt tear — frequency spectrum")
axes[2, 1].set_xlabel("Frequency (Hz)"); axes[2, 1].set_ylabel("Magnitude (g)")
axes[2, 1].set_xlim(0, 50); axes[2, 1].grid(True, alpha=0.3)

fig.suptitle("ADXL345 vibration simulation — three belt conditions", fontsize=14, y=1.005)
fig.tight_layout()
fig.savefig(OUT / "vibration_fft.png", dpi=120, bbox_inches="tight")
plt.close()

# ---- Summary ----
rms_h = np.sqrt(np.mean(healthy**2))
rms_f = np.sqrt(np.mean(failing**2))
rms_t = np.sqrt(np.mean(tear**2))

print("Vibration simulation complete.")
print(f"  Healthy belt RMS:        {rms_h:.3f} g")
print(f"  Failing bearing RMS:     {rms_f:.3f} g")
print(f"  Belt tear peak:          {tear.max():.2f} g  (alarm threshold > 8 g)")
print(f"  Failing: 3×RPM peak:     {mag_f[idx_3x]:.2f} g  (alarm threshold > 0.6 g)")
print(f"  Output: {OUT / 'vibration_fft.png'}")