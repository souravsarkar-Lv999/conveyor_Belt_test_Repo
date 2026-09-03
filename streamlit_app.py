"""
Smart Mine Conveyor-Belt Health-Monitor — Interactive Website (Streamlit)

A Streamlit app that turns the entire hardware design into an interactive
visual demo for hackathon judges.

Run:
    pip install -r requirements.txt
    streamlit run streamlit_app.py
"""

from pathlib import Path
import io
import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")               # headless, no display needed
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

# Force matplotlib to use the same dark theme as Streamlit
plt.rcParams.update({
    "figure.facecolor":  "#0d1117",
    "axes.facecolor":    "#0d1117",
    "axes.edgecolor":    "#0d1117",
    "savefig.facecolor": "#0d1117",
    "savefig.edgecolor": "#0d1117",
    "text.color":        "white",
    "axes.labelcolor":   "white",
    "xtick.color":       "white",
    "ytick.color":       "white",
    "font.family":       "DejaVu Sans",
})

# =====================================================================
# PAGE CONFIG — section selector lives in a TOP TAB BAR, not a sidebar,
# so the user can never lose navigation by collapsing the sidebar.
# =====================================================================
st.set_page_config(
    page_title="BeltGuard — Mine Conveyor Safety",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)
ROOT = Path(__file__).resolve().parent

# =====================================================================
# CSS
# =====================================================================
st.markdown("""
<style>
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    [data-testid="stToolbar"] { visibility: hidden; }
    [data-testid="stStatusWidget"] { visibility: hidden; }
    .block-container { padding-top: 1.0rem; padding-bottom: 1.0rem; }

    .big-title   { font-size:2.8rem; font-weight:800; line-height:1.05;
                   background: linear-gradient(90deg,#ff8800,#ff3300);
                   -webkit-background-clip:text; color:transparent;
                   margin-bottom:0.1rem; }
    .sub-title   { font-size:1.15rem; color:#888; margin-top:-0.4rem; }

    .metric-card { background:#1e1e1e; padding:1rem 1.2rem; border-radius:0.8rem;
                   border-left:6px solid #ff8800; margin-bottom:0.4rem; }
    .ok          { color:#00d68f; font-weight:bold; }
    .warn        { color:#ffaa00; font-weight:bold; }
    .crit        { color:#ff3333; font-weight:bold; }

    /* Make the top tab bar stand out */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        background: #161b22;
        padding: 0.5rem 0.7rem;
        border-radius: 0.6rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.0rem;
        font-weight: 600;
        padding: 0.6rem 1.1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# VISUAL PRIMITIVES
# =====================================================================
def draw_block(ax, x, y, w, h, label, color="#ff8800", textcolor="white",
               fontsize=10, radius=0.12):
    """Draw a rounded, labeled block — no emojis (matplotlib fonts don't have them)."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=1.5, edgecolor=color, facecolor=color, alpha=0.92,
    )
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, label,
            ha="center", va="center",
            color=textcolor, fontsize=fontsize, fontweight="bold")


def draw_arrow(ax, x1, y1, x2, y2, color="#888", lw=2):
    """Draw a clean arrow without white-background artifacts."""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=18, color=color, lw=lw,
        shrinkA=0, shrinkB=0,
    )
    ax.add_patch(arrow)


