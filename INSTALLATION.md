# Installation Guide — Smart Belt Monitor

A step-by-step procedure to bolt the entire system onto a conveyor belt
in an open-cast or surface mine. Expect **4–6 hours per belt** for a
two-pod install + 1 hour for the cabin gateway.

> ⚠ **Safety first.** This work is done in a coal/iron mine. Follow mine
> safety procedure: PTW (Permit to Work), lock-out tag-out on the
> conveyor, gas testing, PPE (helmet, boots, hi-vis, gas monitor).
> The conveyor must be **locked out and not under power** while installing
> the strain gauge and ACS712.

---

## 1. Pre-Installation Checklist

| Done | Item |
|---|---|
| ☐  | PTW obtained, conveyor locked out |
| ☐  | Site survey completed (GPS, photos, structural measurements) |
| ☐  | LoRa link test passed (pod ↔ cabin RF-budget confirmed) |
| ☐  | All parts present and accounted for (vs BOM-A) |
| ☐  | Tools staged: torque wrench, drill, M10 tap, M6 Allen, crimper, hot-air gun |
| ☐  | Pod firmware pre-loaded on all ESP32s (done at bench) |
| ☐  | Cabin dashboard software installed and tested with a stand-in pod |
| ☐  | Spare fuses, screws, glands |

---

## 2. Tools Required

- Cordless impact driver + drill bits (M6, M10, M12)
- M10 × 1.5 tap (for belt-frame mounting holes, if not pre-tapped)
- Torque wrench (5–25 Nm)
- Multimeter + clamp meter
- USB-UART cable (for pod programming via the lid connector)
- Crimper for ring terminals (10 AWG, 18 AWG)
- LoRa RSSI meter or SDR dongle (for antenna alignment)
- Compass + inclinometer (solar panel orientation)
- Step ladder / scissor lift (for solar pod on the roof)
- First-aid kit + gas detector

---

## 3. Step-by-Step Install

### Phase A — Solar Pod (45 min)

1. **Survey the roof / pole position.** Pick a spot ≥ 3 m above grade
   with **clear south exposure** (Northern hemisphere), no shadows from
   trusses, no falling-rock path.
2. **Anchor the pole.** Drill 4 × M12 holes into the concrete roof (or
   use chemical anchors), bolt the base plate, erect the GI pole.
3. **Mount the panel.** Bolt the panel to the U-bracket, set tilt to
   latitude − 10°, point the panel true south (use compass with
   declination correction).
4. **Mount the solar pod box** (ABS, with battery inside) on the pole
   below the panel.
5. **Wire MPPT inside the box.** Connect panel MC4 → fuse → MPPT PV
   input. Connect MPPT battery output → 5 A fuse → battery.
6. **Connect battery.** Strip the leads, crimp ring terminals, torque
   to 5 Nm.
7. **Verify the MPPT is alive.** The LCD should show battery voltage
   (≈ 12.6 V) and PV voltage (≈ 18 V on a sunny day).

### Phase B — Pod-1 at Tail Pulley (60 min)

1. **Position the bracket.** Hold the bracket against the C-channel of
   the belt frame, **200 mm below** the tail pulley on the return side.
   Mark 2 × M10 hole positions.
2. **Drill and tap** (if needed). Use cutting oil, low RPM.
3. **Bolt bracket with M10 U-bolts**, torque to 35 Nm.
4. **Apply strain gauge** to the take-up frame:
   - Grind the surface smooth (180-grit).
   - Degrease with isopropanol.
   - Apply M-Bond 200 catalyst.
   - Stick gauge with M-Bond 610 adhesive.
   - Cover with M-Coat A + 3M 1181 tape.
   - Wait 24 h for full cure (or accelerate with heat lamp 60 °C for 2 h).
5. **Mount the ADXL345 bracket** (separate from the pod) on the
   bracket, **outside** the Sorbothane isolators.
6. **Place Sorbothane pads** between the bracket and the pod back-plate.
7. **Bolt the pod** to the bracket. Hand-tighten M6 captive screws.
8. **Wire all sensor cables** to J1–J7 (see `WIRING_DIAGRAM.md`).
9. **Tighten all cable glands** to 5 Nm.
10. **Connect the solar-pod armoured cable** to J1 (+12 V, GND).
11. **Close the lid**, torque Torx screws to 3 Nm.
12. **Power up.** Watch the OLED: "BOOT OK".

### Phase C — Pod-2 at Head Pulley (60 min)

Same as Phase B, with these differences:

- Mount 2 m **before** the head pulley on the carry-side structure.
- Install IR sensor brackets on each side of the belt, **5 cm above**
  the belt surface. Align the beams across the belt edge.
- MQ-2 and MQ-135 sit **above** the belt (gas rises).
- GP2Y dust inlet faces into the carry-side airspace, with the PTFE
  membrane facing down.
- Mount magnet ring on the drive-pulley end face. Set Hall sensor
  air-gap to 2 mm.

### Phase D — Run the Sensor Cables (30 min per pod)

