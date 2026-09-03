# Smart Mine Conveyor-Belt Health-Monitor — Hardware Design

> **Goal:** Continuously monitor the mechanical & thermal health of a coal/iron-ore
> conveyor belt in a remote underground / open-cast mine and transmit live data
> wirelessly to the maintenance cabin — replacing the current "one human watches
> with eyes" inspection model that has failed repeatedly (belt blasts / fires).
>
> **Scope of this document:** Hardware only. Sensors, MCU, wiring, power, RF,
> enclosure, mounting. The firmware team handles the ESP32 code separately.

---

## 1. High-Level Architecture

The system is split into three physical zones:

```
┌──────────────────────────────────────────┐    LoRa / GSM     ┌──────────────────────────┐
│   ZONE A — BELT-MOUNTED SENSOR POD       │   (433/868/915MHz)│  ZONE C — MAINTENANCE    │
│   (IP67 die-cast box clamped to belt     │ ════════════════► │  STATION (in cabin)      │
│    frame, between idlers)                │                   │  - LoRa gateway          │
│                                          │                   │  - Dashboard / siren    │
│  • ESP32-WROOM-32 main MCU                │                   │  - Solar + battery       │
│  • Vibration (SW-420 / ADXL345)           │                   └──────────────────────────┘
│  • Strain Gauge + HX711 (belt tension)    │
│  • NTC 100k + DS18B20 (temp / fire)      │   GSM SMS fallback
│  • Hall-effect RPM sensor (speed)         │ ════════════════►  Cloud / Phone alerts
│  • IR / inductive belt-tear sensor        │
│  • Current sensor ACS712 (motor load)    │
│  • Dust sensor GP2Y1010AU0F (PM/coal)    │
│  • MQ-2 / MQ-135 (CH4, smoke, CO)        │
│  • Buzzer + local OLED                    │
│  • Buck converter + BMS + Li-ion         │
└──────────────────────────────────────────┘
            ▲
            │ low-voltage cable (V+, GND) — optional, otherwise solar pod is
            │   fully self-contained.
┌──────────────────────────────────────────┐
│   ZONE B — SOLAR POD (mounted on tunnel  │
│   roof / pole, 5–10 m from belt)         │
│   • 20 W mono solar panel                 │
│   • MPPT charge controller                │
│   • 12 V / 20 Ah LiFePO4 battery         │
│   • 5 V & 3.3 V buck converters          │
└──────────────────────────────────────────┘
```

The belt pod and the solar pod are connected by a single 2-conductor IP67
cable carrying 12 V. Everything else is local.

---

## 2. System Block Diagram (Mermaid)

```mermaid
flowchart TB
  subgraph SP["☀ SOLAR POD"]
    PV["20W Mono Solar Panel"]
    MPPT["MPPT Charge Controller"]
    BAT["12V 20Ah LiFePO4"]
    BC5["5V Buck (LM2596)"]
    BC3["3.3V LDO (AMS1117)"]
  end

  subgraph BP["📦 BELT-MOUNTED POD (IP67)"]
    MCU["ESP32-WROOM-32"]
    LORA["LoRa SX1278 / RA-02"]
    GSM["SIM800L GSM Module"]
    VIB["Vibration Sensor"]
    STR["Strain Gauge + HX711"]
    TMP["DS18B20 + NTC"]
    RPM["Hall-Effect RPM"]
    IR["IR Belt-Tear Sensor"]
    CUR["ACS712 Current Sensor"]
    DUST["GP2Y1010AU0F Dust"]
    GAS["MQ-2 / MQ-135 Gas"]
    BUZ["Buzzer / Siren"]
    OLED["OLED 0.96\" Display"]
  end

  subgraph MS["🏠 MAINTENANCE STATION"]
    GW["LoRa Gateway + ESP32"]
    DSH["Dashboard / PC"]
    SRN["Cabin Siren"]
  end

  PV --> MPPT --> BAT --> BC5 --> BC3
  BC5 -- 5V --> MCU
  BC3 -- 3.3V --> MCU
  BC5 -- 5V --> LORA
  BAT -- 12V --> GSM
  BC3 -- 3.3V --> VIB
  BC3 -- 3.3V --> TMP
  BC3 -- 3.3V --> RPM
  BC3 -- 3.3V --> STR
  BC3 -- 3.3V --> IR
  BC3 -- 3.3V --> CUR
  BC3 -- 3.3V --> DUST
  BC3 -- 5V via boost --> GAS
  MCU --> LORA -.LoRa.-> GW --> DSH
  MCU --> BUZ
  MCU --> OLED
  MCU -.SMS fallback.-> GSM
  MCU -->|alarm| SRN
```

---

## 3. Design Philosophy

