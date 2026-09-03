# Enclosure & Mechanical Design

The belt pod lives next to a moving conveyor of coal/iron ore. It sees:

- **Coal dust** (explosive concentration = 50 g/m³, our box is at 0 g/m³)
- **Water spray** from the carry-side wash-down pumps
- **Falling rocks** from transfer chutes
- **Continuous mechanical vibration** (5–15 g peak)
- **Ambient temp** from -10 °C (winter) to +55 °C (summer afternoon)
- **UV** if any part is sun-exposed (rare on the belt, common on the
  solar pod)

The enclosure is rated and built accordingly.

---

## 1. Belt Pod Enclosure

### 1.1 Specifications

| Spec | Value |
|---|---|
| Type | Die-cast aluminium, hinged lid |
| Manufacturer reference | Spelsberg AL-PCB 241613 or equivalent (240 × 160 × 130 mm) |
| Wall thickness | 3 mm cast aluminium |
| Lid | 4 × M6 captive screws (Torx-20 security) |
| Gasket | Silicone closed-cell, 2 mm cross-section, RAL 7001 groove |
| Finish | RAL 9005 (jet black) polyester powder coat, 60 µm |
| IP rating | **IP67** — IEC 60529: dust-tight, immersion to 1 m for 30 min |
| Impact rating | **IK08** (5 J impact, equivalent to 500 g from 1 m) |
| Operating temp | -40 °C to +120 °C enclosure; internal derating to +85 °C |
| Weight | ~2.5 kg empty, ~3.2 kg with PCB + battery cell |

### 1.2 Why Die-Cast Aluminium (not plastic, not steel)

| Material | Verdict |
|---|---|
| Die-cast aluminium | ✅ Heat sink for ESP32/LoRa, EMI shield, rock-resistant |
| ABS plastic | ✗ Soft, UV-degrades, no EMI shield |
| Polycarbonate | ✗ Cracks under rock impact |
| Stainless steel | ✅ But heavy, expensive, hard to machine |
| Fibreglass (SMC) | ✅ But expensive, hard to machine in field |

### 1.3 Internal Layout (top-down view)

```
   ┌────────────────────────────────────────┐  ◄── hinged lid (inside)
   │  ┌──────────────────────────────────┐  │
   │  │  ESP32-WROOM-32 dev board        │  │
   │  │  (mounted on standoffs, M3)      │  │
   │  │                                  │  │
   │  │  LM2596 buck │ AMS1117           │  │
   │  │  ─────────── ─────────           │  │
   │  └──────────────────────────────────┘  │
   │                                          │
   │  LoRa RA-02         SIM800L              │
   │  ┌────┐             ┌────┐               │
   │  │SMA │──antenna    │uFL │──SMA bulkhead │
   │  └────┘             └────┘               │
   │                                          │
   │  HX711 (separate PCB, on isolators)      │
   │                                          │
   │  Terminal blocks for external sensors    │
   │  ─ J1: ADXL345   ─ J4: DS18B20 + NTC     │
   │  ─ J2: HX711     ─ J5: Hall + RPM        │
   │  ─ J3: ACS712    ─ J6: IR tear           │
   │  ─ J7: MQ-2 + MQ-135                    │
   │  ─ J8: GP2Y dust                        │
   │  ─ J9: Buzzer / OLED                     │
   │                                          │
   │  Cable glands (M12 IP67):                │
   │   Ⓒ1: solar-pod power cable             │
   │   Ⓒ2: HX711 shielded cable              │
   │   Ⓒ3: DS18B20 + NTC                     │
   │   Ⓒ4: Hall sensor                       │
   │   Ⓒ5: IR + MQ sensor cluster            │
   │   Ⓒ6: GP2Y dust                         │
   │   Ⓒ7: ACS712 from starter panel         │
   └──────────────────────────────────────────┘
```

### 1.4 Vibration Isolation

- **Sorbothane isolators**, 30 durometer, 5 mm thick, between the
  belt-frame bracket and the pod back-plate.
- These decouple the pod from high-frequency belt-frame vibration while
  still coupling low-frequency signals to the ADXL345.
- The ADXL345 sits on the **outer bracket**, not inside the isolated
  pod — it must sense the belt, not the isolated box.