def show(fig):
    """Render a matplotlib figure in Streamlit with NO white box around it."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight",
                transparent=False, facecolor="#0d1117")
    plt.close(fig)
    buf.seek(0)
    st.image(buf, use_container_width=True)


# =====================================================================
# RENDER FUNCTIONS
# =====================================================================
def render_architecture():
    st.markdown("## System Architecture")
    st.caption("Hardware loop — sensors on belt -> radio -> maintenance cabin.")

    fig, ax = plt.subplots(figsize=(14, 7.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")

    # Belt (drawn first so other blocks sit above it)
    belt_y = 1.0
    ax.add_patch(Rectangle((0.4, belt_y - 0.18), 6.0, 0.36,
                           color="#666", zorder=1))
    ax.text(3.4, belt_y, "Conveyor Belt", ha="center", va="center",
            color="white", fontsize=11, fontweight="bold", zorder=2)

    # Pulleys
    for cx in [0.6, 6.2]:
        c = Circle((cx, belt_y), 0.28, color="#999", ec="white", lw=1.4, zorder=3)
        ax.add_patch(c)
    ax.text(0.6, belt_y - 0.55, "drive", ha="center", color="#aaa", fontsize=8)
    ax.text(6.2, belt_y - 0.55, "head",  ha="center", color="#aaa", fontsize=8)

    # ===== ROW 1: SENSORS (top) =====
    sensors = [
        (0.5, 6.6, "DS18B20\nbelt temp",  "#ff5555"),
        (2.3, 6.6, "ADXL345\nvibration",  "#55aaff"),
        (4.1, 6.6, "HX711\ntension",      "#cc66ff"),
        (5.9, 6.6, "E18 IR\ntear detect",  "#55ff88"),
        (7.7, 6.6, "MQ-2 / MQ-135\nsmoke / gas", "#ffcc55"),
    ]
    for x, y, lbl, c in sensors:
        draw_block(ax, x, y, 1.6, 0.9, lbl, color=c, fontsize=10)
        # Each sensor feeds the Belt Sensor Pod (line goes straight down to pod)
        ax.plot([x + 0.8, 4.2], [y, 4.6], color=c, lw=1.0, ls="--", alpha=0.5, zorder=0)

    # ===== ROW 2: BELT SENSOR POD (center) =====
    draw_block(ax, 3.0, 3.4, 2.4, 1.2,
               "BELT SENSOR POD\nESP32-WROOM\n10 sensors",
               color="#ff8800", fontsize=11)

    # ===== ROW 3: SOLAR POD (right) =====
    draw_block(ax, 10.0, 5.6, 3.2, 1.4,
               "SOLAR POD\n20 W panel + 12 V 20 Ah\nLiFePO4 + MPPT",
               color="#ffd700", textcolor="black", fontsize=10)

    # Power conversion chain (solar -> power rails -> pod)
    draw_block(ax, 10.0, 3.4, 3.2, 1.0,
               "POWER RAILS\n12 V -> 5 V (LM2596)\n-> 3.3 V (AMS1117)",
               color="#aa8800", fontsize=10)
    draw_arrow(ax, 11.6, 5.6, 11.6, 4.4, color="#ffd700", lw=2)

    # Power cable from rails to pod (curved arrow above the radio block so labels don't collide)
    draw_arrow(ax, 10.0, 3.9, 5.4, 3.9, color="#ffaa00", lw=2)
    ax.text(7.7, 4.15, "12 V power (cable <= 30 m)",
            color="#aaa", fontsize=8, ha="center")

    # ===== ROW 4: RADIO (pod -> gateway) =====
    # Move radio down to row below belt-pod to free up space for the power label.
    draw_block(ax, 6.2, 1.7, 2.0, 1.2,
               "LoRa SX1278\n868 MHz\n+ SIM800L GSM",
               color="#0088ff", fontsize=10)
    # Arrow from belt pod down-right to radio
    draw_arrow(ax, 5.4, 3.8, 6.2, 2.9, color="#ff8800", lw=2)

    # ===== ROW 5: GATEWAY =====
    draw_block(ax, 9.0, 1.6, 2.4, 1.0,
               "GATEWAY\nRA-02 + ESP32\n4G / WiFi uplink",
               color="#00aaff", fontsize=10)
    draw_arrow(ax, 7.2, 3.4, 9.0, 2.6, color="#0088ff", lw=2)
    ax.text(8.1, 3.1, "LoRa 2-5 km",
            color="#aaccff", fontsize=8, ha="center", fontweight="bold")

    # ===== ROW 6: CABIN =====
    draw_block(ax, 11.5, 1.6, 2.2, 1.0,
               "CABIN\ndashboard + siren\n+ SMS alerts",
               color="#00cc66", fontsize=10)
    draw_arrow(ax, 11.4, 2.1, 11.5, 2.1, color="#00cc66", lw=2)

    show(fig)

    # Detection paths
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        **Fire detect path**
        1. DS18B20 spots T > 70 °C
        2. MQ-2 / MQ-135 confirms smoke / gas
        3. -> Siren + SMS
        """)
    with c2:
        st.markdown("""
        **Tear detect path**
        1. E18 IR beam breaks
        2. ADXL345 records impulse
        3. HX711 shows tension drop
        """)
    with c3:
        st.markdown("""
        **Seizure / slip detect path**
        1. Hall RPM drops
        2. ACS712 current spikes
        3. ADXL345 RMS rises
        """)


