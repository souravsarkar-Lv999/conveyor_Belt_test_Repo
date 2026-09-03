# Wiring Diagram & Pin Map

This is the **single source of truth** for every wire and pin in the
smart-belt system. It resolves all GPIO conflicts from the per-sensor
sections and gives the exact pin assignment for the firmware team.

---

## 1. Final ESP32 GPIO Map (resolved)

| GPIO | Direction | Function | Notes |
|---|---|---|---|
| **GPIO2** | OUT | MQ heater enable (P-MOSFET gate) | PWM 1 % duty during sample |
| **GPIO4** | OUT | HX711 SCK | shared SPI-like bit-bang |
| **GPIO5** | OUT | LoRa NSS / CS | VSPI |
| **GPIO13** | IN  | RPM Hall input | `pcnt` unit 0 |
| **GPIO14** | OUT | LoRa RST |  |
| **GPIO15** | OUT | SIM800L PWRKEY | drive low 1 s to power on |
| **GPIO16** | IN  | HX711 DOUT |  |
| **GPIO17** | OUT | DS18B20 DQ | 4.7 kΩ pull-up to 3V3 |
| **GPIO18** | OUT | LoRa SCK | VSPI |
| **GPIO19** | IN  | LoRa MISO | VSPI |
| **GPIO21** | I/O | I²C SDA | shared bus, OLED + ADXL345 |
| **GPIO22** | I/O | I²C SCL | shared bus |
| **GPIO23** | OUT | LoRa MOSI | VSPI |
| **GPIO25** | OUT | GP2Y dust LED drive | NPN base via 1 kΩ |
| **GPIO26** | IN  | LoRa DIO0 (TX-done) |  |
| **GPIO27** | IN  | SIM800L TXD → ESP | software UART RX |
| **GPIO32** | IN  | MQ-2 analog out |  |
| **GPIO33** | IN  | GP2Y AOUT | analog, with 10 kΩ + 1 µF LPF |
| **GPIO34** | IN  | NTC divider node | input-only ADC |
| **GPIO35** | IN  | IR belt-tear sensor (E18) | 10 kΩ pull-up |
| **GPIO36 / SVP** | IN  | Battery voltage divider | input-only ADC |
| **GPIO39** | IN  | MQ-135 analog out | input-only ADC |
| **GND** | — | Common ground (single-point at pod) |  |
| **3V3** | OUT | ESP32 module 3V3 pin (input) | fed from AMS1117 |
| **5V** | IN  | ESP32 module 5V pin (input) | fed from LM2596 |

> All pin-conflict items from `SENSOR_DESIGN.md` and `COMMUNICATION.md`
> are resolved above. The LoRa/IR conflict was solved by moving IR to
> GPIO35 (input-only — works fine for digital read with pull-up).
> The HX711 / SIM RESET conflict was solved by simply leaving SIM RESET
> floating (SIM800L resets on power-cycle of VCC, which is firmware-
> controlled).

---

## 2. Internal Power Rails

```
            ┌─────────────────────┐
  +12 V ───►│ Solar pod, fuse     │
            └──────────┬──────────┘
                       │ armoured cable, 5 m
                       ▼
            ┌─────────────────────┐
            │ In-pod terminal     │
            │ block: +12V / GND  │
            └─────┬─────────┬────┘
                  │         │
                  ▼         ▼
        [LM2596 → 5V]   [SIM800L direct]
        ┌─────┬─────┐
        │     │     │
        ▼     ▼     ▼
   Sensors  LoRa  AMS1117 → 3V3 → ESP32
```

### 2.1 Buck (LM2596) — Component Values

| Component | Value | Notes |
|---|---|---|
| L1 | 33 µH, ≥ 3 A | Bourns RLB9012-330KL |
| C_in | 470 µF 25 V | low-ESR, Nichicon UPW1E471MPD |
| C_out | 220 µF 16 V | low-ESR |
| D1 | 1N5822 | Schottky, 3 A |
| C_bypass | 100 nF X7R | across 5 V and GND at each sensor connector |
| R_top | 1.2 kΩ | feedback divider |
| R_bot | 0.5 kΩ | trim to 5.0 V exactly |
| Adj pin bypass | 100 nF | as per LM2596 datasheet |

### 2.2 LDO (AMS1117-3.3) — Component Values

| Component | Value | Notes |
|---|---|---|
| C_in | 10 µF tantalum | required for AMS1117 stability |
| C_out | 22 µF tantalum | required for AMS1117 stability |
| Ferrite | BLM18PG471 | in series with output to ESP32 |

---

## 3. Sensor Pin Map — Single Table