```
   belt frame ──► [bracket A] ──► ADXL345 (bolted)
                       │
                       └── Sorbothane pad ──► [bracket B] ──► aluminium pod
```

### 1.5 Conformal Coating

Every PCB is dipped in **HumiSeal 1A33** (acrylic, 25 µm dry film):

- Covers solder joints, components, exposed traces.
- Is **not** applied to: connectors, antenna feed, battery contacts,
  MEMS microphone (v2), pressure-sensor port.
- Re-applied after every board repair in the field.

### 1.6 Cable Entries

All cables enter through **M12 IP67 cable glands**, sized to the cable
diameter. Each gland:

- Has a silicone O-ring.
- Has a hex nut torqued to 5 Nm.
- Is fitted with a stress-relief grommet on the inside.

Inside the pod, all cables are clamped to the wall with **P-clips** to
prevent strain on solder joints.

### 1.7 Drainage & Vents

- Two **drain holes** (3 mm) at the lowest point of the pod, fitted with
  Gore-Tex vents (PMF100640) to keep water out but let pressure
  equalise.
- **One-way breath vent** (Bossard GORE PMF100545) on the side wall.

### 1.8 Window for OLED

The lid has a 40 × 25 mm **polycarbonate window** (Makrolon AR2, 6 mm
thick), bonded with **3M DP-8010** structural acrylic. Anti-fog coating
on the inside.

---

## 2. Solar Pod Enclosure

A second, smaller IP66 box on a pole or tunnel roof:

| Spec | Value |
|---|---|
| Box | 200 × 150 × 100 mm ABS, IP66, pole-mount bracket |
| Pole | 50 mm OD GI pipe, 2 m long, 4 × M10 anchor bolts |
| Panel mount | Adjustable tilt bracket, 30° to 60° |
| Battery | Inside the pod, strapped, BMS accessible via door |

### 2.1 Solar Panel Bracket

- 20 W panel mounted on **aluminium U-channel** frame.
- Tilt angle = site latitude − 10° for winter (max harvest when sun is
  low).
- Orient panel **true south** (Northern hemisphere) using compass.
- Hinge + pin allow panel to be tilted down for cleaning without
  removing from pole.

---

## 3. Mounting on the Conveyor

### 3.1 Bracket to Belt Frame

```
   belt frame (C-channel) ──┐
                             │
        ┌────────────────────┘
        │   M10 U-bolt (2×), SS-316
        ▼
   ┌─────────┐
   │ Sorbothane│   5 mm, 30 durometer
   │   pad     │
   └─────┬─────┘
         ▼
   ┌─────────────┐
   │  POD (AL box)│
   └─────────────┘
```

### 3.2 Location Choice (Pod-1: tail pulley)

- Mounted **200 mm below the tail pulley** on the return-side C-channel.
- This gives the strain-gauge a clean lever arm to belt tension.
- Vibration sensor here captures **return-side idler vibration** (best
  signal for early idler-seizure).

### 3.3 Location Choice (Pod-2: head pulley)

- Mounted **2 m before the head pulley** on the carry-side structure.
- The IR belt-tear sensor beams across the belt just before it wraps the
  head pulley (where any tear opens up).
- Gas + smoke sensors are co-located here (rising gas reaches the
  carry-side airspace).

### 3.4 Forbidden Locations

- Directly under the carry-side (coal dust + rock impact).
- On the return-side past the take-up pulley (high tension, mount would
  tear off).
- Inside the skirt (heat + dust + impingement).
- On a structural member that vibrates at 50 Hz from mains harmonics
  (would mask bearing-frequency vibration).

---

## 4. Thermal Management

| Risk | Mitigation |
|---|---|
| ESP32 overheating in summer | Die-cast box acts as a heat sink; ESP32 thermal-padded to box wall |
| Battery cold-soak in winter | Internal heater pad on battery compartment (powered from solar pod, thermostat at 5 °C) |
| Solar panel covered in coal dust | Smooth glass surface; cleaned monthly; rain has self-cleaning effect on tilted panel |
| MQ sensor condensation in humid pit | Sintered bronze vent + heater on 1 % duty for 30 s each hour to dry sensor head |

