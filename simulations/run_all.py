"""
run_all.py — Run every simulation in this folder and print a summary.

Usage:
    cd simulations
    python run_all.py

Each simulation writes a PNG into ./output/ and prints key numbers.
This script runs them in a logical order and at the end prints a
single PASS/FAIL summary.
"""

import sys
import time
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT  = HERE / "output"
OUT.mkdir(exist_ok=True)

SIMS = [
    "power_budget.py",
    "solar_harvest.py",
    "lora_link_budget.py",
    "vibration_fft.py",
    "belt_thermal.py",
    "strain_calibration.py",
]

print("=" * 60)
print("Smart-belt hardware — running all simulations")
print("=" * 60)

results = []
for sim in SIMS:
    print(f"\n>>> {sim}")
    t0 = time.time()
    try:
        cp = subprocess.run(
            [sys.executable, str(HERE / sim)],
            capture_output=True, text=True, timeout=120,
        )
        dt = time.time() - t0
        if cp.returncode == 0:
            print(cp.stdout.strip())
            print(f"  ({dt:.1f} s)  OK")
            results.append((sim, True, dt))
        else:
            print("FAILED:")
            print(cp.stdout)
            print(cp.stderr)
            results.append((sim, False, dt))
    except Exception as e:
        print(f"EXCEPTION: {e}")
        results.append((sim, False, 0))

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
all_ok = True
for sim, ok, dt in results:
    flag = "✅" if ok else "❌"
    print(f"  {flag} {sim:30s}  {dt:.1f} s")
    if not ok:
        all_ok = False

print()
if all_ok:
    print("ALL SIMULATIONS PASSED ✅")
    print(f"Plots written to: {OUT}")
    sys.exit(0)
else:
    print("SOME SIMULATIONS FAILED ❌")
    sys.exit(1)