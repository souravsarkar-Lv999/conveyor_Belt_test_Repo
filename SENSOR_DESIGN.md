# Sensor Design — Smart Mine Conveyor-Belt Monitor

This file describes **every sensor** in the belt pod: what it does, why it is
chosen, how it is electrically wired to the ESP32, and where on the conveyor
it is physically mounted.

---

## 1. Sensor Layout on the Conveyor

```
                   ◄──────── belt travel ────────
                   ┌────────────────────────────┐
                   │                            │
   ┌─── TAIL ───────┤   idlers  ═══════════════  ├──── HEAD ────┐
   │  pulley        │   . . . . . . . . . . .   │  pulley       │
   │                │                            │               │
   └───────┬────────┘                            └─────┬─────────┘
           │                                         │
           │                                         │
       [Pod-1: tension + temp + RPM]            [Pod-2: tear + vibration + gas]
       (mounted between last idler              (mounted 2 m before head pulley)
        and tail pulley)
```

Two pods per belt (≈50 m belt). One is mandatory, two is recommended.
Both pods share the same LoRa address family but different IDs so the gateway
can identify which one is talking.

---

## 2. Sensor-by-Sensor Design

### 2.1 Vibration Sensor — **SW-420 (digital) + ADXL345 (analog tri-axial)**

**Why:** A belt that is about to tear / has a seized idler / has a failing
bearing vibrates differently. RMS amplitude and frequency content are the
earliest indicator of mechanical failure.

| Spec | Value |
|---|---|
| Part | ADXL345 (3-axis MEMS, ±16 g, I²C/SPI) + SW-420 digital threshold |
| Interface | I²C (default addr 0x53) |
| Range | ±16 g, resolution 3.9 mg/LSB |
| Sample rate | 100 Hz (more than enough for 0–20 Hz belt vibration) |
| ESP32 pin | SDA=21, SCL=22 (shared I²C bus) |

**Wiring:**
```
ADXL345 VCC ──► 3V3
ADXL345 GND ──► GND
ADXL345 SDA ──► GPIO21  (10 kΩ pull-up to 3V3)
ADXL345 SCL ──► GPIO22  (10 kΩ pull-up to 3V3)
ADXL345 CS  ──► 3V3 (forces I²C mode)
ADXL345 SDO ──► GND   (selects addr 0x53)
```

**Mounting:** Rigid aluminium bracket bolted through the belt frame, **not** on
the idler itself (we want belt-frame vibration, not pulley noise). Apply thin
layer of silicone thermal compound between bracket and frame for good coupling.

**Diagnostic logic (hardware implication):**
- RMS > 4 g continuously → "severe vibration"
- Spectral peak shift from 1×RPM to 3×RPM → bearing wear
- Sudden impulse > 8 g → possible belt tear

---

### 2.2 Strain Gauge + HX711 — Belt Tension & Load

**Why:** Over-tensioning or sudden loss of tension are direct precursors to
belt rip / drive-pulley slip. A half-bridge strain gauge glued to the belt
frame tells us tension in real time.

| Spec | Value |
|---|---|
| Gauge | BF350-3AA, 350 Ω, gauge factor 2.0 |
| Configuration | Full Wheatstone bridge on a load-bearing cross-bar |
| Amplifier | HX711 24-bit ADC, 10 Hz / 80 Hz selectable |
| ESP32 pin | DOUT=GPIO16, SCK=GPIO4 |

**Wiring:**
```
HX711 VCC  ──► 5V
HX711 GND  ──► GND
HX711 DOUT ──► GPIO16
HX711 SCK  ──► GPIO4
HX711 E+/E- ──► bridge excitation
HX711 A+/A- ──► bridge output
```

**Mounting:** Glue the strain gauge (covered with M-Coat A + 3M 1181 tape) to
the **underside of the take-up pulley frame**, where strain from belt tension
is maximum. Run a 4-wire shielded cable back to the pod; shield grounded at
pod end only.

