# Smart Mine Conveyor-Belt Health-Monitor

A wireless sensor pod + solar power + LoRa telemetry to detect the
conditions that lead to conveyor **belt blasts and fires** in coal/iron
mines — *replacing the "one human watches the belt with eyes" model
that has failed too many times.*

> **🎬 Demo:** run the interactive Streamlit website locally —
> double-click `run_website.bat` (Windows) or `bash run_website.sh`
> (Linux/macOS). Opens at <http://localhost:8501>.

---

## The problem

In coal and iron mines, conveyor belts carry thousands of tonnes per hour.
Today the only health check is a human inspector walking past the belt every
shift. Between inspections, **belt fires and belt tears can start, and a
"belt blast" — coal-dust fire + belt rupture — can kill people and shut
the mine for months.**

This project puts a **sealed sensor pod on the belt** that continuously
monitors vibration, temperature, smoke, gas, dust, tension, speed,
and tear formation, and reports back to the maintenance cabin via
**LoRa radio** (no SIM needed; works through rock) with **GSM as an
emergency fallback**.

---

## Quick start — run the website

```bash
# 1) install deps (one-time)
pip install -r requirements.txt

# 2) launch the website
streamlit run streamlit_app.py
# OR just double-click run_website.bat
```

Then open <http://localhost:8501> in your browser. The site has
**9 interactive sections** (left sidebar):

1. **🏠 Overview** — hero metrics, system block diagram
2. **🏗 Architecture** — full animated schematic with annotated sensors
3. **🎛 Sensor Pod (3D)** — download the .glb 3D model, internal layout, sensor map
4. **📡 Live Telemetry** — simulated dashboard with "inject fire" button
5. **🔬 Simulations** — interactive plots with sliders (same maths as the PNGs)
6. **☀ Power System** — solar sizing, energy budget table
7. **📶 LoRa Link** — radio budget, antenna notes
8. **💰 BOM & Cost** — searchable bill of materials, total in ₹ / USD
9. **🛠 Installation** — 8-step install walkthrough

---

## Hardware (this repo)

This repository contains the **complete hardware design** as Markdown
documentation + diagrams + Python simulations + Streamlit website.

### Docs

| File | What it covers |
|---|---|
| [`HARDWARE_DESIGN.md`](HARDWARE_DESIGN.md) | System overview, block diagram, philosophy, spec snapshot, failure modes |
| [`SENSOR_DESIGN.md`](SENSOR_DESIGN.md) | Every sensor: ESP32, ADXL345, HX711 + strain gauge, DS18B20, NTC, Hall, E18 IR, ACS712, GP2Y, MQ-2/-135, OLED, buzzer — with rationale, wiring, mounting |
| [`POWER_SYSTEM.md`](POWER_SYSTEM.md) | Solar sizing, MPPT charge controller, LiFePO4 battery, LM2596 / AMS1117 rails |
| [`COMMUNICATION.md`](COMMUNICATION.md) | SX1278 LoRa + SIM800L GSM link budget, antenna placement, gateway, range extension |
| [`ENCLOSURE_DESIGN.md`](ENCLOSURE_DESIGN.md) | Die-cast IP67 box, vibration isolation, conformal coat, Ex-d option, mounting locations |
| [`WIRING_DIAGRAM.md`](WIRING_DIAGRAM.md) | Full GPIO pin map (all conflicts resolved), connector pin-outs, PCB layout notes, ASCII schematics |
| [`BOM.md`](BOM.md) | Bill of materials with part numbers, prices (India), per-component justification |
| [`INSTALLATION.md`](INSTALLATION.md) | Step-by-step install on a live belt, commissioning sheet, common mistakes |

### Simulations & 3D model

