# LTspice Simulation — LM2596 Solar Buck

This folder contains an **LTspice schematic** that simulates the
**LM2596 buck converter** stepping the solar pod's 12 V battery
output down to the 5 V rail that powers the belt pod.

## Files

- `solar_charger.asc` — open this in LTspice

## How to run

1. Install **LTspice XVII** (free from
   [Analog Devices](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)).
2. Double-click `solar_charger.asc`. LTspice will open.
3. Click the **running-man icon** in the toolbar (top right) to start
   the simulation.
4. The schematic already has `.tran 0.05 0.2` so it simulates 0–200 ms.
5. To see the 5 V output, click on the **Vout** net label or right-click
   on the wire and choose "Plot V(vout)".
6. You should see a clean ~5 V rail with switching ripple from the
   LM2596.

## What the schematic contains

- **V1** — 12 V DC source (the LiFePO4 battery)
- **U1** — LM2596-ADJ switching regulator
- **L1** — 33 µH inductor (Bourns RLB9012)
- **D1** — 1N5822 Schottky free-wheel diode
- **C1** — 220 µF output capacitor
- **C2** — 220 µF input capacitor
- **R1** — 470 Ω load resistor (≈ 10 mA, light load)

## What's NOT in the schematic

This is a simplified model. The full carrier-board schematic also has:

- AMS1117 3.3 V LDO downstream of the 5 V
- ESP32 load transients
- Solar panel input instead of battery

For those, see `../../WIRING_DIAGRAM.md` §4 for the full ASCII schematic.

## Companion Python sim

For system-level behaviour (battery over days, link budget, vibration
FFT, fire detection, strain gauge), see `../run_all.py`.