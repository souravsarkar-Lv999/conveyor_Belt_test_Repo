# LTspice Simulation — Solar Buck Converter

This folder contains **two** LTspice schematics that simulate the
**LM2596 buck converter** stepping 12 V → 5 V for the belt pod's
5 V rail.

## ⚠ Important — pick the right file

LTspice does **NOT** ship with an LM2596 subcircuit model. If you try
to simulate `solar_charger.asc` (the original) you will get the
error:

> Couldn't find a valid version of LM2596 ...

There are **two ways** to fix this:

### Option A — use the substitute schematic (recommended for first-time users)

1. Open `LM2596_substitute.asc`.
2. Click the running-man icon.
3. This schematic uses a **voltage-controlled switch** driven by a
   138 kHz pulse (50% duty = ~5 V out) to emulate the LM2596's
   internal MOSFET switching. The external components (inductor,
   Schottky diode, capacitors, load) are identical to the real LM2596
   buck, so the steady-state response and ripple are correct.

### Option B — download the LM2596 SPICE model (advanced)

1. Go to https://www.ti.com/product/LM2596 and click
   **"Download datasheet"**, then in the datasheet find the link to
   **"LM2596 PSpice Transient Model"**.
2. Save the .sub file as `LM2596.sub` in this folder.
3. Open `solar_charger.asc`.
4. Add a SPICE directive at the top:
   ```
   .inc LM2596.sub
   ```
5. The U1 symbol will now resolve to the LM2596 subcircuit.

---

## Files

| File | Purpose |
|---|---|
| `solar_charger.asc`         | Schematic with U1=LM2596 (needs external model) |
| `LM2596_substitute.asc`     | Behavioural substitute using a switch — works out of the box |
| `README.md`                 | This file |

## Companion Python sim

For system-level behaviour (battery over days, link budget, vibration
FFT, fire detection, strain gauge), see `../run_all.py` and the
Streamlit website at `../../streamlit_app.py`.