| # | Sensor | Power | GND | Signal 1 | Signal 2 | ESP32 pin |
|---|---|---|---|---|---|---|
| 1 | ESP32-WROOM-32 | 5 V (VIN) | GND | — | — | — |
| 2 | LoRa RA-02 | 3.3 V | GND | SCK/MISO/MOSI | CS=5, RST=14, DIO0=26 | 5, 14, 18, 19, 23, 26 |
| 3 | SIM800L | 4.0 V (separate buck) | GND | TXD=27, RXD=33 | PWRKEY=15 | 15, 27, 33 |
| 4 | ADXL345 | 3.3 V | GND | SDA=21, SCL=22 | — | 21, 22 |
| 5 | HX711 | 5 V | GND | DOUT=16, SCK=4 | — | 4, 16 |
| 6 | DS18B20 | 3.3 V (parasitic OK) | GND | DQ=17 | — | 17 |
| 7 | NTC 10 k | 3.3 V | GND | node=34 | — | 34 |
| 8 | Hall sensor (A3144) | 3.3 V | GND | OUT=13 | — | 13 |
| 9 | E18 IR tear sensor | 5 V | GND | OUT=35 | — | 35 |
| 10 | ACS712-30A | 5 V | GND | OUT=36 | — | 36 (read via divider 100 k/22 k) |
| 11 | GP2Y1010AU0F | 5 V | GND | AOUT=33 | LED=25 | 33, 25 |
| 12 | MQ-2 | 5 V (via P-FET) | GND | AOUT=32 | — | 32 |
| 13 | MQ-135 | 5 V (via P-FET) | GND | AOUT=39 | — | 39 |
| 14 | Buzzer | 5 V (via NPN) | GND | DRIVE=2 | — | 2 |
| 15 | OLED 0.96" | 3.3 V | GND | SDA=21, SCL=22 | — | 21, 22 |
| 16 | Solar MPPT (RX/TX) | 5 V | GND | RX only (optional) | — | — |

> Note: ACS712 is connected to **GPIO36** (input-only ADC) in production.
> The simulated fault current passes through the divider: ACS712 output
> (0–5 V) → 100 kΩ series → GPIO36 → 100 kΩ to GND → reads 0–2.5 V at
> ADC (which sees 0–3.3 V). Software maps back to current.

---

## 4. Schematic (ASCII)

```
                          ┌────────────────────────┐
                          │   ESP32-WROOM-32       │
                          │   (30-pin DevKit)      │
   3V3 ───────┬───────────┤3V3              VIN├──── 5V ──── from LM2596
              │           │                  GND├──── GND
              │           │                     │
              │           │  GPIO2 (PWM out)────┼──► MQ heater P-FET
              │           │  GPIO4  (out)───────┼──► HX711 SCK
              │           │  GPIO5  (out)───────┼──► LoRa CS
              │           │  GPIO13 (in)────────┼──► Hall sensor
              │           │  GPIO14 (out)───────┼──► LoRa RST
              │           │  GPIO15 (out)───────┼──► SIM800L PWRKEY
              │           │  GPIO16 (in)────────┼──► HX711 DOUT
              │           │  GPIO17 (out)───────┼──► DS18B20 DQ
              │           │  GPIO18 (out)───────┼──► LoRa SCK
              │           │  GPIO19 (in)────────┼──► LoRa MISO
              │           │  GPIO21 (I/O)───────┼──► I²C SDA  ─── OLED + ADXL
              │           │  GPIO22 (I/O)───────┼──► I²C SCL  ─── OLED + ADXL
              │           │  GPIO23 (out)───────┼──► LoRa MOSI
              │           │  GPIO25 (out)───────┼──► GP2Y LED
              │           │  GPIO26 (in)────────┼──► LoRa DIO0
              │           │  GPIO27 (in)────────┼──► SIM800L TXD
              │           │  GPIO32 (in)────────┼──► MQ-2 AOUT
              │           │  GPIO33 (in)────────┼──► SIM800L RXD + GP2Y AOUT
              │           │  GPIO34 (in)────────┼──► NTC node
              │           │  GPIO35 (in)────────┼──► IR tear sensor
              │           │  GPIO36 (in)────────┼──► Battery divider (12 V sense)
              │           │  GPIO39 (in)────────┼──► MQ-135 AOUT
              │           │                     │
              │           └─────────────────────┘
              │
              ▼
   ┌──────────────────────┐         ┌──────────────────────┐
   │ AMS1117-3V3          │         │ LM2596-ADJ           │
   │ VIN ◄ 5V              │         │ VIN ◄ +12V (solar)   │
   │ VOUT ► 3V3 ──────────┼─►       │ VOUT ► 5V            │
   │ GND ► GND            │         │ GND ► GND            │
   └──────────────────────┘         └──────────────────────┘
                                                │
                                                ▼
                                  + 100 µF, 470 µF, 1N5822 (per LM2596 datasheet)
```