def render_sensor_pod():
    st.markdown("## Sensor Pod")
    tab1, tab2, tab3 = st.tabs(["3D model", "Internal layout", "Sensor map"])

    with tab1:
        st.markdown("### 3D reference model")
        st.caption("Download the .glb, open in Blender or Windows 3D Viewer.")
        glb = ROOT / "assets" / "quarry_conveyor_system_kit.glb"
        if glb.exists():
            with open(glb, "rb") as f:
                st.download_button(
                    "Download .glb 3D model (6.9 MB)",
                    data=f.read(),
                    file_name="quarry_conveyor_belt.glb",
                    mime="model/gltf-binary",
                )
            st.info("Tip: also browse assets/ for reference photos.")
        st.markdown("**Reference photos:**")
        col1, col2, col3 = st.columns(3)
        for col, name in zip(
            [col1, col2, col3],
            ["Basic-components-of-a-conveyor-belt-800x400.webp",
             "Parts-of-the-conveyor-belt-a-Belt-The-belt-is-consisting-of-2-or-more-layers-of.webp",
             "oreflow-2-min.jpg.webp"],
        ):
            p = ROOT / "assets" / name
            if p.exists():
                col.image(str(p), use_column_width=True,
                          caption=name.split(".")[0][:40])

    with tab2:
        st.markdown("### Internal layout (top-down)")
        st.caption("Die-cast aluminium IP67 enclosure, 240 x 160 x 90 mm.")
        fig, ax = plt.subplots(figsize=(11, 6.5))
        ax.set_xlim(0, 11); ax.set_ylim(0, 7); ax.axis("off")

        # Outer box
        ax.add_patch(Rectangle((0.2, 0.2), 10.6, 6.6, fill=False,
                               edgecolor="#ff8800", lw=3))
        ax.text(5.5, 6.45, "Die-cast aluminium, IP67, 240 x 160 x 90 mm",
                ha="center", color="#ff8800", fontsize=11, fontweight="bold")

        # Components
        draw_block(ax, 0.5, 3.0, 2.4, 1.4,
                   "ESP32-WROOM\nmain controller", color="#0077ff", fontsize=10)
        draw_block(ax, 0.5, 1.4, 2.4, 1.2,
                   "SX1278 LoRa\n868 MHz",          color="#0088ff", fontsize=10)
        draw_block(ax, 0.5, 0.3, 2.4, 0.9,
                   "SIM800L GSM\nSMS fallback",     color="#ff3333", fontsize=10)
        draw_block(ax, 3.5, 3.5, 3.0, 1.5,
                   "Carrier PCB\n(sensors + power)", color="#aa00aa", fontsize=10)
        draw_block(ax, 3.5, 1.4, 3.0, 1.6,
                   "DS18B20  NTC\nADXL345  HX711\nACS712  Hall", color="#ff5555", fontsize=9)
        draw_block(ax, 7.5, 4.5, 3.0, 1.0,
                   "LM2596  12 V -> 5 V",            color="#cc8800", fontsize=10)
        draw_block(ax, 7.5, 3.0, 3.0, 1.0,
                   "AMS1117  5 V -> 3.3 V",         color="#cc8800", fontsize=10)
        draw_block(ax, 7.5, 1.4, 3.0, 1.2,
                   "OLED 0.96\"\n+ Buzzer",          color="#666", fontsize=10)

        # Antenna feedthroughs
        ax.add_patch(Circle((1.0, 6.4), 0.18, color="#fff", ec="white"))
        ax.text(1.0, 6.75, "LoRa ant", color="white", ha="center", fontsize=8)
        ax.add_patch(Circle((2.3, 6.4), 0.15, color="#fff", ec="white"))
        ax.text(2.3, 6.75, "GSM ant", color="white", ha="center", fontsize=8)

        # Cable glands on bottom
        for x, lbl in [(4.5, "tear IR"), (6.0, "RPM"),
                       (7.5, "strain"), (9.0, "solar 12V")]:
            ax.add_patch(Circle((x, 0.5), 0.18, color="#aaa"))
            ax.text(x, 1.0, lbl, color="#aaa", ha="center", fontsize=8)

        show(fig)

    with tab3:
        st.markdown("### Where each sensor sits on the belt")
        fig, ax = plt.subplots(figsize=(14, 4.5))
        ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis("off")

        # Belt
        ax.add_patch(Rectangle((0.5, 2.0), 13.0, 0.6, color="#666"))
        # Idlers
        for x in [1.0, 3.5, 6.0, 8.5, 11.0, 13.0]:
            ax.add_patch(Circle((x, 2.0), 0.22, color="#999", ec="white"))

        # Sensor pod
        draw_block(ax, 5.5, 2.7, 3.0, 0.9, "BELT SENSOR POD",
                   color="#ff8800", fontsize=11)

        # Annotations
        ann = [
            (1.0,  0.6, "ADXL345\non idler",          "#55aaff"),
            (6.0,  4.2, "DS18B20\nunder pod",          "#ff5555"),
            (9.0,  4.2, "HX711\non take-up\nframe",     "#cc66ff"),
            (13.0, 0.6, "E18 IR\nat head pulley",      "#55ff88"),
            (13.0, 4.2, "Hall RPM\nat drive pulley",   "#ffcc55"),
        ]
        for x, y, lbl, c in ann:
            ax.annotate(lbl, xy=(x, 2.3), xytext=(x, y),
                        ha="center", color=c, fontsize=9, fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color=c, lw=1.4))

        show(fig)


