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
import matplotlib.pyplot as plt
from matplotlib.patches import (
    FancyBboxPatch, Rectangle, FancyArrowPatch, Circle, Wedge
)

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="BeltGuard — Mine Conveyor Safety",
    page_icon="⛏",
    layout="wide",
    initial_sidebar_state="expanded",
)
ROOT = Path(__file__).resolve().parent

# =====================================================================
# CSS
# =====================================================================
st.markdown("""
<style>
    .big-title   { font-size:3.0rem; font-weight:800; line-height:1.1;
                   background: linear-gradient(90deg,#ff8800,#ff3300);
                   -webkit-background-clip:text; color:transparent; }
    .sub-title   { font-size:1.2rem; color:#888; margin-top:-0.6rem; }
    .metric-card { background:#1e1e1e; padding:1rem 1.2rem; border-radius:0.8rem;
                   border-left:6px solid #ff8800; margin-bottom:0.4rem; }
    .ok          { color:#00d68f; font-weight:bold; }
    .warn        { color:#ffaa00; font-weight:bold; }
    .crit        { color:#ff3333; font-weight:bold; }
    .pill        { display:inline-block; padding:0.15rem 0.7rem; border-radius:1rem;
                   background:#ff8800; color:black; font-size:0.85rem; font-weight:bold; }
    .stTabs [data-baseweb="tab-list"] button { font-size:1.05rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# VISUAL PRIMITIVES
# =====================================================================
def fig_to_buffer(fig):
    """Convert matplotlib figure to PNG bytes for st.image()."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def draw_block(x, y, w, h, label, color="#ff8800", ax=None, textcolor="white", fontsize=10):
    """Draw a labeled block."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.05,rounding_size=0.1",
                         linewidth=1.5, edgecolor=color, facecolor=color, alpha=0.85)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, label, ha="center", va="center",
            color=textcolor, fontsize=fontsize, fontweight="bold", wrap=True)

def draw_arrow(x1, y1, x2, y2, color="#666"):
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->",
                            mutation_scale=15, color=color, lw=2)
    plt.gca().add_patch(arrow)


# =====================================================================
# 1. ARCHITECTURE BLOCK DIAGRAM
# =====================================================================
def render_architecture():
    st.markdown("## 🏗 System Architecture")
    st.caption("Tap any block to learn more.")

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_facecolor("#0d1117")
    fig.patch.set_facecolor("#0d1117")

    # Belt
    ax.add_patch(Rectangle((0.3, 0.3), 6.4, 0.5, color="#444"))
    ax.text(3.5, 0.55, "Coal / Iron on Conveyor Belt", ha="center", color="white", fontsize=10, fontweight="bold")

    # Pulleys
    for cx, lbl in [(0.6, "Drive\npulley"), (6.4, "Head\npulley")]:
        c = Circle((cx, 0.55), 0.45, color="#888", ec="white", lw=1.5)
        ax.add_patch(c)
        ax.text(cx, 0.55, lbl, ha="center", va="center", color="black", fontsize=8, fontweight="bold")

    # Sensor pod (large)
    draw_block(2.4, 1.3, 2.2, 1.0, "📡  Belt Sensor Pod\nESP32 + 10 sensors",
               color="#ff8800", ax=ax, fontsize=11)
    draw_arrow(3.5, 1.3, 3.5, 0.85, color="#ff8800")

    # Solar pod
    draw_block(9.0, 5.0, 2.6, 1.0, "☀  Solar Pod\n20 W + 12 V 20 Ah",
               color="#ffd700", ax=ax, fontsize=10, textcolor="black")
    draw_arrow(10.3, 5.0, 10.3, 4.0, color="#ffd700")

    # Power flow
    draw_block(9.0, 3.2, 2.6, 0.7, "12 V → 5 V → 3.3 V",
               color="#aa8800", ax=ax, fontsize=9)
    draw_arrow(10.3, 3.2, 10.3, 2.3, color="#aa8800")
    draw_arrow(4.6, 1.8, 9.0, 1.8, color="#888")
    ax.text(6.8, 1.9, "power cable (≤30 m)", color="#aaa", fontsize=8)

    # Radio
    draw_block(2.4, 2.8, 2.2, 0.7, "LoRa 868 MHz\n+ GSM fallback",
               color="#0088ff", ax=ax, fontsize=10)
    draw_arrow(3.5, 2.8, 3.5, 2.3, color="#0088ff")

    # Gateway
    draw_block(7.0, 4.5, 1.8, 1.0, "🏠  Gateway\nLoRa + 4G/WiFi",
               color="#00aaff", ax=ax, fontsize=9)
    draw_arrow(4.6, 3.1, 7.0, 4.7, color="#0088ff")
    ax.text(5.6, 4.0, "LoRa\n2-5 km", color="#aaccff", fontsize=8)

    # Cabin
    draw_block(11.0, 4.5, 2.5, 1.4, "🖥  Maintenance Cabin\nDashboard + Siren\n+ SMS alerts",
               color="#00cc66", ax=ax, fontsize=10)
    draw_arrow(8.8, 5.0, 11.0, 5.0, color="#00cc66")

    # Sensor callouts (left side)
    sensors = [
        (0.1, 5.5, "🌡 DS18B20\nbelt temp"),
        (0.1, 4.6, "🛎 ADXL345\nvibration"),
        (0.1, 3.7, "🪢 HX711\ntension"),
        (0.1, 2.8, "👁 E18\ntear IR"),
        (0.1, 1.9, "💨 MQ-2\nsmoke"),
    ]
    for x, y, lbl in sensors:
        ax.add_patch(FancyBboxPatch((x, y), 1.7, 0.7,
                                    boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor="#222", edgecolor="#ff8800"))
        ax.text(x + 0.85, y + 0.35, lbl, ha="center", va="center",
                color="white", fontsize=8)
        # connection
        ax.plot([x + 1.7, 2.4], [y + 0.35, 1.8], color="#ff8800", lw=0.8, ls="--", alpha=0.6)

    ax.text(7, 0.1, "BeltGuard — end-to-end safety loop",
            ha="center", color="#888", fontsize=10, style="italic")

    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        ### 🔥 Fire detect path
        1. **DS18B20** spots T > 70 °C
        2. **MQ-2** confirms smoke rise
        3. → **Siren** + **SMS**
        """)
    with c2:
        st.markdown("""
        ### 🪢 Tear detect path
        1. **E18 IR** beam breaks
        2. **ADXL345** records impulse
        3. **HX711** shows tension drop
        """)
    with c3:
        st.markdown("""
        ### ⚙ Seizure detect path
        1. **RPM** Hall sensor drops
        2. **ACS712** current spikes
        3. **Vibration RMS** rises
        """)