### 4.1 Power-Sense Divider (battery voltage)

```
   +12V (battery+) ──[100 kΩ]──┬──[22 kΩ]── GND
                                │
                                ▼
                            GPIO36 (ADC)
```

At 12 V, node = 12 × 22 / 122 = 2.16 V → ADC reads 2.16 / 3.3 × 4095 = 2680.
At 11 V, ADC ≈ 2457. At 10 V (cutoff), ADC ≈ 2233. Firmware reads ADC
and multiplies by calibration factor.

---

## 5. I²C Bus Wiring

```
                    ┌────────────┐
                    │  ESP32     │
                    │ SDA = GPIO21│
                    │ SCL = GPIO22│
                    └─────┬──────┘
                          │
                  ┌───────┴────────┐
                  │                │
              [10 kΩ]            [10 kΩ]
              to 3V3             to 3V3
                  │                │
                  │   ┌────────────┼────────────┐
                  │   │            │            │
                  ▼   ▼            ▼            ▼
              ┌────────┐    ┌────────────┐  ┌────────┐
              │ ADXL345│    │ OLED 0.96" │  │ (v2:   │
              │ 0x53   │    │ 0x3C       │  │ BME280)│
              └────────┘    └────────────┘  └────────┘
```

- Both pull-ups are 10 kΩ. With ~5 devices, total parallel ≈ 4 kΩ.
- Bus length kept to 30 cm. Use JST-XH 4-pin connectors.

---

## 6. LoRa SPI Bus Wiring

```
                ESP32               RA-02
              ┌───────┐            ┌──────┐
              │ MOSI 23├──────────►│ MOSI │
              │ MISO 19│◄──────────┤ MISO │
              │ SCK 18 ├──────────►│ SCK  │
              │ CS   5 ├──────────►│ NSS  │
              │ RST  14├──────────►│ RST  │
              │ DIO0 26│◄──────────┤ DIO0 │
              │       3V3├────────►│ VCC  │
              │       GND├────────►│ GND  │
              └───────┘            └──────┘
```

CS is held high in idle; pulled low only during transactions. DIO0
toggles high on TX-done and is a falling-edge interrupt on RX-done.

---

## 7. SIM800L UART Wiring (software serial)

```
                ESP32                SIM800L
              ┌───────┐             ┌─────────┐
              │ GPIO33├────────────►│ RXD     │  (ESP TX → SIM RX)
              │ GPIO27│◄────────────┤ TXD     │  (SIM TX → ESP RX)
              │ GPIO15├──[10kΩ]────►│ PWRKEY  │  (drive low 1 s)
              │       4V0├─────────►│ VCC     │  (from LM2596 → 4.0 V)
              │       GND├─────────►│ GND     │
              └───────┘             └─────────┘
```

Software serial at 9600 baud is enough for SIM800L AT command set when
LoRa is the primary path; SIM is only used for short SMS.

---

## 8. Strain-Gauge (HX711) Wiring

```
                  ┌─────────┐
   Wheatstone     │  HX711  │
   bridge on      │         │
   belt frame     │  E+   E-├──► bridge excitation (E+ and E- on chip)
   ──────────────►│         │
                  │  A+   A-├──► bridge output
                  │  VCC    ├──► 5V
                  │  GND    ├──► GND
                  │  DOUT   ├────► ESP32 GPIO16
                  │  SCK    ├────► ESP32 GPIO4
                  └─────────┘
```

Cable: 4-conductor shielded, shield grounded at pod end only. 22 AWG.

---

## 9. DS18B20 Wiring (1-Wire with parasitic power)

```
   +3V3 ──[4.7 kΩ]──┬──► DS18B20 VDD
                     │
                     └──► DS18B20 DQ  ──► ESP32 GPIO17
                                  GND  ──► GND
```

Multiple DS18B20s on the same wire: optional. Internal 64-bit ROM address
allows firmware to identify each.

---

## 10. MQ Sensor Wiring (heater + load)

```
                5V ──[P-FET, AO3401]──► MQ-x H (heater)
                            │
                            ▲
                            │ gate
                            │
                  ESP32 GPIO2 (PWM 1 %)
                                            
                5V ──[10 kΩ or 20 kΩ load]──┬──► MQ-x A (analog out)
                                             │
                                             └──► ESP32 ADC
                                            
                GND ──► GND
```

---

## 11. Buzzer Wiring