- Cables run in **flexible conduit** (PVC, 20 mm OD).
- Conduit clamped every 30 cm with **SS-316 P-clips**.
- Where cables cross belt structure, **bridge** them on a 50 × 50 mm
  steel angle iron to protect from impact.
- All cables labelled at both ends with printed heat-shrink.

### Phase E — Cabin Gateway (60 min)

1. **Mount gateway** in the cabin, near a window or external wall.
2. **Mount the external antenna** (6 dBi Yagi) on a pole or wall
   bracket, aimed at the belt pit.
3. **Run coax** through a wall gland into the gateway enclosure.
4. **Wire cabin siren + strobe** to the relay output (12 V coil, 5 A
   contacts).
5. **Plug gateway into PC** via USB; verify "hello" packet arrives on
   the dashboard.
6. **Set the LoRa address pair** (pod ID 0x01, 0x02, gateway 0x00).

### Phase F — Acceptance Test (30 min)

Run through the 7-step acceptance test from
[`ENCLOSURE_DESIGN.md`](ENCLOSURE_DESIGN.md) §9:

1. Power-up: pod OLED shows "BOOT OK".
2. Cabin "ALARM TEST" → pod buzzes + cabin siren fires.
3. Local button → status blink.
4. Lighter heat near DS18B20 → "TEMP WARN" reaches cabin within 30 s.
5. Hand-shake bracket → "VIB" message arrives.
6. Cover solar panel → battery voltage drops over 30 min, pod alive.
7. "STATUS?" SMS → reply within 60 s.

Sign off the as-built form and photograph each installation point.

---

## 4. Commissioning Sheet

Print and fill in on the day of install:

```
╔════════════════════════════════════════════════════════════╗
║              SMART BELT MONITOR COMMISSIONING              ║
╠════════════════════════════════════════════════════════════╣
║ Site:                  ____________________________        ║
║ Conveyor ID:           ____________________________        ║
║ Pod-1 S/N:             ____________________________        ║
║ Pod-2 S/N:             ____________________________        ║
║ Gateway S/N:           ____________________________        ║
║ LoRa addr (pod-1):     0x____                                ║
║ LoRa addr (pod-2):     0x____                                ║
║ Solar pod battery V:   ________ V (should be 12.4–13.4)     ║
║ Solar pod battery A:   ________ Ah (full = 20)              ║
║ Pod-1 firmware ver:    ________                              ║
║ Pod-2 firmware ver:    ________                              ║
║ Gateway firmware ver:  ________                              ║
║ LoRa RSSI @ install:   ________ dBm                          ║
║ Acceptance test pass:  ☐ 1  ☐ 2  ☐ 3  ☐ 4  ☐ 5  ☐ 6  ☐ 7    ║
║ Photos taken:          ☐ bracket   ☐ solar   ☐ cabin        ║
║ Installed by:          ____________________________        ║
║ Date:                  ________                              ║
║ Sign-off:              ____________________________        ║
╚════════════════════════════════════════════════════════════╝
```

---

## 5. First-Week Monitoring (remote)

The firmware team will get daily heartbeats. Watch for:

- **Battery V drops > 0.5 V/day** → solar panel dirty, or shading
- **LoRa RSSI drops > 10 dB** → antenna loose, water in coax, or new
  obstruction
- **MQ sensor baseline drifts > 20 %** → humidity issue, replace
  sensor
- **Strain gauge zero drifts** → M-Coat failure, re-glue

---

## 6. Decommissioning (when belt is replaced)

1. Lock out conveyor.
2. Power off pod via lid switch.
3. Disconnect solar pod from battery.
4. Label all cables.
5. Remove pods, antenna, solar pod.
6. Drain battery to 30 % SoC for long-term preservation (per LiFePO4
   storage guidelines).
7. Bag and store in dry cabinet.

---

## 7. Common Installation Mistakes (and how to avoid them)

| Mistake | Consequence | Fix |
|---|---|---|
| Solar panel faces north | Battery never charges | Compass + declination check |
| Strain gauge glued over paint | Gauge peels in 2 weeks | Grind to bare metal, M-Bond 200 |
| IR sensor aimed at coal, not belt edge | False alarms every minute | Aim beam across belt edge |
| MPPT battery terminals loose | Voltage drops under load, MPPT resets | Torque to 5 Nm, re-check after 1 week |
| LoRa antenna routed next to power cable | RSSI drops 15 dB | Separate by ≥ 30 cm |
| MQ sensor heater always on | Battery dies in 1 day | PWM 1 % duty |
| DS18B20 in a thermally-conducting grease | Reads MCU temp | Use thermal pad, not grease |
| ACS712 near a VFD | Pickup noise spikes | Add 1 kΩ + 100 nF LPF |
| Bolt bracket into thin gauge metal | Tears out under vibration | Through-bolt with backing plate |
| Forgot drain holes in pod | Condensation pools, kills PCB | Drill 2× 3 mm holes, fit Gore vent |

---

**Hardware design is complete.** Review, hand off to firmware team,
build one kit, install, iterate.