# =====================================================================
# 2. SENSOR POD 3D MODEL + MOCKUP
# =====================================================================
def render_sensor_pod():
    st.markdown("## 🎛 Sensor Pod")

    tab1, tab2, tab3 = st.tabs(["🧊 3D model", "🪛 Internal layout", "📐 Sensor map"])

    with tab1:
        st.markdown("### 3D reference model")
        st.caption("Open this .glb file in Blender or Windows 3D Viewer for an interactive view.")
        glb = ROOT / "assets" / "quarry_conveyor_system_kit.glb"
        if glb.exists():
            with open(glb, "rb") as f:
                st.download_button(
                    "⬇ Download .glb 3D model (6.9 MB)",
                    data=f.read(),
                    file_name="quarry_conveyor_belt.glb",
                    mime="model/gltf-binary",
                )
            st.info("💡 Tip: also browse `assets/` for reference photos.")
        st.markdown("**Reference photos (you uploaded):**")
        col1, col2, col3 = st.columns(3)
        for col, name in zip(
            [col1, col2, col3],
            ["Basic-components-of-a-conveyor-belt-800x400.webp",
             "Parts-of-the-conveyor-belt-a-Belt-The-belt-is-consisting-of-2-or-more-layers-of.webp",
             "oreflow-2-min.jpg.webp"],
        ):
            p = ROOT / "assets" / name
            if p.exists():
                col.image(str(p), use_column_width=True, caption=name.split(".")[0][:40])

    with tab2:
        st.markdown("### Internal layout of the sensor pod")
        st.caption("Top-down view of the die-cast IP67 enclosure (240 × 160 × 90 mm).")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
        ax.set_facecolor("#0d1117"); fig.patch.set_facecolor("#0d1117")

        # Outer box
        ax.add_patch(Rectangle((0.2, 0.2), 9.6, 5.6, fill=False,
                               edgecolor="#ff8800", lw=3))
        ax.text(5, 5.45, "Die-cast aluminium, IP67, 240×160×90 mm",
                ha="center", color="#ff8800", fontsize=11, fontweight="bold")

        # ESP32
        draw_block(1.0, 3.0, 2.0, 1.0, "ESP32-WROOM\nmain controller", color="#0077ff", ax=ax, fontsize=10)
        # LoRa
        draw_block(1.0, 1.5, 2.0, 0.8, "SX1278 LoRa\n868 MHz", color="#0088ff", ax=ax, fontsize=10)
        # Battery carrier PCB
        draw_block(4.0, 3.5, 2.5, 1.5, "Carrier PCB\n(sensors + power)", color="#aa00aa", ax=ax, fontsize=10)
        # Buck converter
        draw_block(7.0, 4.0, 2.0, 0.7, "LM2596 12→5 V", color="#cc8800", ax=ax, fontsize=10)
        draw_block(7.0, 3.0, 2.0, 0.7, "AMS1117 5→3.3 V", color="#cc8800", ax=ax, fontsize=10)
        # OLED
        draw_block(7.0, 1.5, 2.0, 0.8, "OLED 0.96\"", color="#666", ax=ax, fontsize=10)
        # GSM
        draw_block(1.0, 0.4, 2.0, 0.8, "SIM800L GSM", color="#ff3333", ax=ax, fontsize=10)
        # Antenna feedthroughs
        ax.add_patch(Circle((0.5, 5.5), 0.12, color="white"))
        ax.text(0.5, 5.85, "LoRa ant", color="white", ha="center", fontsize=8)
        ax.add_patch(Circle((1.5, 5.5), 0.10, color="white"))
        ax.text(1.5, 5.85, "GSM ant", color="white", ha="center", fontsize=8)
        # Cable glands
        for x, lbl in [(3.0, "belt-edge\ntear IR"), (5.0, "RPM\nhall"),
                       (6.5, "strain\ngauge"), (8.5, "solar\n12V")]:
            ax.add_patch(Circle((x, 0.5), 0.15, color="#888"))
            ax.text(x, 1.0, lbl, color="#aaa", ha="center", fontsize=8)

        st.pyplot(fig)
        plt.close(fig)

    with tab3:
        st.markdown("### Where each sensor sits on the belt")
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
        ax.set_facecolor("#0d1117"); fig.patch.set_facecolor("#0d1117")

        # Belt
        ax.add_patch(Rectangle((0.5, 1.6), 11, 0.6, color="#444"))
        # Idlers
        for x in [1.0, 3.0, 5.0, 7.0, 9.0, 11.0]:
            ax.add_patch(Circle((x, 1.6), 0.2, color="#888"))
        # Pod
        ax.add_patch(FancyBboxPatch((4.5, 2.3), 3, 0.7,
                                    boxstyle="round,pad=0.05,rounding_size=0.1",
                                    facecolor="#ff8800", edgecolor="white"))
        ax.text(6, 2.65, "Sensor Pod", ha="center", color="black", fontweight="bold")

        # Labels
        ann = [
            (1.0, 0.5, "ADXL345\non idler 1", "#0077ff"),
            (5.0, 0.5, "DS18B20\nunder pod", "#ff3333"),
            (5.0, 3.4, "HX711\non take-up\nframe", "#aa00aa"),
            (10.0, 0.5, "E18 IR\nat head pulley", "#00aa00"),
            (8.5, 3.4, "Hall RPM\nat drive", "#ffaa00"),
        ]
        for x, y, lbl, c in ann:
            ax.annotate(lbl, xy=(x, 1.6), xytext=(x, y),
                        ha="center", color=c, fontsize=9, fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color=c, lw=1.5))

        st.pyplot(fig)
        plt.close(fig)


