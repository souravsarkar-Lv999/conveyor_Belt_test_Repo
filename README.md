# Smart Mine Conveyor-Belt Health-Monitor

A wireless sensor pod + solar power + LoRa telemetry to detect the
conditions that lead to conveyor **belt blasts and fires** in coal/iron
mines — *replacing the "one human watches the belt with eyes" model
that has failed too many times.*

---

## 👉 New here? Start with [`HOW_TO_READ_THIS.md`](HOW_TO_READ_THIS.md)

It tells you which file to open, in plain English.

---

## Why

In mines, coal and iron are carried on conveyor belts. Today the only
health check is a human inspector watching the belt. Belt fires,
longitudinal tears, and idler seizures happen between inspections, and
when they happen the belt "blasts" — coal-dust fire / belt rupture —
endangering the mine and its people.

This project puts a **sealed sensor pod on the belt** that continuously
monitors vibration, temperature, smoke, gas, dust, tension, speed,
and tear formation, and reports back to the maintenance cabin via
**LoRa radio** (no SIM needed; works through rock) with **GSM as an
emergency fallback**.

---

## Hardware (this repo)

This repository contains the **complete hardware design** as Markdown
documentation + diagrams + Python simulations. The firmware team
handles the ESP32 code in a sibling repo.

### Index of docs

| File | What it covers |
|---|---|
| [`HOW_TO_READ_THIS.md`](HOW_TO_READ_THIS.md) | **Plain-English navigation guide — read this first** |
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
| `simulations/ltspice/` | A ready-to-run LTspice schematic for the LM2596 buck converter |

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

- **Surface / open-pit version:** ~₹30 000 / ~USD 370 per belt.
- **Underground coal-mine Ex-d version:** ~₹98 000 (extra for
  certification, flameproof box, intrinsic-safety barriers).
- See [`BOM.md`](BOM.md) for the line-by-line.

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
├── HOW_TO_READ_THIS.md    ← plain-English guide, read first
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
├── assets/                ← belt photos + 3D model
│   ├── *.webp             ← reference photos of conveyor belts
│   └── quarry_conveyor_system_kit.glb  ← 3D belt model (open in Blender)
│
└── simulations/           ← Python + LTspice
    ├── README.md
    ├── run_all.py         ← runs every Python sim, prints PASS/FAIL
    ├── power_budget.py    → power_budget.png
    ├── solar_harvest.py   → solar_harvest.png
    ├── lora_link_budget.py→ lora_link_budget.png
    ├── vibration_fft.py   → vibration_fft.png
    ├── belt_thermal.py    → belt_thermal.png
    ├── strain_calibration.py → strain_calibration.png
    ├── _organize.py       ← moves images into assets/ (run once)
    └── ltspice/
        ├── solar_charger.asc  ← LM2596 buck, open in LTspice
        └── README.md
```

The firmware team should:

1. Read [`HOW_TO_READ_THIS.md`](HOW_TO_READ_THIS.md) first.
2. Then read [`HARDWARE_DESIGN.md`](HARDWARE_DESIGN.md) end to end.
3. Then drill into [`WIRING_DIAGRAM.md`](WIRING_DIAGRAM.md) for the
   exact pin assignments.
4. Then [`COMMUNICATION.md`](COMMUNICATION.md) for the LoRa air
   protocol.

---

## Status

- ✅ Hardware design complete
- ✅ Python simulations (6 plots) — see `simulations/output/`
- ✅ LTspice schematic for the LM2596 buck
- ✅ 3D belt model in `assets/`
- ⏳ Firmware (separate repo): in progress
- ⏳ First install: planned
- ⏳ Field trial: planned