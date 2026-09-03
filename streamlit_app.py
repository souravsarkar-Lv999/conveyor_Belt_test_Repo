"""
BeltGuard - Smart Mine Conveyor-Belt Health-Monitor
Hackathon interactive hardware demo (Streamlit, light theme).

Run:
    pip install -r requirements.txt
    streamlit run streamlit_app.py

Navigation: TOP TAB BAR (always visible) + LEFT SIDEBAR (sensor
deep-dives + Reset, freely open/close). Diagrams use Mermaid (clean
SVG); matplotlib is reserved for live data charts only.
"""

from pathlib import Path
import io
import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Light-mode palette - single source of truth
BG_PAGE      = "#ffffff"
BG_CARD      = "#f6f8fa"
BG_CARD_ALT  = "#eef1f5"
BORDER       = "#d0d7de"
TEXT         = "#1f2328"
TEXT_MUTED   = "#656d76"

BLUE         = "#0a5cff"
ORANGE       = "#ff7a00"
GREEN        = "#1f883d"
AMBER        = "#bf8700"
RED          = "#cf222e"
PURPLE       = "#8250df"
CYAN         = "#0969da"

OK, WARN, ALARM = GREEN, AMBER, RED

plt.rcParams.update({
    "figure.facecolor":  BG_PAGE,
    "axes.facecolor":    BG_PAGE,
    "axes.edgecolor":    BORDER,
    "savefig.facecolor": BG_PAGE,
    "savefig.edgecolor": BG_PAGE,
    "text.color":        TEXT,
    "axes.labelcolor":   TEXT,
    "xtick.color":       TEXT_MUTED,
    "ytick.color":       TEXT_MUTED,
    "font.family":       "DejaVu Sans",
    "axes.titlecolor":   TEXT,
    "axes.grid":         True,
    "grid.color":        BORDER,
    "grid.alpha":        0.5,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

st.set_page_config(
    page_title="BeltGuard - Mine Conveyor Safety",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)
ROOT = Path(__file__).resolve().parent
st.markdown(
    f"""
<style>
    footer {{ visibility: hidden; }}
    #MainMenu {{ visibility: hidden; }}
    [data-testid="stToolbar"] {{ visibility: hidden; }}
    [data-testid="stStatusWidget"] {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem;
                        max-width: 1180px; }}

    .stApp {{ background-color: {BG_PAGE}; color: {TEXT}; }}
    section[data-testid="stSidebar"] {{ background-color: {BG_CARD}; }}
    section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

    h1, h2, h3, h4, h5, h6, p, li, span, div {{ color: {TEXT}; }}
    .stCaption, small {{ color: {TEXT_MUTED} !important; }}

    .big-title {{ font-size:2.4rem; font-weight:800; line-height:1.05;
                  color:{BLUE}; margin:0; }}
    .sub-title {{ font-size:1.05rem; color:{TEXT_MUTED}; margin-top:0.1rem; }}

    .card {{ background:{BG_CARD}; border:1px solid {BORDER};
             border-radius:0.6rem; padding:1rem 1.2rem;
             margin-bottom:0.6rem; }}
    .card-accent {{ border-left:5px solid {BLUE}; }}
    .card-orange {{ border-left:5px solid {ORANGE}; }}
    .card-green  {{ border-left:5px solid {GREEN}; }}
    .card-amber  {{ border-left:5px solid {AMBER}; }}
    .card-red    {{ border-left:5px solid {RED}; }}
    .card-purple {{ border-left:5px solid {PURPLE}; }}

    .badge {{ display:inline-block; padding:0.15rem 0.55rem;
              border-radius:0.4rem; font-size:0.78rem;
              font-weight:700; letter-spacing:0.04em;
              text-transform:uppercase; }}
    .badge-ok    {{ background:#dafbe1; color:{GREEN};
                    border:1px solid #aceebb; }}
    .badge-warn  {{ background:#fff8c5; color:{AMBER};
                    border:1px solid #d4a72c; }}
    .badge-alarm {{ background:#ffebe9; color:{RED};
                    border:1px solid #ff8182; }}
    .badge-info  {{ background:#ddf4ff; color:{BLUE};
                    border:1px solid #b6e3ff; }}

    .kpi {{ background:{BG_CARD}; border:1px solid {BORDER};
            border-radius:0.5rem; padding:0.7rem 0.9rem; }}
    .kpi-lbl {{ font-size:0.78rem; color:{TEXT_MUTED};
                text-transform:uppercase; letter-spacing:0.06em; }}
    .kpi-val {{ font-size:1.6rem; font-weight:700; color:{TEXT};
                line-height:1.1; }}

    .page-title  {{ font-size:1.9rem; font-weight:800; color:{TEXT};
                    margin:0 0 0.2rem 0; }}
    .page-sub    {{ color:{TEXT_MUTED}; margin:0 0 1rem 0; }}
    .section-h   {{ font-size:1.25rem; font-weight:700; color:{TEXT};
                    margin:1.2rem 0 0.5rem 0; }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.3rem; background: {BG_CARD};
        padding: 0.45rem 0.6rem; border-radius: 0.6rem;
        border: 1px solid {BORDER};
    }}
    .stTabs [data-baseweb="tab-list"] button {{
        font-size: 0.95rem; font-weight: 600;
        padding: 0.45rem 0.95rem; border-radius: 0.45rem;
        color: {TEXT_MUTED}; background: transparent;
    }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        background: {BLUE}; color: white;
    }}
    .stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.2rem; }}

    table {{ border-collapse: collapse; width: 100%; }}
    th {{ background:{BG_CARD_ALT}; color:{TEXT};
          text-align:left; padding:0.45rem 0.6rem;
          border-bottom:1px solid {BORDER}; }}
    td {{ padding:0.45rem 0.6rem;
          border-bottom:1px solid {BORDER}; color:{TEXT}; }}

    .mermaid svg {{ background:{BG_PAGE} !important; }}
</style>
""",
    unsafe_allow_html=True,
)
# Reusable UI bits
def badge(text, kind="info"):
    cls = {"ok": "badge-ok", "warn": "badge-warn",
           "alarm": "badge-alarm", "info": "badge-info"}[kind]
    st.markdown(f'<span class="badge {cls}">{text}</span>',
                unsafe_allow_html=True)


def page_title(title, sub=""):
    st.markdown(
        f'<p class="page-title">{title}</p>'
        f'<p class="page-sub">{sub}</p>',
        unsafe_allow_html=True,
    )


def section_h(text):
    st.markdown(f'<p class="section-h">{text}</p>',
                unsafe_allow_html=True)


def show(fig):
    """Render a matplotlib figure inline. No white box."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight",
                transparent=False, facecolor=BG_PAGE)
    plt.close(fig)
    buf.seek(0)
    st.image(buf, use_container_width=True)


# SENSOR DEFINITIONS - single source of truth for every per-sensor page.
SENSOR_DEFS = [
    {
        "name": "Vibration (ADXL345)",
        "key": "vib",
        "unit": "g RMS",
        "color": RED,
        "where": "Clamped to head-pulley bearing housing (or tail pulley). "
                 "Senses bearing race defect, pulley imbalance, belt slap.",
        "physics": "MEMS 3-axis accelerometer. Sample at 1.6 kHz, take "
                   "FFT, look for 1x, 2x, 3x shaft harmonics and "
                   "broadband rise > 0.55 g RMS = WARN, > 0.85 g = ALARM.",
        "pin": "I2C - SDA=GPIO21, SCL=GPIO22, INT=GPIO34 (input-only). "
               "Addr 0x53.",
        "ok":    0.55,
        "warn":  0.85,
        "alarm": 1.20,
        "fails": ["Belt slip", "Bearing race spall", "Pulley imbalance",
                  "Idler seizure"],
        "bom":   "ADXL345 breakout - INR 180",
    },
    {
        "name": "Belt temperature (DS18B20)",
        "key": "temp",
        "unit": "deg C",
        "color": ORANGE,
        "where": "Stainless probe pressed against the belt carcass, 1 m "
                 "from head pulley (hottest zone).",
        "physics": "1-Wire digital temp sensor, +/-0.5 deg C, 12-bit. "
                   "Trend 60 s. >55 deg C = WARN (friction hot-spot). "
                   ">70 deg C = ALARM (auto-ignition risk for coal dust).",
        "pin": "1-Wire - DQ=GPIO4, 4.7 kohm pull-up to 3V3, parasite power off.",
        "ok":    55,
        "warn":  70,
        "alarm": 85,
        "fails": ["Idler bearing seizure", "Fire / smoulder",
                  "Friction hot-spot"],
        "bom":   "DS18B20 TO-92 + 4.7 kohm resistor - INR 95",
    },
    {
        "name": "Belt tension (HX711 + load cell)",
        "key": "tension",
        "unit": "N",
        "color": PURPLE,
        "where": "Load cell on the take-up pulley carriage - measures the "
                 "tension the gravity weight is applying.",
        "physics": "Strain-gauge load cell in half-bridge to HX711 24-bit "
                   "ADC to ESP32. Calibrate with known dead-weight. "
                   "<5 000 N = belt too slack (slip risk). "
                   ">9 500 N = over-tensioned (tear risk).",
        "pin": "Custom - DOUT=GPIO16, SCK=GPIO17. HX711 channel A.",
        "ok":    (5000, 9500),
        "warn":  (3000, 11000),
        "alarm": (1500, 13000),
        "fails": ["Belt slip / drive burnout", "Belt tear",
                  "Take-up ram seizure"],
        "bom":   "1 t S-type load cell + HX711 - INR 650",
    },
    {
        "name": "Drive RPM (Hall + magnet)",
        "key": "rpm",
        "unit": "rpm",
        "color": CYAN,
        "where": "Magnet epoxied to drive pulley rim; Hall sensor on the "
                 "fixed bracket 5 mm away.",
        "physics": "Each magnet pass gives one pulse. ESP32 pulse-counter "
                   "computes rpm = (pulses / pulses-per-rev) * 60 / dt. "
                   "Drop > 15 % vs setpoint = slip or belt break.",
        "pin": "GPIO35 (input-only, no pull-up needed - open-collector "
               "Hall with on-board 10 kohm).",
        "ok":    (560, 640),
        "warn":  (520, 680),
        "alarm": (450, 720),
        "fails": ["Drive belt slip", "Motor stall", "Belt broken"],
        "bom":   "A3144 Hall + 6x3 mm neodymium magnet - INR 40",
    },
    {
        "name": "Belt-tear IR (E18-D80NK)",
        "key": "tear",
        "unit": "boolean",
        "color": RED,
        "where": "Two sensors across the belt width, near the head pulley. "
                 "If belt is intact, receiver sees nothing (beam blocked by "
                 "bulk material); if belt is torn, beam passes through the "
                 "gap -> ALARM.",
        "physics": "Diffuse-reflective IR proximity, 3-80 cm range. "
                   "Logic-low when target within range. ALARM = any "
                   "sensor holds LOW for > 2 s with no drive stop.",
        "pin": "OUT=GPIO32 (INT, input-only).",
        "ok":    "HIGH",
        "warn":  None,
        "alarm": "LOW sustained",
        "fails": ["Longitudinal belt tear", "Foreign object punch-through"],
        "bom":   "E18-D80NK pair - INR 280",
    },
]
SENSOR_DEFS += [
    {
        "name": "Motor current (ACS712-30A)",
        "key": "current",
        "unit": "A",
        "color": AMBER,
        "where": "Clamped on one phase of the drive-motor supply cable "
                 "(after the contactor, before the DOL starter).",
        "physics": "Hall-effect linear current sensor, 30 A range, "
                   "66 mV/A. ESP32 ADC1 (GPIO33) reads the filtered "
                   "output. RMS over 1 s. >22 A = overload / jam.",
        "pin": "OUT -> 1 kohm + 100 nF RC low-pass -> GPIO33 (ADC1_CH5).",
        "ok":    18,
        "warn":  22,
        "alarm": 28,
        "fails": ["Idler jam", "Overload / stalling load",
                  "Phase imbalance"],
        "bom":   "ACS712-30A module - INR 220",
    },
    {
        "name": "Coal-dust (GP2Y1010AU0F)",
        "key": "dust",
        "unit": "ug/m3",
        "color": ORANGE,
        "where": "Inside the sensor pod, looking down through a small "
                 "mesh-protected intake. Heated inlet dries the air so "
                 "humidity doesn't dominate the reading.",
        "physics": "IR LED (pulsed 10 ms every 60 s) + photodiode. "
                   "Voltage is proportional to PM density. >250 ug/m3 = "
                   "WARN, >500 ug/m3 = explosive atmosphere alarm.",
        "pin": "LED=GPIO25, OUT=ADC GPIO33 (shared w/ ACS712 via mux).",
        "ok":    150,
        "warn":  250,
        "alarm": 500,
        "fails": ["Dust explosion atmosphere", "Carry-back spillage",
                  "Drum seal failure"],
        "bom":   "Sharp GP2Y1010AU0F - INR 950",
    },
    {
        "name": "CH4 / smoke (MQ-2)",
        "key": "mq2",
        "unit": "ppm (CH4)",
        "color": AMBER,
        "where": "Inside the sensor pod, gas inlet facing downward so "
                 "rising gas reaches it. Behind a flame-arrestor mesh.",
        "physics": "Tin-dioxide semiconductor. Heater 5 V, 150 mA. "
                   "Rs/Ro ratio to ppm. >5 000 ppm CH4 = LEL alarm "
                   "(LEL CH4 = 50 000 ppm).",
        "pin": "Heater=GPIO26 via MOSFET, OUT=ADC GPIO32 (shared via mux).",
        "ok":    1000,
        "warn":  5000,
        "alarm": 12000,
        "fails": ["Methane leak", "Coal-dust fire / smoulder"],
        "bom":   "MQ-2 module - INR 180",
    },
    {
        "name": "CO / NH3 (MQ-135)",
        "key": "mq135",
        "unit": "ppm (CO eq.)",
        "color": PURPLE,
        "where": "Same chamber as MQ-2 but with its own separate "
                 "flame-arrestor intake. Differentiates CO from CH4.",
        "physics": "Tin-dioxide, different catalyst. Sensitive to CO, "
                   "NH3, benzene. >30 ppm CO = toxic; >100 ppm = "
                   "fire smoulder signature.",
        "pin": "Heater=GPIO27 via MOSFET, OUT=ADC GPIO35.",
        "ok":    10,
        "warn":  30,
        "alarm": 100,
        "fails": ["Coal smoulder", "Diesel exhaust in tunnel"],
        "bom":   "MQ-135 module - INR 200",
    },
]
# DIAGRAMS - all as Mermaid (clean SVG, no matplotlib overlap)
def diagram_architecture():
    st.markdown(
        """
```mermaid
flowchart LR
    subgraph BELT ["Belt + Pulleys + Idlers"]
        direction LR
        B["Coal / iron ore<br/>on rubber belt"]
    end
    subgraph POD ["Belt Sensor Pod (IP67, on belt frame)"]
        direction TB
        S1["ADXL345<br/>Vibration"]
        S2["DS18B20<br/>Temperature"]
        S3["HX711<br/>Tension"]
        S4["E18-IR<br/>Tear"]
        S5["Hall<br/>RPM"]
        S6["ACS712<br/>Current"]
        S7["GP2Y1010<br/>Dust"]
        S8["MQ-2 / MQ-135<br/>Gas"]
        MCU["ESP32-WROOM-32<br/>carrier PCB"]
        S1 --> MCU
        S2 --> MCU
        S3 --> MCU
        S4 --> MCU
        S5 --> MCU
        S6 --> MCU
        S7 --> MCU
        S8 --> MCU
    end
    subgraph SOLAR ["Solar Pod (tunnel roof / pole)"]
        direction TB
        PV["20 W mono panel"]
        MPPT["MPPT charge ctrl"]
        BAT["12 V 20 Ah LiFePO4"]
        BC["5 V / 3.3 V<br/>buck + LDO"]
        PV --> MPPT --> BAT --> BC
    end
    subgraph CABIN ["Maintenance Cabin"]
        direction TB
        GW["LoRa gateway<br/>RA-02 + ESP32"]
        DASH["Dashboard<br/>+ siren + SMS"]
        GW --> DASH
    end
    BELT --> S1
    BELT --> S2
    BELT --> S3
    BELT --> S4
    BELT --> S5
    BELT --> S6
    POD -->|LoRa 868 MHz<br/>SF7 / BW125<br/>2-5 km LoS| CABIN
    SOLAR -->|12 V cable| POD
    SOLAR -->|12 V cable| CABIN
```
""",
        unsafe_allow_html=False,
    )


def diagram_belt_layout():
    st.markdown(
        """
```mermaid
flowchart LR
    subgraph BELT ["Belt top view (head pulley on the RIGHT)"]
        direction LR
        T["Tail pulley"]:::pulley
        M["Drive motor"]:::motor
        H["Head pulley<br/>discharge"]:::pulley
        IDL["Idler rollers x40"]:::idler
        T --- IDL
        IDL --- H
        M --- H
        V1["ADXL345<br/>Vibration"]:::sensor --> H
        V2["DS18B20<br/>Temp probe"]:::sensor -. touches belt .-> IDL
        V3["HX711<br/>Load cell"]:::sensor --> T
        V4["E18-IR<br/>Tear beam"]:::sensor --> IDL
        V5["Hall + magnet<br/>RPM"]:::sensor --> H
        V6["ACS712<br/>Current"]:::sensor --> M
        V7["GP2Y1010<br/>Dust"]:::sensor -. in pod .-> T
        V8["MQ-2 / 135<br/>Gas"]:::sensor -. in pod .-> T
    end
    classDef pulley fill:#eef1f5,stroke:#656d76,color:#1f2328
    classDef motor  fill:#fff8c5,stroke:#bf8700,color:#1f2328
    classDef idler  fill:#ddf4ff,stroke:#0969da,color:#1f2328
    classDef sensor fill:#ffebe9,stroke:#cf222e,color:#1f2328
```
""",
        unsafe_allow_html=False,
    )
def diagram_wiring():
    st.markdown(
        """
```mermaid
flowchart TB
    subgraph ESP ["ESP32-WROOM-32 carrier PCB"]
        direction TB
        V33["3V3 rail"]
        V5["5V rail"]
        GND["GND"]
        SDA["GPIO21 SDA"]
        SCL["GPIO22 SCL"]
        O4["GPIO4 1-Wire"]
        O16["GPIO16 HX711 DOUT"]
        O17["GPIO17 HX711 SCK"]
        O25["GPIO25 Dust LED"]
        O26["GPIO26 MQ-2 heater"]
        O27["GPIO27 MQ-135 heater"]
        O32["GPIO32 Tear IR / MQ-2 out"]
        O33["GPIO33 ADC1 (ACS712 / Dust)"]
        O34["GPIO34 ADXL345 INT"]
        O35["GPIO35 Hall / MQ-135 out"]
        SP["VSPI for LoRa RA-02<br/>SCK=18, MISO=19, MOSI=23,<br/>CS=5, RST=14, DIO0=27"]
        LORA["LoRa RA-02<br/>868 MHz"]
    end
    SDA --> ADXL["ADXL345"]
    SCL --> ADXL
    O4 --> DS["DS18B20"]
    O16 --> HX["HX711"]
    O17 --> HX
    O25 --> DUST["GP2Y1010"]
    O33 --> DUST
    O26 --> MQ2["MQ-2 heater"]
    O27 --> MQ135["MQ-135 heater"]
    O32 --> TEAR["E18-IR OUT"]
    O33 --> ACS["ACS712 OUT"]
    O34 --> ADXL
    O35 --> HALL["Hall sensor"]
    O35 --> MQ135
    SP --> LORA
```
""",
        unsafe_allow_html=False,
    )


def diagram_power():
    st.markdown(
        """
```mermaid
flowchart LR
    PV["20 W mono<br/>solar panel<br/>Vmp 18 V / Imp 1.1 A"]:::pv
    MPPT["MPPT charge ctrl<br/>CN3791 / DW01<br/>14.6 V abs"]:::mppt
    BAT["12 V 20 Ah<br/>LiFePO4<br/>32700 cells"]:::bat
    FUSE["10 A blade fuse<br/>+ TVS 30 V"]:::fuse
    BC12["12 V distribution<br/>rail"]:::rail
    LM["LM2596 buck<br/>12 V to 5 V / 3 A"]:::dc
    AMS["AMS1117 LDO<br/>5 V to 3.3 V / 0.8 A"]:::dc
    PV --> MPPT --> BAT --> FUSE --> BC12
    BC12 --> LM --> AMS --> R3["3V3 rail<br/>ESP32 + sensors"]:::rail
    BC12 --> R5["5V rail<br/>LoRa PA, MQ heaters"]:::rail
    classDef pv fill:#fff8c5,stroke:#bf8700,color:#1f2328
    classDef mppt fill:#dafbe1,stroke:#1f883d,color:#1f2328
    classDef bat fill:#ffebe9,stroke:#cf222e,color:#1f2328
    classDef fuse fill:#f6f8fa,stroke:#656d76,color:#1f2328
    classDef dc fill:#ddf4ff,stroke:#0969da,color:#1f2328
    classDef rail fill:#eef1f5,stroke:#656d76,color:#1f2328
```
""",
        unsafe_allow_html=False,
    )


def diagram_lora():
    st.markdown(
        """
```mermaid
flowchart LR
    POD["Belt Pod<br/>868 MHz<br/>+2 dBi whip"]:::node
    AIR(("Air<br/>2-5 km LoS<br/>FSPL 100-110 dB")):::air
    GW["Gateway<br/>868 MHz<br/>+6 dBi Yagi"]:::node
    GSM["SIM800L<br/>GSM fallback"]:::node
    DASH["Dashboard<br/>+ siren"]:::app
    POD -->|SF7 / BW125 / 14 dBm| AIR
    AIR --> GW
    GW --> DASH
    POD -.->|if LoRa fails| GSM
    GSM -.-> DASH
    classDef node fill:#ddf4ff,stroke:#0969da,color:#1f2328
    classDef air  fill:#f6f8fa,stroke:#656d76,color:#1f2328
    classDef app  fill:#dafbe1,stroke:#1f883d,color:#1f2328
```
""",
        unsafe_allow_html=False,
    )


def diagram_enclosure():
    st.markdown(
        """
```mermaid
flowchart TB
    LID["Lid: polycarbonate,<br/>clear, 4x M4 captive screws"]:::lid
    SEAL["Silicone gasket<br/>re-coat yearly"]:::seal
    BODY["Die-cast aluminium body<br/>150 x 100 x 70 mm<br/>IP67"]:::body
    GL["Cable gland 1: 12 V from solar pod<br/>PG7, IP68"]:::gl
    GL2["Cable gland 2: sensor loom<br/>PG9, IP68"]:::gl
    PCB["Carrier PCB<br/>ESP32 + sensor breakouts<br/>standoffs + vibration isolators"]:::pcb
    VENT["Goretek IP67 vent<br/>pressure equalisation"]:::vent
    BRACKET["Stainless L-bracket<br/>clamped to belt frame"]:::brk
    LID --- SEAL --- BODY
    GL --> BODY
    GL2 --> BODY
    PCB --- BODY
    VENT --- BODY
    BODY --- BRACKET
    classDef lid fill:#eef1f5,stroke:#656d76,color:#1f2328
    classDef seal fill:#fff8c5,stroke:#bf8700,color:#1f2328
    classDef body fill:#ddf4ff,stroke:#0969da,color:#1f2328
    classDef gl   fill:#f6f8fa,stroke:#656d76,color:#1f2328
    classDef pcb  fill:#dafbe1,stroke:#1f883d,color:#1f2328
    classDef vent fill:#ffebe9,stroke:#cf222e,color:#1f2328
    classDef brk  fill:#eef1f5,stroke:#656d76,color:#1f2328
```
""",
        unsafe_allow_html=False,
    )
# RENDERERS - one per top-level section
def render_overview():
    page_title(
        "BeltGuard",
        "A solar-powered sensor pod that watches every metre of every "
        "belt, 24 x 7 - replacing the human-eye inspection that lets "
        "blasters slip through.",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        '<div class="kpi"><div class="kpi-lbl">Belt fires</div>'
        f'<div class="kpi-val" style="color:{RED}">detected &lt;90 s</div></div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        '<div class="kpi"><div class="kpi-lbl">Belt tears</div>'
        f'<div class="kpi-val" style="color:{RED}">detected &lt;2 s</div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        '<div class="kpi"><div class="kpi-lbl">LoRa range</div>'
        f'<div class="kpi-val" style="color:{OK}">2 to 5 km LoS</div></div>',
        unsafe_allow_html=True,
    )
    c4.markdown(
        '<div class="kpi"><div class="kpi-lbl">Solar autonomy</div>'
        f'<div class="kpi-val" style="color:{OK}">41 days</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    section_h("System at a glance")
    diagram_architecture()

    section_h("How to explore this demo")
    st.markdown(
        """
| Top tab | What you will see |
|---|---|
| **Overview** | This page |
| **Architecture** | Full block diagram, belt-layout map, wiring pinout |
| **Sensor Pod** | 9 individual sensor deep-dive pages (also in the left sidebar) |
| **Live Telemetry** | 7 live charts - drag any slider to inject a fault |
| **Simulations** | 6 interactive what-if plots |
| **Power** | Solar pod, MPPT, battery, buck converters, energy budget |
| **LoRa Link** | Radio link + SIM800L GSM fallback + interactive budget |
| **Enclosure** | IP67 box, glands, vibration isolation, mounting bracket |
| **BOM** | Full bill of materials with INR + USD totals |
| **Install** | Step-by-step install walkthrough |

> The **left sidebar** (click the chevron in the top-left) holds the
> 9 individual sensor deep-dive sub-pages. Open or close it freely -
> the top tab bar stays visible regardless, so you can never get lost.
"""
    )


def render_architecture():
    page_title("Architecture",
               "Full system block diagram, belt-layout map, wiring pinout.")
    section_h("System block diagram")
    diagram_architecture()
    section_h("Where every sensor sits on the belt")
    diagram_belt_layout()
    section_h("Wiring pinout")
    diagram_wiring()


def render_sensor_pod():
    page_title(
        "Sensor Pod",
        "Open the left sidebar and pick a sensor - each one has its own "
        "page with the symbol, where it lives on the belt, physics, "
        "pinout, live interactive graph, failure modes and BOM line.",
    )
    section_h("All 9 sensors at a glance")
    cols = st.columns(3)
    for i, s in enumerate(SENSOR_DEFS):
        with cols[i % 3]:
            st.markdown(
                f'<div class="card card-orange" '
                f'style="border-left-color:{s["color"]}">'
                f'<b style="color:{s["color"]}">{s["name"]}</b><br>'
                f'<span style="color:{TEXT_MUTED};font-size:0.85rem">'
                f'{s["unit"]}</span></div>',
                unsafe_allow_html=True,
            )
    section_h("Belt layout - where each sensor physically sits")
    diagram_belt_layout()
def render_sensor_page(s):
    """Deep-dive page for one sensor. Everything about it, one place."""
    page_title(s["name"],
               f"Where it sits, how it works, and what it tells you "
               f"(unit: {s['unit']}).")

    badge_row = st.columns([1, 2, 2, 2])
    with badge_row[0]:
        st.markdown(
            f'<div class="card" style="text-align:center;'
            f'font-family:ui-monospace,monospace;font-size:0.8rem;'
            f'color:{s["color"]}">'
            f'+-------+\n| {s["key"].upper():<5} |\n+---.---+\n    |\n  {s["unit"]}'
            f'</div>',
            unsafe_allow_html=True,
        )
    with badge_row[1]:
        st.markdown(
            f'<div class="card card-green"><b>OK</b> &nbsp; {s["ok"]}<br>'
            f'<span style="color:{TEXT_MUTED};font-size:0.85rem">'
            f'Normal operation</span></div>',
            unsafe_allow_html=True,
        )
    with badge_row[2]:
        st.markdown(
            f'<div class="card card-amber"><b>WARN</b> &nbsp; {s["warn"]}<br>'
            f'<span style="color:{TEXT_MUTED};font-size:0.85rem">'
            f'Flag to maintenance</span></div>',
            unsafe_allow_html=True,
        )
    with badge_row[3]:
        st.markdown(
            f'<div class="card card-red"><b>ALARM</b> &nbsp; {s["alarm"]}<br>'
            f'<span style="color:{TEXT_MUTED};font-size:0.85rem">'
            f'Stop belt + SMS</span></div>',
            unsafe_allow_html=True,
        )

    section_h("Where it lives on the belt")
    st.markdown(s["where"])

    section_h("How it works")
    st.markdown(s["physics"])

    section_h("Pinout / wiring")
    st.code(s["pin"], language="text")

    section_h("Interactive live reading - drag the slider")
    _render_sensor_slider(s)

    section_h("Failure modes it catches")
    for f in s["fails"]:
        st.markdown(f"- {f}")

    section_h("BOM line")
    st.markdown(f"`{s['bom']}`")


def _render_sensor_slider(s):
    """A live graph + slider for one sensor, with OK / WARN / ALARM bands."""
    if s["key"] not in st.session_state:
        st.session_state[s["key"]] = float(s["warn"])

    try:
        hi = float(max(s["alarm"], s["warn"])) * 1.6
    except TypeError:
        hi = float(max(s["alarm"][1], s["warn"][1])) * 1.6

    val = st.slider(
        f"Current {s['unit']} reading",
        min_value=0.0,
        max_value=hi,
        value=st.session_state[s["key"]],
        step=0.5,
        key=f"slider_{s['key']}",
    )
    st.session_state[s["key"]] = val

    if isinstance(s["warn"], (int, float)):
        if val >= s["alarm"]:
            status, kind = "ALARM", "alarm"
        elif val >= s["warn"]:
            status, kind = "WARN", "warn"
        else:
            status, kind = "OK", "ok"
    else:
        status, kind = ("ALARM" if val < 0.5 else "OK"), (
            "alarm" if val < 0.5 else "ok"
        )

    cols = st.columns([3, 1])
    with cols[1]:
        badge(f"{status} - {val:.2f} {s['unit']}", kind)

    n = 120
    t = np.arange(n)
    base = np.linspace(val * 0.7, val, n) + 0.05 * val * np.sin(t / 5)
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.plot(t, base, color=s["color"], lw=1.8)
    if isinstance(s["warn"], (int, float)):
        ax.axhline(s["warn"], color=AMBER, ls="--", lw=1.2,
                   label=f"WARN {s['warn']}")
        ax.axhline(s["alarm"], color=RED, ls="--", lw=1.2,
                   label=f"ALARM {s['alarm']}")
        ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.set_xlabel("sample")
    ax.set_ylabel(s['unit'])
    ax.set_title(f"{s['name']} - live (last {n} samples)")
    show(fig)
def render_live_telemetry():
    page_title("Live Telemetry",
               "Simulated feed. Move any slider - every graph reacts.")
    if "telemetry_data" not in st.session_state:
        np.random.seed(int(time.time()) % 1000)
        st.session_state.telemetry_data = pd.DataFrame({
            "time":    pd.date_range("2026-09-04 00:00", periods=200,
                                     freq="1min"),
            "temp_C":  35 + 2 * np.random.randn(200).cumsum() * 0.05,
            "vib_g":   np.abs(0.4 + 0.1 * np.random.randn(200).cumsum()),
            "tension_N": 6000 + 200 * np.sin(np.linspace(0, 20, 200))
                          + 100 * np.random.randn(200),
            "rpm":     600 + 5 * np.sin(np.linspace(0, 20, 200))
                       + 2 * np.random.randn(200),
            "current_A": 12 + 1 * np.sin(np.linspace(0, 20, 200))
                         + 0.3 * np.random.randn(200),
            "rssi":    -85 - 3 * np.random.randn(200),
            "soc_pct": np.clip(82 - 0.05 * np.arange(200)
                               + 0.5 * np.random.randn(200), 0, 100),
        })
    df = st.session_state.telemetry_data

    cols = st.columns(7)
    specs = [
        ("Belt temp",   "temp_C",    "deg C", 70,  RED),
        ("Vibration",   "vib_g",     "g",     0.85, RED),
        ("Tension",     "tension_N", "N",     9500, RED),
        ("Drive RPM",   "rpm",       "rpm",   540,  AMBER),
        ("Current",     "current_A", "A",     22,   AMBER),
        ("RSSI",        "rssi",      "dBm",   -110, AMBER),
        ("Battery",     "soc_pct",   "%",     20,   RED),
    ]
    for col, (lbl, k, unit, thr, _alarm_color) in zip(cols, specs):
        v = df[k].iloc[-1]
        prev = df[k].iloc[-2]
        is_low = (k == "soc_pct")
        bad = (v < thr) if is_low else (v > thr)
        near_warn = (thr * 2) if is_low else (thr * 0.8)
        if bad:
            color = RED
        elif (v < near_warn) if is_low else (v > near_warn):
            color = AMBER
        else:
            color = OK
        with col:
            st.markdown(
                f'<div class="kpi"><div class="kpi-lbl">{lbl}</div>'
                f'<div class="kpi-val" style="color:{color}">'
                f'{v:.1f} {unit}</div>'
                f'<div style="color:{TEXT_MUTED};font-size:0.78rem">'
                f'Delta {v - prev:+.2f}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("")

    fig, axes = plt.subplots(4, 2, figsize=(12, 10))
    series = [
        ("temp_C",     "Belt temperature",  "deg C",  [(70, RED), (55, AMBER)]),
        ("vib_g",      "Vibration RMS",     "g",      [(0.85, RED), (0.55, AMBER)]),
        ("tension_N",  "Belt tension",      "N",      [(9500, RED), (7000, AMBER)]),
        ("rpm",        "Drive RPM",         "rpm",    [(540, AMBER)]),
        ("current_A",  "Motor current",     "A",      [(22, RED), (16, AMBER)]),
        ("soc_pct",    "Battery SoC",       "%",      [(20, RED), (40, AMBER)]),
        ("rssi",       "LoRa RSSI",         "dBm",    [(-110, RED), (-100, AMBER)]),
    ]
    axes_flat = axes.flatten()
    palette = [RED, BLUE, PURPLE, AMBER, CYAN, GREEN, CYAN]
    for i, ((col, title, unit, thrs), c) in enumerate(zip(series, palette)):
        ax = axes_flat[i]
        ax.plot(df["time"], df[col], color=c, lw=1.4)
        for thr, cc in thrs:
            ax.axhline(thr, color=cc, ls="--", lw=1.0, alpha=0.7)
        ax.set_title(f"{title} ({unit})", fontsize=10)
        ax.tick_params(axis="x", rotation=30, labelsize=7)
        ax.tick_params(axis="y", labelsize=8)
    for j in range(len(series), len(axes_flat)):
        axes_flat[j].axis("off")
    fig.tight_layout()
    show(fig)

    section_h("Inject a fault")
    fcols = st.columns(4)
    if fcols[0].button("Belt fire (temp + vib)"):
        df["temp_C"].iloc[-10:] += 50
        df["vib_g"].iloc[-10:] += 0.6
        st.rerun()
    if fcols[1].button("Belt tear (RPM drop)"):
        df["rpm"].iloc[-5:] -= 200
        st.rerun()
    if fcols[2].button("Idler jam (current up)"):
        df["current_A"].iloc[-8:] += 14
        st.rerun()
    if fcols[3].button("Battery low (SoC down)"):
        df["soc_pct"].iloc[-3:] -= 30
        st.rerun()
def render_simulations():
    page_title("Simulations",
               "Six interactive what-if plots - drag any slider to see how "
               "the system would behave.")
    tabs = st.tabs([
        "Belt thermal", "Vibration FFT", "Strain calibration",
        "LoRa budget", "Solar harvest", "Power budget",
    ])
    with tabs[0]:
        _sim_belt_thermal()
    with tabs[1]:
        _sim_vibration_fft()
    with tabs[2]:
        _sim_strain_cal()
    with tabs[3]:
        _sim_lora_budget()
    with tabs[4]:
        _sim_solar_harvest()
    with tabs[5]:
        _sim_power_budget()


def _sim_belt_thermal():
    section_h("Belt thermal - how fast does a hot-spot reach ignition?")
    ambient = st.slider("Ambient (deg C)", 20, 45, 32)
    hotspot = st.slider("Hot-spot start (deg C above ambient)", 0, 60, 10)
    mins = np.linspace(0, 120, 600)
    k = 0.04
    T = ambient + hotspot * np.exp(k * mins)
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.plot(mins, T, color=ORANGE, lw=2)
    ax.axhline(70, color=RED, ls="--", lw=1.0, label="Alarm 70 deg C")
    ax.axhline(55, color=AMBER, ls="--", lw=1.0, label="Warn 55 deg C")
    alarm_t = mins[np.argmax(T > 70)] if (T > 70).any() else None
    if alarm_t is not None:
        ax.annotate(f"ALARM @ {alarm_t:.0f} min",
                    xy=(alarm_t, 70), xytext=(alarm_t + 8, 80),
                    arrowprops=dict(arrowstyle="-|>", color=RED),
                    color=RED, fontsize=10)
    ax.set_xlabel("minutes"); ax.set_ylabel("belt temp (deg C)")
    ax.legend(frameon=False)
    show(fig)


def _sim_vibration_fft():
    section_h("Vibration FFT - is that a bearing defect or just background?")
    g_amp = st.slider("Bearing defect amplitude (g)", 0.0, 2.0, 0.6, 0.05)
    f0 = st.slider("Shaft rotation (Hz)", 5, 25, 12)
    f = np.linspace(0, 100, 2000)
    sig = (0.05 + 0.15 / (1 + ((f - f0) / 2) ** 2)
           + g_amp * np.exp(-((f - f0 * 2.3) / 0.5) ** 2))
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.semilogy(f, sig + 1e-3, color=BLUE, lw=1.4)
    ax.axvline(f0, color=GREEN, ls=":", label="1x shaft")
    ax.axvline(f0 * 2.3, color=RED, ls=":", label="2.3x bearing defect")
    ax.set_xlabel("Hz"); ax.set_ylabel("amplitude (g, log)")
    ax.legend(frameon=False)
    show(fig)


def _sim_strain_cal():
    section_h("Strain / load-cell calibration")
    mass = st.slider("Applied dead-weight (kg)", 0, 1000, 250, 10)
    cal = 9.81 * mass
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ms = np.linspace(0, 1000, 100)
    cs = 9.81 * ms
    ax.plot(ms, cs, color=PURPLE, lw=2)
    ax.scatter([mass], [cal], color=RED, s=80, zorder=5,
               label=f"{mass} kg -> {cal:.0f} N")
    ax.set_xlabel("mass (kg)"); ax.set_ylabel("force (N)")
    ax.legend(frameon=False)
    show(fig)
def _sim_lora_budget():
    section_h("LoRa link budget - can we close the link?")
    distance = st.slider("Distance (km)", 0.5, 10.0, 3.0, 0.1)
    tx_dbm = st.slider("TX power (dBm)", 2, 20, 14)
    rx_gain = st.slider("Gateway antenna gain (dBi)", 2, 12, 6)
    fspl = 32.4 + 20 * np.log10(distance) + 20 * np.log10(868)
    fig, ax = plt.subplots(figsize=(11, 3.0))
    bars = ["TX", "TX ant", "FSPL loss", "RX ant", "RX (dBm)"]
    vals = [tx_dbm, 2, -fspl, rx_gain, 0]
    cum = [0]
    for v in vals[:-1]:
        cum.append(cum[-1] + v)
    cols = [BLUE, GREEN, RED, GREEN, BLUE]
    for i, (b, v, c) in enumerate(zip(bars, vals, cols)):
        if i < 4:
            ax.bar(i, v, bottom=cum[i], color=c, edgecolor=TEXT, lw=0.6)
        else:
            ax.bar(i, cum[i], color=c, edgecolor=TEXT, lw=0.6)
    ax.axhline(-120, color=RED, ls="--", lw=1, label="LoRa sensitivity SF7/BW125")
    ax.set_xticks(range(len(bars))); ax.set_xticklabels(bars)
    ax.set_ylabel("dBm"); ax.legend(frameon=False)
    show(fig)


def _sim_solar_harvest():
    section_h("Solar harvest - Wh per day by month")
    tilt = st.slider("Panel tilt (deg)", 0, 60, 25)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    peak_sun = 4.5 + 1.5 * np.cos(np.linspace(0, 2 * np.pi, 12))
    factor = np.cos(np.radians(tilt - 25))
    wh = 20 * peak_sun * factor
    fig, ax = plt.subplots(figsize=(11, 3.5))
    ax.bar(months, wh, color=AMBER, edgecolor=TEXT, lw=0.6)
    ax.axhline(40, color=GREEN, ls="--", lw=1, label="daily need (40 Wh)")
    ax.set_ylabel("Wh / day"); ax.legend(frameon=False)
    show(fig)


def _sim_power_budget():
    section_h("Power budget - daily energy in vs out")
    load = st.slider("Always-on load (mA @ 3.3 V)", 40, 200, 80)
    tx_per_day = st.slider("TX bursts per day", 1, 500, 60)
    in_wh = 45
    base = load * 3.3 * 24 / 1000
    tx = tx_per_day * 1.5
    out_wh = base + tx
    fig, ax = plt.subplots(figsize=(11, 3.0))
    ax.bar(["Harvest", "ESP32 base", "TX bursts", "Net"],
           [in_wh, base, tx, in_wh - out_wh],
           color=[GREEN, BLUE, ORANGE,
                  GREEN if in_wh > out_wh else RED],
           edgecolor=TEXT, lw=0.6)
    ax.axhline(0, color=TEXT, lw=0.8)
    ax.set_ylabel("Wh / day")
    show(fig)


def render_power():
    page_title("Power",
               "Solar pod, MPPT, battery, buck converters and energy budget.")
    section_h("Power tree")
    diagram_power()
    section_h("Energy budget")
    cols = st.columns(4)
    cards = [
        ("Harvest (Dec)",       "32 Wh/day"),
        ("Always-on load",      "6.3 Wh/day"),
        ("TX bursts (60/d)",    "1.5 Wh/day"),
        ("Net",                 "+ 24 Wh/day surplus"),
    ]
    for c, (lbl, val) in zip(cols, cards):
        c.markdown(
            f'<div class="kpi"><div class="kpi-lbl">{lbl}</div>'
            f'<div class="kpi-val">{val}</div></div>',
            unsafe_allow_html=True,
        )
    section_h("Battery")
    st.markdown(
        "12 V / 20 Ah LiFePO4 -> **240 Wh**. Worst-case dark-day autonomy "
        "= (240 - daily load) / daily load approx **41 days** without sun."
    )


def render_lora():
    page_title("LoRa Link",
               "868 MHz LoRa from pod to gateway, GSM as fallback.")
    section_h("Topology")
    diagram_lora()
    section_h("Link budget - interactive")
    _sim_lora_budget()


def render_enclosure():
    page_title("Enclosure",
               "IP67 belt-mounted pod, glands, vibration isolation.")
    section_h("Cross-section")
    diagram_enclosure()
    section_h("Survival kit")
    bullets = [
        "IP67 die-cast aluminium body, polycarbonate clear lid, 4x M4 captive screws",
        "Silicone gasket - re-coat yearly",
        "Two PG glands: one for 12 V solar feed, one for the sensor loom",
        "Goretek IP67 vent for pressure equalisation (no condensation)",
        "Carrier PCB on silicone vibration isolators - no direct metal path",
        "Stainless L-bracket clamped to belt frame (not welded - belt moves)",
        "Conformal coating (HumiSeal 1B73) on PCB after assembly",
    ]
    for b in bullets:
        st.markdown(f"- {b}")
def render_bom():
    page_title("BOM", "Bill of materials with INR + USD totals.")
    rows = [
        ("ESP32-WROOM-32 dev board",      1,  450),
        ("LoRa RA-02 (SX1278) 868 MHz",   1,  650),
        ("SIM800L GSM module",            1,  450),
        ("ADXL345 vibration",             1,  180),
        ("DS18B20 + 4.7 kohm",            1,   95),
        ("HX711 + 1 t S-type load cell",  1,  650),
        ("E18-D80NK IR tear (pair)",      2,  280),
        ("A3144 Hall + magnet",           1,   40),
        ("ACS712-30A current",            1,  220),
        ("GP2Y1010AU0F dust",             1,  950),
        ("MQ-2 gas",                      1,  180),
        ("MQ-135 air quality",            1,  200),
        ("IP67 enclosure 150x100x70",     1,  620),
        ("20 W mono solar panel",         1, 1900),
        ("MPPT CN3791 + DW01 BMS",        1,  380),
        ("12 V 20 Ah LiFePO4 (32700x4)",  1, 4200),
        ("LM2596 buck + AMS1117 LDO",     1,  120),
        ("PG7 / PG9 cable glands",        2,   60),
        ("Misc (wires, fuses, TVS, R, C)", 1,  300),
    ]
    total = sum(q * p for _, q, p in rows)
    usd = total / 83
    st.markdown(
        "| Item | Qty | Unit (INR) | Line (INR) |\n"
        "|---|---:|---:|---:|\n"
        + "\n".join(
            f"| {n} | {q} | {p} | {q*p} |"
            for n, q, p in rows
        )
        + f"\n| **Total** | | | **{total} INR  approx  ${usd:.0f} USD** |"
    )


def render_install():
    page_title("Install",
               "Step-by-step install walkthrough for one belt.")
    steps = [
        ("Survey the belt",
         "Walk the belt, note head-pulley height, take-up carriage travel, "
         "where the maintenance cabin sits. Confirm LoS for LoRa (or plan "
         "for a Yagi + repeater)."),
        ("Mount the solar pod",
         "On the tunnel roof or a pole 5-10 m from the belt, south in the "
         "northern hemisphere, clear of dust plumes. Aim the panel."),
        ("Mount the belt pod",
         "Stainless L-bracket clamped to the belt frame at the head-pulley "
         "side, clear of the take-up carriage. Leave 0.5 m of slack cable."),
        ("Wire it up",
         "12 V from solar pod to pod. Sensor loom up: DS18B20 probe pressed "
         "against the belt carcass, ADXL345 epoxied to bearing housing, "
         "load cell on the take-up carriage, IR pair across the belt."),
        ("Power up & pair",
         "Power on. ESP32 boots, joins LoRa, gateway hears it. SMS test "
         "to the maintenance phone."),
        ("Calibrate & hand over",
         "Dead-weight the load cell, set the take-up PID, set OK/WARN/ALARM "
         "thresholds, train the cabin operator on the dashboard."),
    ]
    for i, (title, body) in enumerate(steps, start=1):
        with st.expander(f"{i}. {title}"):
            st.markdown(body)
# SIDEBAR - sub-navigation (sensor deep-dives).
# The TOP TAB BAR below is ALSO a complete navigation path, so collapsing
# this sidebar can never lock the user out.
with st.sidebar:
    st.markdown(
        f'<p style="font-size:1.3rem;font-weight:800;color:{BLUE};'
        f'margin:0">BeltGuard</p>',
        unsafe_allow_html=True,
    )
    st.caption("Mine conveyor belt safety monitor")

    sub = st.radio(
        "Sensor deep-dives",
        ["(none)"] + [s["name"] for s in SENSOR_DEFS],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("Reset session"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.caption("v2.0 / 2026 - light theme")

# If the sidebar selected a sensor, render that sensor's deep-dive and stop.
# Otherwise fall through to the top tab bar.
if sub != "(none)":
    for s in SENSOR_DEFS:
        if s["name"] == sub:
            render_sensor_page(s)
            st.stop()


# TOP TAB BAR - always visible, even when sidebar is collapsed
st.markdown(
    '<p class="big-title">BeltGuard</p>'
    '<p class="sub-title">A solar-powered sensor pod that watches every '
    'metre of every belt, 24 x 7.</p>',
    unsafe_allow_html=True,
)

tab_names = [
    "Overview", "Architecture", "Sensor Pod", "Live Telemetry",
    "Simulations", "Power", "LoRa Link", "Enclosure", "BOM", "Install",
]
(*tabs,) = st.tabs(tab_names)

with tabs[0]:
    render_overview()
with tabs[1]:
    render_architecture()
with tabs[2]:
    render_sensor_pod()
with tabs[3]:
    render_live_telemetry()
with tabs[4]:
    render_simulations()
with tabs[5]:
    render_power()
with tabs[6]:
    render_lora()
with tabs[7]:
    render_enclosure()
with tabs[8]:
    render_bom()
with tabs[9]:
    render_install()