# =====================================================================
# 3. LIVE TELEMETRY (simulated)
# =====================================================================
def render_live_telemetry():
    st.markdown("## 📡 Live Telemetry Dashboard")
    st.caption("Simulated live feed from one pod. (Replace the mock generator with a real LoRa receiver in production.)")

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

    # Top metrics
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Belt temp",  f"{df['temp_C'].iloc[-1]:.1f} °C",
              delta=f"{df['temp_C'].iloc[-1]-df['temp_C'].iloc[-2]:+.1f}")
    c2.metric("Vibration",  f"{df['vib_g'].iloc[-1]:.2f} g",
              delta=f"{df['vib_g'].iloc[-1]-df['vib_g'].iloc[-2]:+.2f}")
    c3.metric("Drive RPM",  f"{df['rpm'].iloc[-1]:.0f}",
              delta=f"{df['rpm'].iloc[-1]-df['rpm'].iloc[-2]:+.0f}")
    c4.metric("LoRa RSSI",  f"{df['rssi'].iloc[-1]:.0f} dBm")
    c5.metric("Battery",    f"{df['soc_pct'].iloc[-1]:.0f} %")
    status = "🟢 OK"
    if df['temp_C'].iloc[-1] > 70 or df['vib_g'].iloc[-1] > 1.0:
        status = "🔴 ALARM"
    elif df['temp_C'].iloc[-1] > 55 or df['vib_g'].iloc[-1] > 0.7:
        status = "🟡 WARN"
    c6.metric("Status", status)

    st.markdown("---")

    # Live chart
    fig, axes = plt.subplots(2, 2, figsize=(14, 6))
    axes[0,0].plot(df["time"], df["temp_C"], color="red");   axes[0,0].set_title("Temperature (°C)")
    axes[0,0].axhline(70, color="red", ls="--", alpha=0.5); axes[0,0].grid(alpha=0.3)
    axes[0,1].plot(df["time"], df["vib_g"], color="blue");   axes[0,1].set_title("Vibration RMS (g)")
    axes[0,1].axhline(0.8, color="red", ls="--", alpha=0.5); axes[0,1].grid(alpha=0.3)
    axes[1,0].plot(df["time"], df["rpm"], color="green");    axes[1,0].set_title("Drive RPM")
    axes[1,0].grid(alpha=0.3)
    axes[1,1].plot(df["time"], df["soc_pct"], color="orange");axes[1,1].set_title("Battery SoC (%)")
    axes[1,1].set_ylim(0, 100); axes[1,1].grid(alpha=0.3)
    for ax in axes.flat: ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    st.pyplot(fig); plt.close(fig)

    # Inject fault button
    if st.button("🔥 Inject simulated belt fire (demo)"):
        idx = df.index[-1]
        df.loc[idx, "temp_C"] = 85.0
        df.loc[idx, "vib_g"] = 1.4
        st.session_state.telemetry_data = df
        st.error("🚨 ALARM: Belt temp > 70 °C and vibration > 1 g — fire suspected. SMS dispatched.")


