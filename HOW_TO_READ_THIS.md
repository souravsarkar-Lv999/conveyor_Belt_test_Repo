# How to Read This Repo — A "Baby Terms" Guide

If you are opening this repo and going *"what is all this?"* — read this
file first. It explains what each file is for, in plain English, and
which one to open when.

---

## 1. What is this project? (in one sentence)

A small **solar-powered sensor box** is bolted onto a coal-mine conveyor
belt. It measures things like vibration, heat, smoke and stretch, and
**wirelessly reports** to the maintenance cabin so a human doesn't have
to stand and stare at the belt all day.

---

## 2. What's in this repo?

```
conveyor_Belt_test_Repo/
│
├── README.md              ← the short intro, top of the repo
├── HOW_TO_READ_THIS.md    ← this file (you are here)
│
├── HARDWARE_DESIGN.md     ← the master plan (read this second)
├── SENSOR_DESIGN.md       ← every sensor explained
├── POWER_SYSTEM.md        ← how it gets electricity
├── COMMUNICATION.md       ← how it talks to the cabin
├── ENCLOSURE_DESIGN.md    ← the metal box that protects everything
├── WIRING_DIAGRAM.md      ← which wire goes where
├── BOM.md                 ← shopping list with prices
├── INSTALLATION.md        ← how to bolt it onto a real belt
│
├── assets/                ← photos and the 3D belt model
│   ├── Basic-components-of-a-conveyor-belt-800x400.webp
│   ├── Parts-of-the-conveyor-belt-...webp
│   ├── oreflow-2-min.jpg.webp
│   └── quarry_conveyor_system_kit.glb      ← 3D model you can open in Blender
│
└── simulations/           ← Python scripts + plots proving the design works
    ├── README.md
    ├── run_all.py         ← one-command: run everything
    ├── power_budget.py
    ├── solar_harvest.py
    ├── lora_link_budget.py
    ├── vibration_fft.py
    ├── belt_thermal.py
    └── strain_calibration.py
```

---

## 3. Which file do I open if I want to know…?

| If you want to know… | Open this file | What you'll find |
|---|---|---|
| What does the system look like, top-down? | `HARDWARE_DESIGN.md` | Big block diagram + spec table |
| Why did you pick each sensor? | `SENSOR_DESIGN.md` | One section per sensor, with the wiring |
| Where does the electricity come from? | `POWER_SYSTEM.md` | Solar panel math + battery sizing |
| How does the data reach the cabin? | `COMMUNICATION.md` | LoRa link budget + GSM fallback |
| Will it survive in a coal mine? | `ENCLOSURE_DESIGN.md` | IP67 box, Ex-d for underground, mounting locations |
| How do I wire it? | `WIRING_DIAGRAM.md` | ASCII schematics + final GPIO pin map |
| How much does it cost? | `BOM.md` | ~₹30 000 surface, ~₹98 000 underground |
| How do I install it? | `INSTALLATION.md` | Step-by-step, A → F |
| Prove the numbers are right | `simulations/` | Python scripts that generate plots |

---

## 4. Quick-start: run the simulations

You need Python 3.9+ and `matplotlib` + `numpy`. To install:

```
pip install matplotlib numpy
```

Then, from the repo root:

```
cd simulations
python run_all.py
```

This will generate **6 PNG plots** in `simulations/output/` and print the
key numbers in the terminal. Plots:

1. `power_budget.png` — battery SoC over 7 days (normal + alarm)
2. `solar_harvest.png` — solar harvest vs load across a monsoon week
3. `lora_link_budget.png` — RSSI vs distance with rock-wall penalty
4. `vibration_fft.png` — simulated ADXL345 reading + FFT showing
   bearing-fault signature
5. `belt_thermal.png` — belt surface temperature vs time during a fire
6. `strain_calibration.png` — HX711 output vs belt tension

---

## 5. Quick-start: view the 3D belt model

The file `assets/quarry_conveyor_system_kit.glb` is a 3D model of a
quarry conveyor system. To view it:

- **Blender** (free): File → Import → glTF 2.0 → pick the file. Then
  orbit with middle mouse button.
- **Windows 3D Viewer** (built-in on Win 10/11): double-click the file.
- **Web**: drag-drop into <https://gltf-viewer.donmccurdy.com>

Use it as a reference when placing the sensor pod on the belt. Suggested
mounting points are described in `ENCLOSURE_DESIGN.md` §3.

---

## 6. Quick-start: the schematics

You asked about circuit diagrams. There are three layers:

### 6.1 ASCII schematics (inside the .md files)

Open `WIRING_DIAGRAM.md` for the **full ASCII schematic** of the ESP32
carrier board, the power rails, and every external connector.

### 6.2 LTspice simulation (optional, you mentioned LTspice)

A ready-to-run LTspice schematic is provided at
`simulations/ltspice/solar_charger.asc`. To use:

1. Install LTspice (free from Analog Devices).
2. Open the `.asc` file.
3. Press the running-man icon (Simulate).

It shows the LM2596 buck converter stepping 12 V → 5 V under varying
load (which is what your pod will see in real life).

### 6.3 Python simulations (the meaty stuff)

See §4 above. These give you real **plots** showing the system's
behaviour over time, distance, temperature, etc.

---

## 7. If you are the **firmware team**

1. Read `HARDWARE_DESIGN.md` (10 min skim, 30 min deep read).
2. Open `WIRING_DIAGRAM.md` §1 — that table is your pin map. Every
   conflict in the per-sensor docs is resolved there.
3. Open `COMMUNICATION.md` §1.6 — that's the LoRa air protocol you
   need to implement.
4. Open `SENSOR_DESIGN.md` §2.3 (DS18B20) for the temperature routine.
5. Open `simulations/vibration_fft.py` — that file simulates what the
   ADXL345 will produce when a bearing fails. Useful for tuning your
   FFT thresholds.

---

## 8. If you are the **field engineer** installing it

Read `INSTALLATION.md` end-to-end **before you go to site**. The
phases are A → F. The commissioning sheet at §4 is a printable form.

---

## 9. If you are the **boss / investor** reading this

- Open `README.md` first (1-minute summary).
- Then open `BOM.md` for cost.
- Then open `HARDWARE_DESIGN.md` §5 (spec snapshot) and §6 (failure
  modes matrix) — that one screen answers "what does it actually do?".
- The **simulations** prove the numbers — open
  `simulations/output/` and look at the PNGs.

---

## 10. If you just want to know "does it work?"

Run:

```
cd simulations
python run_all.py
```

If all 6 PNGs generate and you see "ALL SIMULATIONS PASSED ✅", the
design numbers are self-consistent. The hardware itself then needs to
be built and bench-tested, but you've already de-risked the math.