| File | What it covers |
|---|---|
| `assets/` | Photos of conveyor belts + a **3D `.glb` model** of a quarry conveyor (open in Blender / Windows 3D Viewer) |
| `simulations/` | **Python scripts** that mathematically model the whole hardware system, generating PNG plots in `simulations/output/` |
| `simulations/run_all.py` | One command runs every simulation |
| `simulations/ltspice/` | Two LTspice schematics — `solar_charger.asc` (needs LM2596 model) and **`LM2596_substitute.asc`** (works out of the box) |
| `streamlit_app.py` | The interactive website |
| `requirements.txt` | Python deps for the website |
| `run_website.bat` / `.sh` | One-click launcher |

---

## What it does (in one minute)

```
   sensor pod on belt ───LoRa───► maintenance cabin
   (solar-powered)            (dashboard + siren)
         │
         └── GSM (SMS only, fallback)
```

| Detected | How |
|---|---|
| **Belt tear** | IR diffuse sensor at head pulley (primary) + vibration impulse + tension drop (backup) |
| **Belt fire** | DS18B20 > 70 °C + MQ-2 smoke + MQ-135 CO/CH₄ rise |
| **Idler seizure** | RPM drop + ACS712 current spike + vibration RMS rise |
| **Belt slip** | RPM vs expected divergence + current drop + tension drop |
| **Bearing wear** | ADXL345 spectral peak shift from 1× to 3× RPM |
| **Power outage** | Battery V < 11.0 V, pod drops to low-power mode |

Any **two** sensors confirming a fault within 30 s → **cabin siren + SMS
+ local buzzer**.

---

## Bill of materials (summary)

- **Surface / open-pit version:** ~₹17 000 / ~USD 200 per belt.
- **Underground coal-mine Ex-d version:** ~₹98 000 (extra for
  certification, flameproof box, intrinsic-safety barriers).
- See [`BOM.md`](BOM.md) and the **BOM section** in the Streamlit
  website for the line-by-line.

---

## Spec snapshot

| | |
|---|---|
| Supply | 12 V from solar pod (20 W panel + MPPT + 12 V 20 Ah LiFePO4) |
| Power rails | 5 V (LM2596), 3.3 V (AMS1117) |
| Solar autonomy | 41 days normal mode, 6.8 days alarm mode |
| RF link | LoRa 868 MHz SF12 BW125 — 2–5 km line of sight, ~500 m through 1 rock wall |
| IP rating | IP67 belt pod, IP66 solar pod |
| Operating temp | -20 °C to +70 °C |
| Service interval | 6 months |

---

## Repo layout

```
conveyor_Belt_test_Repo/
├── README.md              ← you are here
├── streamlit_app.py       ← ⭐ the website — run this!
├── requirements.txt       ← pip install -r requirements.txt
├── run_website.bat        ← Windows one-click launcher
├── run_website.sh         ← Linux/macOS launcher
│
├── HARDWARE_DESIGN.md
├── SENSOR_DESIGN.md
├── POWER_SYSTEM.md
├── COMMUNICATION.md
├── ENCLOSURE_DESIGN.md
├── WIRING_DIAGRAM.md
├── BOM.md
├── INSTALLATION.md
│
├── assets/                ← belt photos + 3D .glb model
│
└── simulations/           ← Python + LTspice
    ├── README.md
    ├── run_all.py
    ├── power_budget.py
    ├── solar_harvest.py
    ├── lora_link_budget.py
    ├── vibration_fft.py
    ├── belt_thermal.py
    ├── strain_calibration.py
    ├── output/            ← generated PNG plots (committed)
    └── ltspice/
        ├── solar_charger.asc     ← original (needs LM2596 model)
        ├── LM2596_substitute.asc ← ⭐ works out of the box
        └── README.md
```

---

## Status

- ✅ Hardware design complete
- ✅ Interactive **Streamlit website** with 9 sections
- ✅ Python simulations (6 plots) — see `simulations/output/`
- ✅ LTspice schematic for the LM2596 buck (substitute + original)
- ✅ 3D belt model in `assets/`
- ⏳ Firmware (separate repo): in progress
- ⏳ First install: planned
- ⏳ Field trial: planned