def render_live_telemetry():
    st.markdown("## Live Telemetry Dashboard")
    st.caption("Simulated feed from one pod. (Replace with real LoRa receiver in production.)")

    if "telemetry_data" not in st.session_state:
        np.random.seed(int(time.time()) % 1000)
        st.session_state.telemetry_data = pd.DataFrame({
            "time":   pd.date_range("2026-09-04 00:00", periods=200, freq="1min"),
            "temp_C": 35 + 2*np.random.randn(200).cumsum()*0.05,
            "vib_g":  np.abs(0.4 + 0.1*np.random.randn(200).cumsum()),
            "rpm":    600 + 5*np.sin(np.linspace(0, 20, 200)) + 2*np.random.randn(200),
            "rssi":   -85 - 3*np.random.randn(200),
            "soc_pct":np.clip(82 - 0.05*np.arange(200) + 0.5*np.random.randn(200), 0, 100),
        })

    df = st.session_state.telemetry_data

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Belt temp",  f"{df['temp_C'].iloc[-1]:.1f} °C",
              delta=f"{df['temp_C'].iloc[-1]-df['temp_C'].iloc[-2]:+.1f}")
    c2.metric("Vibration",  f"{df['vib_g'].iloc[-1]:.2f} g",
              delta=f"{df['vib_g'].iloc[-1]-df['vib_g'].iloc[-2]:+.2f}")
    c3.metric("Drive RPM",  f"{df['rpm'].iloc[-1]:.0f}",
              delta=f"{df['rpm'].iloc[-1]-df['rpm'].iloc[-2]:+.0f}")
    c4.metric("LoRa RSSI",  f"{df['rssi'].iloc[-1]:.0f} dBm")
    c5.metric("Battery",    f"{df['soc_pct'].iloc[-1]:.0f} %")
    status = "OK"
    if df['temp_C'].iloc[-1] > 70 or df['vib_g'].iloc[-1] > 1.0:
        status = "ALARM"
    elif df['temp_C'].iloc[-1] > 55 or df['vib_g'].iloc[-1] > 0.7:
        status = "WARN"
    c6.metric("Status", status)

    st.markdown("---")

    fig, axes = plt.subplots(2, 2, figsize=(14, 6))
    axes[0, 0].plot(df["time"], df["temp_C"], color="#ff5555")
    axes[0, 0].axhline(70, color="red", ls="--", alpha=0.5)
    axes[0, 0].set_title("Belt temperature (C)")
    axes[0, 0].grid(alpha=0.2)

    axes[0, 1].plot(df["time"], df["vib_g"], color="#55aaff")
    axes[0, 1].axhline(0.8, color="red", ls="--", alpha=0.5)
    axes[0, 1].set_title("Vibration RMS (g)")
    axes[0, 1].grid(alpha=0.2)

    axes[1, 0].plot(df["time"], df["rpm"], color="#55ff88")
    axes[1, 0].set_title("Drive RPM")
    axes[1, 0].grid(alpha=0.2)

    axes[1, 1].plot(df["time"], df["soc_pct"], color="#ffaa00")
    axes[1, 1].set_title("Battery SoC (%)")
    axes[1, 1].set_ylim(0, 100)
    axes[1, 1].grid(alpha=0.2)

    for ax in axes.flat:
        ax.tick_params(axis="x", rotation=30, labelsize=8)
    fig.tight_layout()
    show(fig)

    if st.button("Inject simulated belt fire (demo)"):
        df.loc[df.index[-1], "temp_C"] = 85.0
        df.loc[df.index[-1], "vib_g"] = 1.4
        st.session_state.telemetry_data = df
        st.error("ALARM: Belt temp > 70 C and vibration > 1 g -> fire suspected. SMS dispatched.")


