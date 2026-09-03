# Simulations

This folder contains **Python simulations** that mathematically model the
behaviour of every key part of the smart-belt hardware system. Each
script writes a PNG plot into `./output/` and prints the key numbers
that prove the design.

The simulations are **not** the firmware, and they are **not** the real
hardware. They are **design de-risking** — they check the numbers in
`../POWER_SYSTEM.md`, `../COMMUNICATION.md`, `../SENSOR_DESIGN.md` etc.
are self-consistent before we build the kit.

---

## Quick start

```bash
# 1) install deps (one-time)
pip install matplotlib numpy

# 2) run everything
cd simulations
python run_all.py
```

`run_all.py` will:
- execute every `*.py` script in this folder in order,
- write PNG plots into `output/`,
- print a PASS / FAIL summary.

---

## What each simulation does

| Script | What it models | Output PNG |
|---|---|---|
| `power_budget.py` | 12 V 20 Ah LiFePO4 battery discharging under normal (5 Wh/day) and alarm (30 Wh/day) loads for 7 days | `power_budget.png` |
| `solar_harvest.py` | 20 W solar panel + MPPT + battery, across a clear-sky week and a monsoon week | `solar_harvest.png` |
| `lora_link_budget.py` | LoRa 868 MHz RSSI vs distance, with rock-wall penalty (1 wall, 2 walls) | `lora_link_budget.png` |
| `vibration_fft.py` | ADXL345 readings from a healthy belt, a failing bearing, and a tear event; FFT shows the 3× RPM fault peak | `vibration_fft.png` |
| `belt_thermal.py` | 1-D thermal model of belt surface during a fire, with DS18B20 + NTC probe response | `belt_thermal.png` |
| `strain_calibration.py` | HX711 + BF350 strain-gauge ADC count vs belt tension in Newtons | `strain_calibration.png` |

---

## LTspice simulation

You said you have LTspice installed. There is a ready-to-run schematic in
`ltspice/solar_charger.asc` that simulates the **LM2596 buck
converter** stepping 12 V → 5 V under varying load (the same converter
that powers the belt pod).

To run it:
1. Open LTspice (free download from Analog Devices).
2. File → Open → `ltspice/solar_charger.asc`.
3. Click the running-man icon (top toolbar) to simulate.
4. Click on the output node to see the 5 V rail.

This complements the Python sims by exercising the **circuit-level**
behaviour (ripple, transient response, inductor saturation).

---

## Reading the plots

Each plot is annotated with the threshold that should trigger an alarm
(red dashed line) or a hardware limit (green dotted line). Read the
plot left-to-right or top-to-bottom and look at where the **simulated
trace** crosses the threshold — that tells you **when** the system
would detect the fault in real life.

### Example: `belt_thermal.png`

- **Top panel**: belt surface temperature at the DS18B20 probe (red) and
  at the NTC probe (orange) during a fire that starts at t=2 min and
  peaks at 800 W/m².
- **Bottom panel**: rate of temperature rise (°C/min). The 5 °C/min
  threshold is the **early warning** — it would fire ~30 s *before* the
  70 °C absolute threshold.

---

## Adding a new simulation

Drop another `<name>.py` file in this folder that:
1. has a top-level `from pathlib import Path`,
2. writes a PNG to `output/<name>.png`,
3. prints one or two key numbers,
4. is added to the `SIMS` list in `run_all.py`.

That's it — `run_all.py` will pick it up next time.

---

## What these sims **do not** cover

- The **mechanical** behaviour of the belt (mass, friction, slip).
  That is the firmware team's job to characterise on-site.
- The **wireless propagation** in a specific mine. Real RSSI depends on
  rock type, geometry and moisture — always do a site survey with a
  portable LoRa node before installing the gateway.
- The **intrinsic-safety** calculations (energy limits, surface
  temperature). Those are in `../ENCLOSURE_DESIGN.md` §5.