# =====================================================================
# 4. SIMULATIONS — interactive
# =====================================================================
def render_simulations():
    st.markdown("## 🔬 Simulations — interactive plots")
    st.caption("Re-rendered live with sliders — same maths as the PNGs in `simulations/output/`.")

    sim = st.selectbox("Pick a simulation", [
        "Power budget (battery over 7 days)",
        "Solar harvest (panel over 1 week)",
        "LoRa link budget (RSSI vs distance)",
        "Vibration FFT (3×RPM fault peak)",
        "Belt thermal / fire",
        "Strain-gauge calibration",
    ])

    if "Power budget" in sim:
        st.markdown("### 🔋 12 V 20 Ah LiFePO4 battery — autonomy calculator")
        c1, c2 = st.columns(2)
        load_w   = c1.slider("Continuous load (W)", 0.1, 3.0, 0.3, 0.05)
        days     = c2.slider("Days to simulate", 1, 30, 7)
        e = 205; t = np.arange(0, days*24 + 1)
        soc = np.array([max(0, (e := e - load_w)) for _ in t]) / 205
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(t/24, soc*100, lw=2, color="orange")
        ax.axhline(20, color="red", ls="--", label="BMS cutoff")
        ax.set_xlabel("Days"); ax.set_ylabel("SoC (%)"); ax.grid(alpha=0.3)
        ax.legend(); ax.set_title(f"{load_w:.1f} W → {days/load_w*205/24:.1f} days to 20% SoC")
        st.pyplot(fig); plt.close(fig)

    elif "Solar harvest" in sim:
        st.markdown("### ☀ Solar panel — harvest vs weather")
        c1, c2 = st.columns(2)
        panel_w   = c1.slider("Panel size (W)", 5, 50, 20)
        weather   = c2.slider("Sun-hours equivalent (h/day)", 1.0, 6.0, 4.5)
        load_wh_d = st.slider("Daily load (Wh/day)", 5, 50, 10)
        harvest = panel_w * weather * 0.75  # 75 % system efficiency
        net = harvest - load_wh_d
        fig, ax = plt.subplots(figsize=(10, 4))
        bars = ["Daily harvest", "Daily load", "Net"]
        ax.bar(bars, [harvest, load_wh_d, net], color=["green", "orange", "navy"])
        ax.axhline(0, color="k", lw=0.5)
        for i, v in enumerate([harvest, load_wh_d, net]):
            ax.text(i, v + (1 if v>=0 else -3), f"{v:.1f} Wh", ha="center", fontweight="bold")
        ax.set_ylabel("Wh/day"); ax.set_title(f"Panel {panel_w} W, {weather} h/day, load {load_wh_d} Wh/day")
        st.pyplot(fig); plt.close(fig)
        st.info(f"Net: **{net:+.1f} Wh/day** — battery {'gains' if net>0 else 'loses'} "
                f"{abs(net)/12/20*24*100/205:.1f}% SoC per day.")

    elif "LoRa link budget" in sim:
        st.markdown("### 📶 LoRa 868 MHz RSSI vs distance")
        c1, c2 = st.columns(2)
        tx_dbm  = c1.slider("TX power (dBm)", 2, 20, 14)
        rock_l  = c2.slider("Rock-wall penalty (dB)", 0, 30, 12)
        d = np.linspace(0.1, 10, 500)
        fspl = 32.45 + 20*np.log10(d) + 20*np.log10(868)
        rssi = tx_dbm + 3 + 3 - 1.5 - fspl - rock_l
        sens = -137
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(d, rssi, lw=2, color="blue")
        ax.axhline(sens, color="k", ls="--", label=f"Sensitivity {sens} dBm")
        cross = d[np.where(rssi < sens)[0][0]] if (rssi < sens).any() else 10
        ax.axvline(cross, color="red", ls=":", label=f"Max range ≈ {cross:.1f} km")
        ax.fill_between(d, rssi, -160, where=(rssi > sens), color="green", alpha=0.15)
        ax.fill_between(d, rssi, -160, where=(rssi < sens), color="red", alpha=0.15)
        ax.set_xlabel("Distance (km)"); ax.set_ylabel("RSSI (dBm)")
        ax.set_ylim(-160, -60); ax.legend(); ax.grid(alpha=0.3)
        st.pyplot(fig); plt.close(fig)

    elif "Vibration FFT" in sim:
        st.markdown("### 🛎 ADXL345 vibration — 3× RPM fault peak")
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
        axes[0].plot(t, healthy, label="healthy"); axes[0].plot(t, failing, label="failing")
        axes[0].set_title("Time domain"); axes[0].legend(); axes[0].grid(alpha=0.3)
        axes[1].plot(f1, m1, label="healthy"); axes[1].plot(f1, m2, label="failing")
        axes[1].axvline(rpm3, color="red", ls="--", label=f"3×RPM = {rpm3:.1f} Hz")
        axes[1].set_xlim(0, 100); axes[1].set_title("FFT — fault peak at 3× RPM")
        axes[1].legend(); axes[1].grid(alpha=0.3)
        st.pyplot(fig); plt.close(fig)

    elif "Belt thermal" in sim:
        st.markdown("### 🔥 Belt fire — DS18B20 response")
        fire_w = st.slider("Fire heat flux (kW/m²)", 10, 100, 60)
        t = np.linspace(0, 600, 601)
        # Simplified
        T_amb = 35; flux = np.where(t<120, 0, np.minimum(fire_w*1000, fire_w*1000*np.minimum(1,(t-120)/120)))
        dT = (flux/18000 - 25*(np.zeros_like(t))) * 1  # very rough
        T = T_amb + np.cumsum(dT)/60
        T = np.minimum(T, 950)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(t/60, T, color="red", lw=2)
        ax.axhline(70, color="k", ls="--", label="Alarm threshold 70 °C")
        alarm = t[np.argmax(T > 70)] if (T > 70).any() else None
        if alarm: ax.annotate(f"ALARM @ {alarm/60:.1f} min", xy=(alarm/60, 70),
                             xytext=(alarm/60 + 0.5, 200),
                             arrowprops=dict(arrowstyle="->", color="red"))
        ax.set_xlabel("Time (min)"); ax.set_ylabel("Belt surface T (°C)"); ax.legend(); ax.grid(alpha=0.3)
        st.pyplot(fig); plt.close(fig)

    elif "Strain-gauge" in sim:
        st.markdown("### 🪢 HX711 + BF350 strain gauge — calibration")
        tension_n = st.slider("Belt tension (N)", 0, 10000, 5000)
        code = tension_n * 2097.152
        nf = 21.0
        fig, ax = plt.subplots(figsize=(10, 4))
        tens = np.linspace(0, 10000, 500)
        codes = tens * 2097.152
        ax.plot(tens, codes, lw=2)
        ax.scatter([tension_n], [code], color="red", s=100, zorder=5, label=f"You: {code:,.0f} counts")
        ax.axhline(nf, color="red", ls="--", alpha=0.5, label=f"Noise floor ±{nf:.0f}")
        ax.axhline(-nf, color="red", ls="--", alpha=0.5)
        ax.set_xlabel("Belt tension (N)"); ax.set_ylabel("HX711 ADC code")
        ax.set_title(f"{code:,.0f} counts = {tension_n} N")
        ax.legend(); ax.grid(alpha=0.3)
        st.pyplot(fig); plt.close(fig)