def render_simulations():
    st.markdown("## Simulations — interactive plots")
    sim = st.selectbox("Pick a simulation", [
        "Power budget (battery over 7 days)",
        "Solar harvest (panel over 1 week)",
        "LoRa link budget (RSSI vs distance)",
        "Vibration FFT (3x RPM fault peak)",
        "Belt thermal / fire",
        "Strain-gauge calibration",
    ])

    if "Power budget" in sim:
        st.markdown("### 12 V 20 Ah LiFePO4 — autonomy")
        c1, c2 = st.columns(2)
        load_w = c1.slider("Continuous load (W)", 0.1, 3.0, 0.3, 0.05)
        days   = c2.slider("Days to simulate", 1, 30, 7)
        e = 205
        t = np.arange(0, days*24 + 1)
        soc = np.array([max(0, (e := e - load_w)) for _ in t]) / 205
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(t/24, soc*100, lw=2, color="#ffaa00")
        ax.axhline(20, color="red", ls="--", label="BMS cutoff 20%")
        ax.set_xlabel("Days"); ax.set_ylabel("State of charge (%)")
        ax.grid(alpha=0.2); ax.legend()
        show(fig)

    elif "Solar harvest" in sim:
        st.markdown("### Solar panel — harvest vs weather")
        c1, c2 = st.columns(2)
        panel_w   = c1.slider("Panel size (W)", 5, 50, 20)
        weather   = c2.slider("Sun-hours equivalent (h/day)", 1.0, 6.0, 4.5)
        load_wh_d = st.slider("Daily load (Wh/day)", 5, 50, 10)
        harvest = panel_w * weather * 0.75
        net = harvest - load_wh_d
        fig, ax = plt.subplots(figsize=(10, 4))
        bars = ["Daily harvest", "Daily load", "Net"]
        ax.bar(bars, [harvest, load_wh_d, net],
               color=["#55ff88", "#ffaa00", "#55aaff"])
        ax.axhline(0, color="white", lw=0.5)
        for i, v in enumerate([harvest, load_wh_d, net]):
            ax.text(i, v + (1 if v>=0 else -3), f"{v:.1f} Wh",
                    ha="center", fontweight="bold")
        ax.set_ylabel("Wh/day")
        show(fig)
        st.info(f"Net {net:+.1f} Wh/day — battery {'gains' if net>0 else 'loses'} "
                f"{abs(net)/12/20*24*100/205:.1f}% SoC per day.")

    elif "LoRa link budget" in sim:
        st.markdown("### LoRa 868 MHz — RSSI vs distance")
        c1, c2 = st.columns(2)
        tx_dbm = c1.slider("TX power (dBm)", 2, 20, 14)
        rock_l = c2.slider("Rock-wall penalty (dB)", 0, 30, 12)
        d = np.linspace(0.1, 10, 500)
        fspl = 32.45 + 20*np.log10(d) + 20*np.log10(868)
        rssi = tx_dbm + 3 + 3 - 1.5 - fspl - rock_l
        sens = -137
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(d, rssi, lw=2, color="#55aaff")
        ax.axhline(sens, color="white", ls="--", label=f"Sens {sens} dBm")
        cross = d[np.where(rssi < sens)[0][0]] if (rssi < sens).any() else 10
        ax.axvline(cross, color="red", ls=":",
                   label=f"Max range ~ {cross:.1f} km")
        ax.fill_between(d, rssi, -160, where=(rssi > sens),
                        color="#55ff88", alpha=0.15)
        ax.fill_between(d, rssi, -160, where=(rssi < sens),
                        color="#ff5555", alpha=0.15)
        ax.set_xlabel("Distance (km)"); ax.set_ylabel("RSSI (dBm)")
        ax.set_ylim(-160, -60); ax.grid(alpha=0.2); ax.legend()
        show(fig)

    elif "Vibration FFT" in sim:
        st.markdown("### ADXL345 vibration — 3x RPM fault peak")
        rpm = st.slider("Drive RPM", 100, 1200, 600)
        fs, dur = 200, 3
        t = np.linspace(0, dur, fs*dur)
        rpm1 = rpm/60; rpm3 = 3*rpm/60
        healthy = 0.3*np.sin(2*np.pi*rpm1*t) + 0.1*np.random.randn(len(t))
        failing = healthy + 1.0*np.sin(2*np.pi*rpm3*t) + 0.2*np.random.randn(len(t))
        f1 = np.fft.rfftfreq(len(healthy), 1/fs)
        m1 = np.abs(np.fft.rfft(healthy))*2/len(healthy)
        m2 = np.abs(np.fft.rfft(failing))*2/len(failing)
        fig, axes = plt.subplots(2, 1, figsize=(10, 6))
        axes[0].plot(t, healthy, label="healthy")
        axes[0].plot(t, failing, label="failing")
        axes[0].set_title("Time domain")
        axes[0].grid(alpha=0.2); axes[0].legend()
        axes[1].plot(f1, m1, label="healthy")
        axes[1].plot(f1, m2, label="failing")
        axes[1].axvline(rpm3, color="red", ls="--",
                        label=f"3x RPM = {rpm3:.1f} Hz")
        axes[1].set_xlim(0, 100)
        axes[1].set_title("FFT — fault peak at 3x RPM")
        axes[1].grid(alpha=0.2); axes[1].legend()
        fig.tight_layout()
        show(fig)

    elif "Belt thermal" in sim:
        st.markdown("### Belt fire — DS18B20 response")
        fire_w = st.slider("Fire heat flux (kW/m2)", 10, 100, 60)
        t = np.linspace(0, 600, 601)
        T_amb = 35
        flux = np.where(t < 120, 0,
                np.minimum(fire_w*1000, fire_w*1000*np.minimum(1,(t-120)/120)))
        dT = (flux/18000) * 1
        T = T_amb + np.cumsum(dT)/60
        T = np.minimum(T, 950)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(t/60, T, color="#ff5555", lw=2)
        ax.axhline(70, color="white", ls="--", label="Alarm 70 C")
        alarm = t[np.argmax(T > 70)] if (T > 70).any() else None
        if alarm is not None:
            ax.annotate(f"ALARM @ {alarm/60:.1f} min",
                        xy=(alarm/60, 70), xytext=(alarm/60+0.5, 200),
                        color="white", fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color="red"))
        ax.set_xlabel("Time (min)"); ax.set_ylabel("Belt surface T (C)")
        ax.grid(alpha=0.2); ax.legend()
        show(fig)

    elif "Strain-gauge" in sim:
        st.markdown("### HX711 + BF350 strain gauge — calibration")
        tension_n = st.slider("Belt tension (N)", 0, 10000, 5000)
        code = tension_n * 2097.152
        nf = 21.0
        fig, ax = plt.subplots(figsize=(10, 4))
        tens  = np.linspace(0, 10000, 500)
        codes = tens * 2097.152
        ax.plot(tens, codes, lw=2, color="#cc66ff")
        ax.scatter([tension_n], [code], color="red", s=100, zorder=5,
                   label=f"You: {code:,.0f} counts")
        ax.axhline( nf, color="red", ls="--", alpha=0.5, label=f"Noise +/-{nf:.0f}")
        ax.axhline(-nf, color="red", ls="--", alpha=0.5)
        ax.set_xlabel("Belt tension (N)"); ax.set_ylabel("HX711 ADC code")
        ax.grid(alpha=0.2); ax.legend()
        show(fig)