| Concern | How it is solved |
|---|---|
| **Harsh environment** (dust, water, vibration, falling rocks) | IP67 die-cast aluminium box, conformal coating on every PCB, M12 industrial connectors, vibration-isolated mounting brackets. |
| **No mains power** | 20 W solar + MPPT + 20 Ah LiFePO4. Sized for 3-4 days of autonomy (worst-case monsoon week). |
| **No reliable cellular** | LoRa SX1278 primary link (no SIM, no monthly cost, works underground if antenna is routed to surface). SIM800L GSM is **only** an emergency fallback. |
| **Belt blast / fire** | Redundant sensors: temp + smoke + gas + dust. Any two tripping = alarm. |
| **False alarms** | Sensor fusion on ESP32 — vibration RMS, belt-tension trend, temperature delta, RPM slip ratio. |
| **Remote location, no IT staff** | Watchdog timer, OTA via LoRa, modular sensor arrays that can be swapped with one Torx driver. |
| **Long life** | Industrial-grade parts only (≥ -40 °C to +85 °C). No electrolytics near heat sources. |

---

## 4. Subsystem Index

The detailed design for each subsystem lives in its own file so the firmware
team can read them independently:

| File | What it covers |
|---|---|
| [`SENSOR_DESIGN.md`](SENSOR_DESIGN.md) | Every sensor, why it is chosen, how it is wired, where it is mounted. |
| [`POWER_SYSTEM.md`](POWER_SYSTEM.md) | Solar sizing, charge controller, battery, buck converters. |
| [`COMMUNICATION.md`](COMMUNICATION.md) | LoRa link budget, GSM fallback, antennas, gateway. |
| [`ENCLOSURE_DESIGN.md`](ENCLOSURE_DESIGN.md) | Box, IP rating, gasket, mounting brackets, cable glands. |
| [`WIRING_DIAGRAM.md`](WIRING_DIAGRAM.md) | Full pin-map, colour code, complete ASCII wiring. |
| [`BOM.md`](BOM.md) | Bill of Materials with part numbers, qty, approx cost. |
| [`INSTALLATION.md`](INSTALLATION.md) | How to bolt it onto a running belt. |

---

## 5. Specification Snapshot

| Parameter | Value |
|---|---|
| Supply voltage (input) | 12 V DC from solar pod |
| Supply voltage (internal rails) | 5 V, 3.3 V |
| Continuous load (avg) | ~250 mA @ 5 V (ESP32 + sensors) |
| Peak load (TX burst) | ~600 mA @ 5 V (LoRa +20 dBm) |
| Solar autonomy | ≥ 96 h (no sun, full alarm mode) |
| RF range (LoRa, SF12, 868 MHz) | 2–5 km in open-pit, ~500 m with one rock-wall |
| RF range (GSM) | wherever 2G exists (SIM800L) |
| Operating temp | -20 °C to +70 °C (LiFePO4 limit) |
| IP rating of belt pod | IP67 |
| Enclosure material | Die-cast aluminium, RAL 9005 powder coat |
| Service interval | 6 months (dust-clean, re-torque, antenna inspect) |
| MTBF target | ≥ 50 000 h |

---

## 6. Failure Modes & Redundancy Matrix

| Failure | Detection | Redundancy / Action |
|---|---|---|
| Belt tear (longitudinal rip) | IR diffuse-reflective sensor at head pulley | Backup: vibration spike + sudden tension drop → emergency stop |
| Belt fire (friction / coal) | DS18B20 > 70 °C, MQ-2 smoke | Backup: MQ-135 CO/CH4 rise, NTC gradient > 5 °C/min |
| Idler seizure | RPM drop + ACS712 current spike | Backup: vibration RMS rise |
| Belt slip | RPM vs drive-pulley RPM divergence | Backup: tension drop + current drop |
| Bearing failure | Vibration RMS / kurtosis rise at 1× and 3× RPM | Backup: acoustic emission via MEMS mic (planned v2) |
| Power outage | Battery voltage < 11.0 V | Reduce TX rate to 1/min, disable OLED backlight, shut off GSM |
| Pod electronics death | Watchdog timeout | Local buzzer on separate rail; if no LoRa heartbeat for 5 min, cabin raises alarm |

---

## 7. Why this hardware works in a remote mine

1. **No human in the loop for safety.** The pod decides locally; it only asks
   the human to come fix it.
2. **Survives months unattended.** IP67 + conformal coat + LiFePO4 (no thermal
   runaway) + solar autonomy.
3. **Communicates over rock.** LoRa at SF12/BW125 has ~130 dB link budget — it
   penetrates wet rock far better than Wi-Fi/cellular, and works in tunnels if
   you bring the antenna to the portal.
4. **Fails loudly, never silently.** Local buzzer + cabin siren + SMS + OLED,
   so any single-point failure still produces an alarm path.

---

**Next file:** [`SENSOR_DESIGN.md`](SENSOR_DESIGN.md) — every sensor, one by one.