**Why HX711:** Native 24-bit ADC means we can resolve micro-strain without an
external instrumentation amplifier. Onboard regulated excitation → stable
readings even as 12 V sags.

---

### 2.3 Temperature Sensors — **DS18B20 (digital) + 10 k NTC (analog backup)**

**Why:** Coal-dust fires and idler-seizure fires start at the carry side.
A belt surface above 70 °C = fire until proven otherwise. Two sensor types =
redundancy + faster response.

| Spec | Value |
|---|---|
| Digital | DS18B20, -55 °C to +125 °C, ±0.5 °C, 1-Wire |
| Analog backup | NTC 10 k B=3950, on a voltage divider to 3V3 |
| ESP32 pin | DQ=GPIO17 (with 4.7 kΩ pull-up to 3V3), NTC=GPIO34 (ADC1_CH6) |

**Wiring:**
```
DS18B20 VDD ──► 3V3 (parasite mode also OK)
DS18B20 GND ──► GND
DS18B20 DQ  ──► GPIO17  (4.7 kΩ pull-up to 3V3)
NTC top   ──► 3V3
NTC bot   ──► GPIO34 ──► GND   (10 kΩ series, forms divider)
```

**Mounting:**
- **DS18B20** — clamped to belt underside with a stainless P-clip, **3 cm
  above** the carry-side belt surface (touching the belt surface through
  thermal pad). In a stainless steel probe sheath.
- **NTC** — same location but 30 cm downstream (so a fire has to travel
  between them, gives us a fire-propagation speed reading).

**Diagnostic logic:**
- T > 70 °C → fire warning
- ΔT between two probes > 20 °C in 10 s → local hotspot
- Rate of change > 5 °C/min → combustion signature

---

### 2.4 RPM / Belt-Speed Sensor — **Hall-Effect + Magnet Ring**

**Why:** Drive-pulley RPM is the master clock. Belt speed = π × D × RPM/60.
Sudden drop = slip or tear.

| Spec | Value |
|---|---|
| Sensor | Honeywell SS49E linear Hall, or A3144 digital Hall |
| Trigger | 8 neodymium magnets (N52) glued to drive-pulley end face |
| Interface | Digital pulse, internally pulled-up |
| ESP32 pin | GPIO27 (input, with 10 kΩ pull-up) |
| Use | `pcnt` (hardware pulse counter) on ESP32 |

**Wiring:**
```
Hall VCC ──► 3V3
Hall GND ──► GND
Hall OUT ──► GPIO27  (10 kΩ pull-up to 3V3)
```

**Mounting:** Sensor in aluminium bracket fixed to the take-up frame; magnets
on a stainless ring bolted to the drive-pulley shaft. Set air-gap to **2 mm**.

---

### 2.5 Belt-Tear Sensor — **IR Diffuse-Reflective (E18-D80NK / M18 retro)**

**Why:** A longitudinal tear shows up as a sudden gap in the belt at the
head pulley. A retro-reflective sensor pointed at the belt edge detects
**any** discontinuity (joint, tear, foreign object) within 80 mm.

| Spec | Value |
|---|---|
| Part | E18-D80NK NPN, 3–80 cm adjustable range |
| Output | NPN open-collector, digital |
| ESP32 pin | GPIO26 (interrupt-capable) |

**Wiring:**
```
E18 brown  ──► 5V
E18 blue   ──► GND
E18 black  ──► GPIO26  (10 kΩ pull-up to 3V3, hardware interrupt)
```

**Mounting:** Two units, one on each side of the belt, mounted on the head
pulley frame. Beam crosses the belt edge perpendicularly. If the beam is
broken for >50 ms while belt is moving → torn / opened joint.

> **Why not a camera?** Cameras in coal dust fail in days. IR is robust.

---

### 2.6 Current Sensor — **ACS712-30A (drive-motor current)**