def render_power():
    st.markdown("## Power System")
    st.caption("Solar pod = panel + MPPT + LiFePO4 + buck converters.")
    st.markdown("""
    | Item                              | Spec                                       |
    |-----------------------------------|--------------------------------------------|
    | Panel                             | 20 W mono (Voc 22 V, Isc 1.2 A)            |
    | Controller                       | EPever Tracer 1210AN, 10 A MPPT            |
    | Battery                          | 12 V 20 Ah LiFePO4 (256 Wh, 80% DoD = 205 Wh) |
    | Buck 5 V                         | LM2596-ADJ (3 A)                           |
    | LDO 3.3 V                        | AMS1117-3.3                               |
    """)
    st.markdown("---")
    st.markdown("### Energy budget")
    data = {
        "Mode":          ["Sleep", "Active", "Alarm", "Continuous TX"],
        "Current (mA)":  [3,       80,       200,     500],
        "Hours/day":     [20,      3,        0.5,     0.5],
    }
    df = pd.DataFrame(data)
    df["mAh/day"] = df["Current (mA)"] * df["Hours/day"]
    df["Wh/day"]  = df["mAh/day"] * 3.3 / 1000 * 1.3
    st.dataframe(df, use_container_width=True, hide_index=True)
    total_wh = df["Wh/day"].sum()
    st.metric("Total energy",  f"{total_wh:.1f} Wh/day",
              delta=f"{20*4*0.75 - total_wh:+.1f} Wh/day solar surplus")