# =====================================================================
# 5. POWER SYSTEM
# =====================================================================
def render_power():
    st.markdown("## ☀ Power System")
    st.caption("Solar pod = panel + MPPT + LiFePO4 + buck converters.")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("### Solar panel")
    st.markdown("""
    | Item | Spec |
    |---|---|
    | Panel | 20 W mono (Voc 22 V, Isc 1.2 A) |
    | Controller | EPever Tracer 1210 AN, 10 A MPPT |
    | Battery | 12 V 20 Ah LiFePO4 (256 Wh, 80 % DoD = 205 Wh) |
    | Buck 5 V | LM2596-ADJ (3 A) |
    | LDO 3.3 V | AMS1117-3.3 |
    """)
    st.markdown("---")
    st.markdown("### Energy budget")
    data = {
        "Mode":   ["Sleep", "Active", "Alarm", "Continuous transmit"],
        "mA":     [3,       80,       200,     500],
        "Hours/day": [20,    3,        0.5,     0.5],
    }
    df = pd.DataFrame(data)
    df["mAh/day"] = df["mA"] * df["Hours/day"]
    df["Wh/day"]  = df["mAh/day"] * 3.3 / 1000 * 1.3   # assume 3.3 V then DC-DC losses
    st.dataframe(df, use_container_width=True)
    total_wh = df["Wh/day"].sum()
    st.metric("Total energy", f"{total_wh:.1f} Wh/day",
              delta=f"{20*4*0.75 - total_wh:+.1f} Wh/day solar surplus")


