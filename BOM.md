# Bill of Materials (BOM)

Two BOMs are listed:

1. **BOM-A** — single belt pod + solar pod + maintenance cabin gateway.
   The "demo kit" you can build today.
2. **BOM-B** — same, in flameproof Ex-d enclosure for underground coal
   mines.

Prices are approximate, India-based (Robu, Evelta, Amazon India,
QuartzComponents, etc.) as of late 2025. They exclude PCB fabrication,
3D-printed brackets and labour.

---

## 1. BOM-A — Surface / Open-Pit Demo Kit

### 1.1 Computing & Wireless

| # | Part | Mfr / P/N | Qty | Approx ₹ (ea) |
|---|---|---|---|---|
| 1 | ESP32-WROOM-32 dev kit (30-pin) | Espressif ESP32-DevKitC-32E | 1 | 450 |
| 2 | LoRa RA-02 (SX1278, 868 MHz) | AI-Thinker RA-02 | 1 | 400 |
| 3 | SIM800L module (with SIM holder) | SIMCom SIM800L | 1 | 350 |
| 4 | Micro-SIM card, 1-yr validity | Airtel / Jio IoT SIM | 1 | 200 |

### 1.2 Sensors

| # | Part | Mfr / P/N | Qty | Approx ₹ (ea) |
|---|---|---|---|---|
| 5 | ADXL345 breakout (3-axis) | Adafruit / generic | 1 | 250 |
| 6 | SW-420 vibration module | generic | 1 | 80 |
| 7 | HX711 + 4× BF350 strain gauges | generic | 1 | 350 |
| 8 | DS18B20 (TO-92, stainless probe) | Maxim / Dallas | 2 | 200 |
| 9 | NTC 10 k B=3950 thermistor | generic | 1 | 30 |
| 10 | A3144 Hall sensor (digital) | Allegro A3144 | 1 | 60 |
| 11 | E18-D80NK IR diffuse sensor | generic | 2 | 350 |
| 12 | ACS712-30A current module | Allegro | 1 | 350 |
| 13 | GP2Y1010AU0F dust sensor | Sharp | 1 | 750 |
| 14 | MQ-2 gas sensor module | generic | 1 | 200 |
| 15 | MQ-135 gas sensor module | generic | 1 | 250 |
| 16 | SSD1306 0.96" OLED (I²C) | generic | 1 | 250 |
| 17 | 12 V 110 dB piezo siren | generic | 1 | 350 |

### 1.3 Power Subsystem

| # | Part | Mfr / P/N | Qty | Approx ₹ (ea) |
|---|---|---|---|---|
| 18 | 20 W monocrystalline solar panel | generic (open-pit rated) | 1 | 1800 |
| 19 | EPever Tracer 1210AN MPPT | EPever | 1 | 2200 |
| 20 | 12 V 20 Ah LiFePO4 (with BMS) | DIY Tech / RoHS | 1 | 4500 |
| 21 | 10 W silicone heater pad (12 V) | generic | 1 | 250 |
| 22 | 5 A blade fuse + holder | generic | 1 | 50 |
| 23 | 3 A in-line fuse + holder | generic | 1 | 40 |
| 24 | LM2596-ADJ buck module (12→5 V) | generic | 1 | 80 |
| 25 | LM2596-ADJ buck module (12→4 V) | generic | 1 | 80 |
| 26 | AMS1117-3.3 module | generic | 1 | 30 |
| 27 | MBR2045 Schottky diode | generic | 1 | 20 |
| 28 | SMA-N bulkhead + lightning arrestor | generic | 1 | 350 |
| 29 | 868 MHz 3 dBi fiberglass antenna | generic | 1 | 450 |

### 1.4 Enclosure & Mechanical

| # | Part | Mfr / P/N | Qty | Approx ₹ (ea) |
|---|---|---|---|---|
| 30 | Die-cast AL box 240×160×130 mm | Spelsberg / generic | 1 | 1500 |
| 31 | ABS box 200×150×100 (solar pod) | generic | 1 | 350 |
| 32 | GI pole 50 mm OD × 2 m | generic | 1 | 400 |
| 33 | M10 U-bolts (SS-316) | generic | 4 | 60 |
| 34 | Sorbothane pads 30-duro, 50×50×5 mm | generic | 4 | 80 |
| 35 | M12 IP67 cable glands (4–8 mm) | generic | 7 | 80 |
| 36 | M12 IP67 cable glands (8–12 mm) | generic | 1 | 100 |
| 37 | Gore-Tex PMF100545 breath vent | W.L. Gore | 1 | 350 |
| 38 | Gore-Tex PMF100640 drain vent | W.L. Gore | 2 | 350 |
| 39 | Polycarbonate window 40×25×6 mm | Makrolon AR2 | 1 | 250 |
| 40 | 3M DP-8010 acrylic adhesive | 3M | 1 | 450 |
| 41 | Silicone gasket (per metre) | generic | 2 | 100 |
| 42 | M3 standoffs + screws (kit) | generic | 1 | 100 |
| 43 | Torx-20 security screws (M6×16) | generic | 4 | 30 |