def render_lora():
    st.markdown("## LoRa Radio Link — hardware")
    st.caption("868 MHz ISM band, no SIM required, works through rock.")
    st.markdown("""
    - **Modem**: Semtech SX1278 (RA-02 module) on SPI
    - **Band**: 868 MHz (India / EU sub-GHz ISM, no licence needed)
    - **Spreading factor**: SF12, BW 125 kHz, CR 4/5 -> sensitivity **-137 dBm**
    - **TX power**: +14 dBm (about 25 mW)
    - **Antenna**: 3 dBi omni fiberglass, vertical, 2 m above ground
    - **Range**: 2-5 km line-of-sight, ~500 m through 1 rock wall
    - **Fallback**: SIM800L GSM module (SMS only, 1 message / hour)
    - **Encryption**: AES-128 (LoRaWAN AppKey + NwkSKey)
    """)
    # Hardware block diagram of the radio chain
    fig, ax = plt.subplots(figsize=(14, 4.5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5); ax.axis("off")
    draw_block(ax, 0.2, 1.6, 1.8, 1.2, "ESP32\nSPI bus", color="#0077ff", fontsize=10)
    draw_arrow(ax, 2.0, 2.2, 2.6, 2.2)
    draw_block(ax, 2.6, 1.6, 1.8, 1.2, "SX1278\nRA-02", color="#0088ff", fontsize=10)
    draw_arrow(ax, 4.4, 2.2, 5.0, 2.2)
    draw_block(ax, 5.0, 1.6, 2.0, 1.2, "SMA\nfeedthrough", color="#444", fontsize=10)
    draw_arrow(ax, 7.0, 2.2, 7.6, 2.2)
    draw_block(ax, 7.6, 1.6, 2.4, 1.2, "3 dBi\nfiber-glass ant",
               color="#ff8800", fontsize=10)
    ax.annotate("868 MHz\n2-5 km LoS", xy=(11.0, 2.2), xytext=(11.0, 4.2),
                color="white", ha="center", fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="white"))
    draw_block(ax, 10.4, 0.4, 3.0, 1.0,
               "GATEWAY\nRA-02 + ESP32 + 4G",
               color="#00cc66", fontsize=10)
    show(fig)