# =====================================================================
# 6. LoRa LINK
# =====================================================================
def render_lora():
    st.markdown("## 📶 LoRa Link")
    st.markdown("""
    - **Modem**: Semtech SX1278 (RA-02 module)
    - **Band**: 868 MHz (India / EU)
    - **Spreading factor**: SF12, BW 125 kHz, CR 4/5 → sensitivity **-137 dBm**
    - **TX power**: +14 dBm
    - **Antenna**: 3 dBi omni fiberglass, vertical
    - **Range**: 2–5 km line-of-sight, ~500 m through 1 rock wall
    - **Fallback**: SIM800L GSM module (SMS only, 1 message / hour)
    """)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/LoRa_logo.svg/512px-LoRa_logo.svg.png",
             caption="LoRaWAN is the open standard we use on top of SX1278.",
             width=200)


# =====================================================================
# 7. BOM
# =====================================================================
def render_bom():
    st.markdown("## 💰 Bill of Materials")
    bom = [
        ("ESP32-WROOM-32",                "Main controller",          1, 350),
        ("SX1278 (RA-02) LoRa module",    "868 MHz radio",            1, 450),
        ("SIM800L GSM module",            "SMS fallback",             1, 650),
        ("ADXL345 IMU",                   "Vibration",                1, 220),
        ("HX711 + BF350-3AA strain gauge","Belt tension",             1, 380),
        ("DS18B20 temp probe",            "Belt surface temp",        2, 110),
        ("NTC 10 kΩ thermistor",          "Ambient + secondary temp", 2,  35),
        ("Hall-effect pickup (A3144)",    "RPM",                      1,  80),
        ("E18-IR80NK IR proximity",       "Tear detect",              2, 180),
        ("ACS712-20A current sensor",     "Drive motor current",      1, 220),
        ("GP2Y1010 dust sensor",          "PM2.5",                    1, 380),
        ("MQ-2 gas sensor",               "Smoke / LPG",              1, 180),
        ("MQ-135 gas sensor",             "CO/CH₄/NH₃",               1, 220),
        ("OLED 0.96\" I²C",               "Local display",            1, 180),
        ("Buzzer 5 V active",             "Local alarm",              1,  40),
        ("LM2596-ADJ buck",               "12 → 5 V",                 1,  90),
        ("AMS1117-3.3 LDO",               "5 → 3.3 V",                1,  20),
        ("20 W solar panel",              "Power",                    1, 1400),
        ("EPever Tracer 1210AN MPPT",     "Charge controller",        1, 1800),
        ("12 V 20 Ah LiFePO4 battery",    "Storage",                  1, 6800),
        ("Die-cast aluminium box 240×160", "Enclosure IP67",          1, 1500),
        ("M10 U-bolts, cable glands",     "Mounting hardware",        1,  600),
    ]
    df = pd.DataFrame(bom, columns=["Component", "Function", "Qty", "INR"])
    df["Total"] = df["INR"] * df["Qty"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    total = df["Total"].sum()
    st.metric("Total per belt pod", f"₹ {total:,}",  f"≈ USD {total/83:.0f}")


# =====================================================================
# 8. INSTALLATION
# =====================================================================
def render_install():
    st.markdown("## 🛠 Installation walkthrough")
    steps = [
        ("1️⃣ Mount the bracket", "Weld the M10 U-bolt bracket to the take-up frame, 30 cm from the head pulley."),
        ("2️⃣ Bolt the pod",       "Bolt the IP67 box to the bracket. Torque to 35 Nm."),
        ("3️⃣ Wire sensors",       "Land the DS18B20, ADXL345, strain-gauge, Hall, E18-IR, ACS712, MQ-2, MQ-135, GP2Y wires on the carrier PCB."),
        ("4️⃣ Solar pod",          "Mount the solar panel on the belt-stringer pole, true south, 30° tilt. Run 12 V cable ≤30 m."),
        ("5️⃣ Power on",           'Press the BOOT button — OLED shows firmware version, then READY.'),
        ("6️⃣ Pair with gateway",  "Hold PAIR on the cabin gateway for 5 s; LED blinks green when the pod joins."),
        ("7️⃣ Commissioning",      "Run belt empty for 5 min; verify vibration FFT shows clean 1× RPM peak; tension baseline stored."),
        ("8️⃣ Lock & tag",         "Close the box, torque the lid screws to 4 Nm, attach tamper seal."),
    ]
    for emoji, title, body in steps:
        with st.expander(f"{emoji}  {title}"):
            st.markdown(body)


# =====================================================================
# ROUTING
# =====================================================================
if section.startswith("🏠"):
    # Hero
    st.markdown('<p class="big-title">BeltGuard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">A solar-powered sensor pod that watches every metre of every belt, 24×7.</p>',
                unsafe_allow_html=True)
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown('<div class="metric-card"><b>Belt fires</b><br><span class="crit">detected in <90 s</span></div>', unsafe_allow_html=True)
    c2.markdown('<div class="metric-card"><b>Belt tears</b><br><span class="crit">detected in <2 s</span></div>', unsafe_allow_html=True)
    c3.markdown('<div class="metric-card"><b>LoRa range</b><br><span class="ok">2–5 km LoS</span></div>', unsafe_allow_html=True)
    c4.markdown('<div class="metric-card"><b>Solar autonomy</b><br><span class="ok">41 days</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    render_architecture()

elif section.startswith("🏗"):
    render_architecture()
elif section.startswith("🎛"):
    render_sensor_pod()
elif section.startswith("📡"):
    render_live_telemetry()
elif section.startswith("🔬"):
    render_simulations()
elif section.startswith("☀"):
    render_power()
elif section.startswith("📶"):
    render_lora()
elif section.startswith("💰"):
    render_bom()
elif section.startswith("🛠"):
    render_install()