### 1.5 Cabling & Connectors

| # | Part | Qty | Approx ₹ |
|---|---|---|---|
| 44 | Armoured 2-core cable (5 m) | 1 | 350 |
| 45 | Shielded 4-core cable, 22 AWG (2 m) | 1 | 80 |
| 46 | Shielded twisted pair, 18 AWG (20 m) | 1 | 600 |
| 47 | Silicone 2-wire cable (1 m, heat-resistant) | 1 | 60 |
| 48 | LMR-200 coax (0.3 m) | 1 | 100 |
| 49 | MC4 connector pair | 1 | 80 |
| 50 | JST-XH 4-pin connectors (kit) | 1 | 80 |
| 51 | JST-XH 3-pin connectors (kit) | 1 | 50 |
| 52 | Heat-shrink label printer tape | 1 | 200 |
| 53 | Heat-shrink tubing assortment | 1 | 150 |

### 1.6 PCBs & Passives (placeholders — populated in-house)

| # | Part | Qty | Approx ₹ |
|---|---|---|---|
| 54 | ESP32 carrier PCB (custom 4-layer, JLCPCB) | 1 | 350 |
| 55 | 100 nF X7R 0603 (kit of 100) | 1 | 100 |
| 56 | 10 µF tantalum 0805 (kit of 50) | 1 | 100 |
| 57 | 10 kΩ 0603 resistor (kit) | 1 | 80 |
| 58 | 4.7 kΩ 0603 resistor (kit) | 1 | 80 |
| 59 | 1 kΩ 0603 resistor (kit) | 1 | 80 |
| 60 | 2N2222 NPN transistor (kit) | 1 | 50 |
| 61 | AO3401 P-MOSFET (kit) | 1 | 80 |
| 62 | PRTR5V0U2X TVS array | 4 | 200 |
| 63 | BLM18PG471 ferrite (kit) | 1 | 80 |
| 64 | HumiSeal 1A33 conformal coat, 250 ml | 1 | 1200 |
| 65 | SS49E / A3144 magnet ring (8× N52 magnets) | 1 | 250 |

### 1.7 Gateway (cabin side)

| # | Part | Qty | Approx ₹ |
|---|---|---|---|
| 66 | ESP32-WROOM-32 dev kit (cabin gateway) | 1 | 450 |
| 67 | LoRa RA-02 (cabin gateway) | 1 | 400 |
| 68 | 868 MHz 6 dBi Yagi antenna (cabin) | 1 | 1200 |
| 69 | 12 V 5 A relay module | 1 | 200 |
| 70 | 12 V cabin siren + strobe | 1 | 1500 |
| 71 | USB-UART cable (programming) | 1 | 200 |

### 1.8 Total

| Sub-total | ₹ (approx) |
|---|---|
| Computing & Wireless | 1 400 |
| Sensors | 4 470 |
| Power | 9 870 |
| Enclosure & Mechanical | 5 810 |
| Cabling & Connectors | 1 750 |
| PCBs & Passives | 2 540 |
| Gateway | 4 950 |
| **TOTAL (BOM-A)** | **~₹30 790** |
| USD equivalent (1 USD ≈ 84 INR) | **~$370** |

---

## 2. BOM-B — Underground Coal-Mine Compliant (Ex-d)

Differences from BOM-A only — every line below *replaces* the equivalent
line in BOM-A.

| Line | Change | Approx extra cost |
|---|---|---|
| 30 | Replace AL box with **CMP Ex-d IIB T6** certified enclosure (~3× cost) | + ₹8 000 |
| 35–36 | Replace M12 glands with **Hawke A711** Ex-d glands | + ₹1 500 |
| New | Add **zener-diode IS barriers** on every external sensor lead | + ₹2 500 |
| New | Add **GFL-series flameproof cable** for the solar link | + ₹1 500 |
| New | Add **flameproof junction box** at the solar pod | + ₹3 000 |
| New | Certification: PESO / DGMS testing fee | + ₹50 000 |
| **TOTAL (BOM-B, per pod)** | | **~₹98 000** |