**Why:** Motor current is a leading indicator of load on the belt. A seized
idler spikes the current; a slipped belt drops it.

| Spec | Value |
|---|---|
| Part | ACS712-30A, 66 mV/A, 5 V supply |
| Interface | Analog, 0–3.3 V via on-board divider |
| ESP32 pin | GPIO35 (ADC1_CH7, input-only) |

**Wiring:**
```
ACS712 VCC ──► 5V
ACS712 GND ──► GND
ACS712 OUT ──► GPIO35
```

**Safety:** ACS712 is **isolated** from the motor conductors (no direct
connection). A current transformer (CT) such as SCT-013-030 is preferred in
production — see v2 BOM.

**Mounting:** Clamp around one of the 3-phase supply lines, in the starter
panel, not in the belt pod. Run shielded twisted pair back to the pod. Note:
long cable run + 50 Hz mains frequency → RC low-pass on receiver side
recommended (1 kΩ + 100 nF to GND on the ESP32 pin).

---

### 2.7 Dust / Particulate Sensor — **GP2Y1010AU0F (Sharp)**

**Why:** Excess coal dust = explosion risk (coal-dust methanogenesis). Also
indicates carry-side carry-back spillage.

| Spec | Value |
|---|---|
| Part | GP2Y1010AU0F, optical, 0–0.6 mg/m³ |
| Interface | Analog, with internal IR LED pulsed |
| ESP32 pin | AOUT=GPIO33 (ADC1_CH5), LED=GPIO25 (PWM, 0.32 ms pulse every 10 ms) |

**Wiring:**
```
GP2Y VCC ──► 5V (sensor needs 5 V for the LED)
GP2Y GND ──► GND
GP2Y AOUT ──► GPIO33 (10 kΩ + 1 µF low-pass)
GP2Y LED  ──► GPIO25 (drives NPN via 150 Ω)
```

**Mounting:** Vertical, sampling hole facing into carry-side airspace, away
from direct water spray. Inlet protected by a hydrophobic PTFE membrane
(Whatman 7590) that lets air through but blocks liquid water.

---

### 2.8 Gas / Smoke Sensors — **MQ-2 (smoke/CH4) + MQ-135 (CO/NH3/NOx)**

**Why:** MQ-2 catches a smouldering fire before visible smoke. MQ-135 catches
CO from underground combustion. Two different sensing chemistries = less
common-mode failure.

| Spec | Value |
|---|---|
| MQ-2 | Heater 5 V, load 10 kΩ, analog out |
| MQ-135 | Heater 5 V, load 20 kΩ, analog out |
| ESP32 pin | MQ-2 → GPIO32, MQ-135 → GPIO33 is taken; use GPIO39 (ADC-only) |

**Wiring:**
```
MQ-x VCC (H) ──► 5V (via P-channel MOSFET for heater PWM)
MQ-x GND ──► GND
MQ-x AOUT ──► GPIO (via 10 kΩ to GND as load divider)
MOSFET gate ──► GPIO13  (heater enabled only during sampling)
```

**Mounting:** Gas sensor head outside the enclosure through a sintered
bronze vent (water-trap). Mount **above** the belt (gas rises). Important:
heaters run for **3 days burn-in** before calibration.

> **Caveat:** MQ sensors recover slowly after poisoning by siloxane. Provide
> a calibration flag and plan to replace every 18 months.

---

### 2.9 Local Annunciators — **Buzzer + OLED**

**Why:** Local indication lets on-site workers stop the belt immediately
without waiting for the cabin to acknowledge.

| Spec | Value |
|---|---|
| Buzzer | 12 V, 110 dB piezo siren, PWM-driven via NPN |
| OLED | SSD1306 0.96" I²C, 128×64 |
| ESP32 pin | BUZ=GPIO2 (PWM), OLED on shared I²C bus (0x3C) |

**Wiring:**
```
Buzzer + ──► 5V (via 2N2222 + flyback diode)
Buzzer − ──► GND
OLED VCC ──► 3V3
OLED GND ──► GND
OLED SDA ──► GPIO21
OLED SCL ──► GPIO22
```