---

## 5. Explosion Protection (Coal-Mine Compliance)

Indian coal mines are **Category 1, Zone 0/1** for methane. Strict
regulations apply to anything electrical underground.

This hardware is designed to be installed in the **return-side tunnel
surround** which is typically **Zone 1** (gas present intermittently),
but it is **flameproof-caged** and **intrinsically safe** at the
sensor leads by design. Compliance pathway:

| Approach | Implementation |
|---|---|
| **Flameproof enclosure** (IS/IEC 60079-1) | All electronics in certified Ex-d IIB T6 box (e.g., CMP/Phoenix Contact). Order as an option. |
| **Intrinsic safety barriers** (IS/IEC 60079-11) | Zener-diode barriers on every external sensor lead that crosses into Zone 0 |
| **Cable sealing** | All entries through certified Ex-d cable glands (e.g., Hawke A711) |
| **Surface-mount only** | For open-cast / surface belts, standard IP67 box (cheaper) suffices; no Ex certification required |

**For the demo / first install**, target **open-cast (surface) belts**
where standard IP67 + intrinsically-safe sensor-side design is enough.
For underground deployment, swap to the certified Ex-d pod (same PCB,
different box).

---

## 6. Label & Marking

Each pod has a laser-engraved plate:

```
   ┌──────────────────────────────────────────┐
   │  SMART BELT MONITOR — POD Mk1            │
   │  S/N:  SB-2026-001                       │
   │  Installed:  2026-09-03                  │
   │  Site:       Pit-3, Conveyor-A            │
   │  LoRa ID:    0x42                        │
   │  Battery:    12V 20Ah LiFePO4            │
   │  Mfg:        [your company]              │
   │  ⚠  High voltage — disconnect before open│
   └──────────────────────────────────────────┘
```

A second plate shows **wiring diagram** + **QR code** linking to the
online manual.

---

## 7. Maintenance Window

- Hinged lid opens with **4 security Torx-20 screws** (anti-tamper).
- Internal access: 30 seconds with the right tool.
- Field-replaceable units (FRUs): sensors, antennas, battery pack,
  PCB. PCB can be swapped without removing the box from the bracket
  (4 internal screws + 4 connectors).
- Spare-gland kit included with each pod for one field cable change.

---

## 8. Cabling Strategy

| Cable type | From | To | Length | Notes |
|---|---|---|---|---|
| Armoured 2-core | Solar pod | Belt pod | 5 m | Steel-wire braid, rodent-proof |
| Shielded 4-core | Belt frame | HX711 strain | 2 m | 22 AWG, foil + braid shield |
| Shielded 2-core (twisted pair) | Starter panel | ACS712 | 20 m | 18 AWG, foil shield |
| 2-wire silicone | Belt underside | DS18B20 + NTC | 1 m | Heat-resistant |
| 3-wire shielded | Take-up shaft | Hall sensor | 1.5 m | 24 AWG |
| 4-wire | Head-pulley frame | IR + MQ cluster | 1.5 m | 22 AWG |
| 2-wire | Solar pole | Solar pod | 1 m | UV-resistant outer jacket |
| Antenna coax | LoRa RA-02 | External antenna | 0.3 m | LMR-200 |

Every cable has a **printed heat-shrink label** at both ends with cable
ID and termination point.

---

## 9. Acceptance Test (after install)

A field-eng team runs through this 10-minute test before signing off:

1. Power-up via battery — verify OLED shows "BOOT OK".
2. Send "ALARM TEST" from cabin — verify pod buzzes + cabin siren fires.
3. Press the local button on the pod — verify status blinks.
4. Apply heat from a lighter near DS18B20 — verify temp rises > 5 °C
   in 10 s and "TEMP WARN" appears on cabin dashboard.
5. Vibrate the bracket by hand — verify "VIB" message reaches cabin.
6. Cover the solar panel with cardboard — verify battery voltage
   indicator on MPPT controller drops over 30 min and pod stays alive.
7. Trigger "STATUS?" SMS via GSM — verify reply within 60 s.

---

**Next file:** [`WIRING_DIAGRAM.md`](WIRING_DIAGRAM.md) — the complete pin map.