---

## 3. Per-Component Justification (highlights)

### 3.1 Why ESP32-WROOM-32 (not ESP32-S3, not ESP8266)

- **Wi-Fi + BLE + SPI + I²C + ADC + DAC + capacitive touch** in one chip.
- Dual-core 240 MHz — fast enough for vibration FFT in firmware.
- Built-in crypto accelerators for OTA signing.
- ₹450 vs ₹150 for ESP8266 — but the extra peripherals save 2 chips
  and a level-shifter.
- ESP32-S3 would be nice for USB-OTG but is ~2× the cost and not
  needed.

### 3.2 Why SX1278 (not SX1262 LoRa 2)

| | SX1278 | SX1262 |
|---|---|---|
| Cost | ₹400 | ₹700 |
| Range (max) | -148 dBm | -148 dBm |
| Spreading factors | SF6–SF12 | SF5–SF12 |
| Bandwidth | 7.8–500 kHz | 7.8–500 kHz |
| India availability | ✅ everywhere | ❌ rare, long lead time |
| Verdict | **Used** | Reserve for v2 |

### 3.3 Why LM2596 (not MP1584, not TPS5430)

- ₹80 ready-made module.
- 3 A capability — plenty of headroom for LoRa + GSM peaks.
- Wide input (up to 40 V) — handles solar panel voltage spikes.
- All junior engineers know it.

### 3.4 Why LiFePO4 (not Li-Po, not lead-acid)

See [`POWER_SYSTEM.md`](POWER_SYSTEM.md). Summary: long cycle life
(2000+), no thermal runaway, safe in coal-mine temperatures.

### 3.5 Why AI-Thinker RA-02 (not Dragino, not NiceRF)

- Cheapest LoRa module on the Indian market.
- Standard pinout, community firmware available.
- SMA-K female onboard — easy external antenna connection.

### 3.6 Why SIM800L (not SIM7600, not BG95)

See [`COMMUNICATION.md`](COMMUNICATION.md). Summary: cheapest,
2G-rural-friendly, low-power, sufficient for SMS-only emergency
fallback.

### 3.7 Why Adafruit-style ADXL345 (not MPU6050, not LIS3DH)

- 3-axis, 16 g range.
- Better low-g noise than MPU6050 (60 µg/√Hz vs 400 µg/√Hz).
- I²C interface (MPU6050 also has I²C but more configuration hassle).

### 3.8 Why HX711 (not ADS1220, not NAU7802)

- Onboard regulated excitation (avoids needing an extra LDO).
- 24-bit ADC, 10/80 SPS.
- Plug-in modules everywhere for ₹350.
- TI/ADS would double the BOM.

### 3.9 Why GP2Y1010AU0F (not PMS5003, not SDS011)

- GP2Y is optical + simple analog output; PMS5003 is laser particle
  counter with UART and is **10×** the cost.
- Coal dust is large particles (>10 µm) — GP2Y covers that range well.
- PMS5003 is for PM2.5 air-quality, which we don't need.

### 3.10 Why Sharp GP2Y + MQ, not a single BME680

BME680 is a Bosch combo sensor (T/H/P/gas). It is great for indoor
air-quality, but:

- Its gas sensor is sensitive to VOCs, not to CH₄ or smoke at the
  levels we care about.
- Its T/H readings would couple to the case electronics.
- A separate MQ-2 catches **combustion smoke** specifically, which
  is what we want for early fire detection.

---

## 4. Where to Buy (India)

| Component | Recommended vendor |
|---|---|
| ESP32 / LoRa / sensors | Robu.in, QuartzComponents, Evelta |
| Solar panel / MPPT | Loom Solar, Sungrids, Amazon |
| LiFePO4 battery | Renergy Power, Waaree, Loom Solar |
| Die-cast AL box | element14 India, Farnell, Amazon |
| Conformal coat | Digikey India, Element14 |
| Gore vents | Almarc (India distributor) |
| Ex-d enclosure (BOM-B) | Flameproof Equipment Pvt Ltd, Baliga |

---

## 5. What's NOT in this BOM

- The maintenance-cabin **PC / monitor** (use whatever is on site).
- **Solar panel pole foundation** (concrete / civil works).
- **Network/internet at the cabin** (optional).
- **Spare parts** (recommend keeping 10 % of all FRUs as spares).

---

**Next file:** [`INSTALLATION.md`](INSTALLATION.md) — how to install on a live belt.