---

### 2.10 Communication Modules — **LoRa SX1278 (RA-02) + SIM800L GSM**

> Detailed in [`COMMUNICATION.md`](COMMUNICATION.md). Pin map:
>
> | Module | ESP32 pins |
> |---|---|
> | SX1278 | SCK=18, MISO=19, MOSI=23, CS=5, RST=14, DIO0=26 *(shared with IR sensor — use a 2-channel mux if both on same board, or move IR to GPIO35)* |
> | SIM800L | TXD=17 *(conflict with DS18B20 — use a software UART on 25/33)*, RXD=27 *(conflict with RPM — move RPM to GPIO13)*, PWR=15 |
>
> Note: revised final pin map in [`WIRING_DIAGRAM.md`](WIRING_DIAGRAM.md)
> after resolving all conflicts.

---

### 2.11 Power Modules

> Detailed in [`POWER_SYSTEM.md`](POWER_SYSTEM.md).
> Summary:
>
> | Rail | Source | Purpose |
> |---|---|---|
> | 12 V | LiFePO4 | SIM800L, buzzer |
> | 5 V | LM2596 buck | Sensors, LoRa, OLED |
> | 3.3 V | AMS1117 LDO | ESP32, I²C bus, low-power sensors |

---

## 3. I²C Bus Topology

```
                ┌─── ADXL345 (0x53)
                ├─── OLED 0.96" (0x3C)
   ESP32  ──────┤
   SDA/SCL      ├─── (reserved: BME280 for v2)
                └─── (reserved: ADS1115 for v2)
```

Two pull-ups on the bus (10 kΩ each, one at each end), bus length kept under
30 cm. All sensors on the same bus share a 4-pin JST-XH harness to make pod
disassembly a 4-pin operation.

---

## 4. Sensor-Mounting Reference Photo (ASCII)

```
   belt surface ───────────────────────────────►
                                              belt motion
   ┌──┐     ┌──────────────────────────────┐
   │idler    │                              │
   │  │ ══════════════════════════════════ │ ═══════► belt
   │  │     │                              │
   └──┘     └──────────────────────────────┘
       ▲
       │  2 mm gap (magnet ring)
   ┌───┴───┐
   │ HALL  │    bolt to take-up frame
   └───────┘
                  ┌──────────┐
                  │ POD      │ ◄── hinged door (Torx-20)
                  │  • ADXL  │     silicone gasket, IP67
                  │  • HX711 │
                  │  • DS18  │     cables through M12 glands
                  │  • MQ-2  │         (1× power, 4× sensor)
                  │  • OLED  │
                  │  • LoRa  │     antenna: SMA to N-type
                  │  • SIM   │     bulkhead on side wall
                  └─────┬────┘
                        │  2 m shielded, 4-conductor
                        ▼
                 [solar pod on tunnel roof]
```

---

## 5. Sensor Survival Checklist

| Threat | Mitigation in this design |
|---|---|
| Coal dust ingress | PTFE membrane over dust sensor, IP67 box, sintered bronze vents |
| Water spray | M12 IP67 connectors, cable glands, conformal coat, downward-facing drain holes |
| Rock impact | Die-cast aluminium box (3 mm wall), polycarbonate window, 6 mm thick |
| Heat | Sensors rated -40 to +85 °C; pod mounted in shade |
| Vibration | Rubber isolators (Sorbothane 30 durometer, 5 mm) between bracket and box |
| EMI from VFD | Shielded twisted pairs, on-board TVS diodes on every external pin |
| Corrosion | Stainless 316 brackets, gold-plated SMA, conformal coat (HumiSeal 1A33) |
| Rodent damage | Armoured cable (steel-wire braided) on the solar-pod link |

---

**Next file:** [`POWER_SYSTEM.md`](POWER_SYSTEM.md).