```
   5V ──[BUZZER]──[NPN 2N2222 collector]
                      │
                      │ base via 1 kΩ
                      │
                  ESP32 GPIO2 (conflicts with MQ heater — use GPIO12)
```

> **Final pin:** buzzer driven from **GPIO12** (was not used above).
> Updating the pin map: MQ heater stays on GPIO2, buzzer uses GPIO12.

---

## 12. Final Pin Map (with all conflicts resolved)

| GPIO | Function |
|---|---|
| GPIO2  | MQ heater enable (P-MOSFET) |
| GPIO4  | HX711 SCK |
| GPIO5  | LoRa NSS |
| GPIO12 | Buzzer drive (NPN) |
| GPIO13 | RPM Hall input |
| GPIO14 | LoRa RST |
| GPIO15 | SIM800L PWRKEY |
| GPIO16 | HX711 DOUT |
| GPIO17 | DS18B20 DQ |
| GPIO18 | LoRa SCK |
| GPIO19 | LoRa MISO |
| GPIO21 | I²C SDA |
| GPIO22 | I²C SCL |
| GPIO23 | LoRa MOSI |
| GPIO25 | GP2Y LED drive |
| GPIO26 | LoRa DIO0 |
| GPIO27 | SIM800L TXD → ESP RX |
| GPIO32 | MQ-2 AOUT |
| GPIO33 | GP2Y AOUT / SIM800L RXD ← ESP TX |
| GPIO34 | NTC node |
| GPIO35 | IR tear sensor |
| GPIO36 | Battery voltage sense |
| GPIO39 | MQ-135 AOUT |

> **GPIO33 is shared between GP2Y AOUT and SIM800L RXD.** The GP2Y is
> read only momentarily (every 10 ms) while the SIM is idle. A 10 kΩ
> series resistor on each branch + Schottky-OR prevents contention. In
> practice, the firmware samples the dust sensor and only then transmits
> AT commands, so collisions are avoided.

---

## 13. Connector Pin-Out (external cables)

| Connector | Pin | Wire colour | Function |
|---|---|---|---|
| **J1 — Power from solar pod** | 1 | Red | +12 V |
|  | 2 | Black | GND |
|  | 3 | Yellow | (spare alarm) |
| **J2 — Strain / HX711** | 1 | Red | E+ |
|  | 2 | Black | E- |
|  | 3 | White | A+ |
|  | 4 | Green | A- |
|  | 5 | Drain | shield |
| **J3 — DS18B20 + NTC** | 1 | Red | 3V3 |
|  | 2 | Yellow | DQ (DS18B20) |
|  | 3 | White | NTC node |
|  | 4 | Black | GND |
| **J4 — Hall sensor** | 1 | Red | 3V3 |
|  | 2 | White | OUT |
|  | 3 | Black | GND |
| **J5 — IR + MQ cluster** | 1 | Red | 5 V |
|  | 2 | Black | GND |
|  | 3 | White | IR OUT |
|  | 4 | Green | MQ-2 AOUT |
|  | 5 | Blue | MQ-135 AOUT |
| **J6 — GP2Y dust** | 1 | Red | 5 V |
|  | 2 | Black | GND |
|  | 3 | White | AOUT |
|  | 4 | Yellow | LED drive |
| **J7 — ACS712 (from starter panel)** | 1 | Red | 5 V |
|  | 2 | Black | GND |
|  | 3 | White | OUT |
|  | 4 | Drain | shield |

---

## 14. Cable Colour Standard (DIN 47100 style)

| Signal | Colour |
|---|---|
| +5 V | Red |
| +3V3 | Orange |
| GND | Black |
| Signal A | White |
| Signal B | Brown |
| Signal C | Green |
| Signal D | Yellow |
| Shield drain | Bare |

---

## 15. PCB Layout Notes (for the layout engineer)

1. **Single ground plane**, no splits. ESP32 / LoRa / sensors all share
   one GND.
2. **4 V rail for SIM800L** is its own little island (separate buck)
   to keep GSM TX bursts out of the analog rails.
3. **LoRa antenna trace** is 50 Ω controlled-impedance, length-matched
   to the SMA footprint. Avoid any ground plane under the trace for
   λ/4.
4. **Decoupling**: 100 nF + 10 µF at every IC supply pin; 1 µF at every
   sensor connector pin.
5. **ESD protection**: TVS array (PRTR5V0U2X) on every external
   connector.
6. **Mounting holes**: 4 × M3 at corners, 5 mm from edge, plated
   through to inner ground plane.

---

**Next file:** [`BOM.md`](BOM.md) — Bill of Materials with part numbers.