def render_bom():
    st.markdown("## Bill of Materials")
    bom = [
        ("ESP32-WROOM-32",                  "Main controller",            1,  350),
        ("SX1278 (RA-02) LoRa module",      "868 MHz radio",              1,  450),
        ("SIM800L GSM module",              "SMS fallback",               1,  650),
        ("ADXL345 IMU",                     "Vibration",                  1,  220),
        ("HX711 + BF350-3AA strain gauge",  "Belt tension",               1,  380),
        ("DS18B20 temp probe",              "Belt surface temp",          2,  110),
        ("NTC 10 kOhm thermistor",          "Ambient + secondary temp",   2,   35),
        ("Hall-effect pickup (A3144)",      "RPM",                        1,   80),
        ("E18-IR80NK IR proximity",         "Tear detect",                2,  180),
        ("ACS712-20A current sensor",       "Drive motor current",        1,  220),
        ("GP2Y1010 dust sensor",            "PM2.5",                      1,  380),
        ("MQ-2 gas sensor",                 "Smoke / LPG",                1,  180),
        ("MQ-135 gas sensor",               "CO / CH4 / NH3",             1,  220),
        ('OLED 0.96" I2C',                  "Local display",              1,  180),
        ("Buzzer 5 V active",               "Local alarm",                1,   40),
        ("LM2596-ADJ buck",                 "12 -> 5 V",                  1,   90),
        ("AMS1117-3.3 LDO",                 "5 -> 3.3 V",                 1,   20),
        ("20 W solar panel",                "Power",                      1, 1400),
        ("EPever Tracer 1210AN MPPT",       "Charge controller",          1, 1800),
        ("12 V 20 Ah LiFePO4 battery",      "Storage",                    1, 6800),
        ("Die-cast aluminium box 240x160",  "Enclosure IP67",             1, 1500),
        ("M10 U-bolts, cable glands",       "Mounting hardware",          1,  600),
    ]
    df = pd.DataFrame(bom, columns=["Component", "Function", "Qty", "INR"])
    df["Total"] = df["INR"] * df["Qty"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    total = df["Total"].sum()
    st.metric("Total per belt pod", f"INR {total:,}", f"~ USD {total/83:.0f}")


def render_install():
    st.markdown("## Installation walkthrough")
    steps = [
        ("Mount the bracket",
         "Weld the M10 U-bolt bracket to the take-up frame, 30 cm from the head pulley."),
        ("Bolt the pod",
         "Bolt the IP67 box to the bracket. Torque to 35 Nm."),
        ("Wire sensors",
         "Land the DS18B20, ADXL345, strain-gauge, Hall, E18-IR, ACS712, MQ-2, MQ-135, GP2Y wires on the carrier PCB."),
        ("Solar pod",
         "Mount the solar panel on the belt-stringer pole, true south, 30 deg tilt. Run 12 V cable <= 30 m."),
        ("Power on",
         "Press the BOOT button — OLED shows firmware version, then READY."),
        ("Pair with gateway",
         "Hold PAIR on the cabin gateway for 5 s; LED blinks green when the pod joins."),
        ("Commissioning",
         "Run belt empty for 5 min; verify vibration FFT shows clean 1x RPM peak; tension baseline stored."),
        ("Lock and tag",
         "Close the box, torque the lid screws to 4 Nm, attach tamper seal."),
    ]
    for i, (title, body) in enumerate(steps, start=1):
        with st.expander(f"{i}. {title}"):
            st.markdown(body)


# =====================================================================
# TOP TAB BAR  (replaces sidebar — never lose navigation)
# =====================================================================
st.markdown('<p class="big-title">BeltGuard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">A solar-powered sensor pod that watches '
            'every metre of every belt, 24x7.</p>', unsafe_allow_html=True)

tab_names = [
    "Overview",
    "Architecture",
    "Sensor Pod",
    "Live Telemetry",
    "Simulations",
    "Power",
    "LoRa Link",
    "BOM",
    "Install",
]
tab_overview, tab_arch, tab_pod, tab_tel, tab_sim, tab_pwr, tab_lora, tab_bom, tab_inst = (
    st.tabs(tab_names)
)

with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="metric-card"><b>Belt fires</b><br>'
                '<span class="crit">detected in <90 s</span></div>',
                unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><b>Belt tears</b><br>'
                '<span class="crit">detected in <2 s</span></div>',
                unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><b>LoRa range</b><br>'
                '<span class="ok">2-5 km LoS</span></div>',
                unsafe_allow_html=True)
    c4.markdown('<div class="metric-card"><b>Solar autonomy</b><br>'
                '<span class="ok">41 days</span></div>',
                unsafe_allow_html=True)
    st.markdown("---")
    render_architecture()

with tab_arch:
    render_architecture()

with tab_pod:
    render_sensor_pod()

with tab_tel:
    render_live_telemetry()

with tab_sim:
    render_simulations()

with tab_pwr:
    render_power()

with tab_lora:
    render_lora()

with tab_bom:
    render_bom()

with tab_inst:
    render_install()

# Footer with a "how to open sidebar" hint (sidebar starts collapsed)
st.markdown("---")
with st.sidebar:
    st.markdown("# BeltGuard")
    st.caption("Sidebar contents:")
    st.markdown(
        "Same tabs are above in the top bar. Use this sidebar for "
        "debug info, settings, or quick reset."
    )
    st.markdown("---")
    if st.button("Reset session"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
    st.caption("v1.0 / 2026")