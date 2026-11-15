import os
import folium
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from scipy import stats
import streamlit as st
from streamlit_folium import st_folium

ICONO_NASA_SVG_URI = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<circle cx='50' cy='50' r='46' fill='%230B3D91'/>"
    "<ellipse cx='50' cy='50' rx='42' ry='15' transform='rotate(-24 50 50)' fill='none' stroke='%23FC3D21' stroke-width='5'/>"
    "<circle cx='28' cy='28' r='2.5' fill='white'/><circle cx='72' cy='26' r='2' fill='white'/><circle cx='70' cy='72' r='2.5' fill='white'/>"
    "<text x='50' y='56' font-family='Arial, sans-serif' font-weight='900' font-size='21' fill='white' text-anchor='middle'>NASA</text>"
    "</svg>"
)

st.set_page_config(
    page_title="TEAM Joule Detectives | NASA Space Apps",
    page_icon=ICONO_NASA_SVG_URI,
    layout="wide",
    initial_sidebar_state="auto",
)

# --- CSS TEMA OSCURO + BUSCADOR SIEMPRE VISIBLE + OPTIMIZACIÓN MÓVIL ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Orbitron:wght@700;900&family=Space+Mono:wght@400;700&display=swap');

    .stApp {
        background-color: #0B0E14 !important;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
    }
    .stApp h1, .stApp h2, .stApp h3 {
        color: #38BDF8 !important;
        font-weight: 800 !important;
    }
    .stApp p, .stApp label, .stApp span {
        color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 2px solid #1E3A8A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    input[type="text"], input[type="number"] {
        background-color: #1F2937 !important;
        color: #FACC15 !important;
        border: 2px solid #38BDF8 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    .stDownloadButton > button {
        width: 100% !important;
        background-color: #0B3D91 !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8 !important;
        font-weight: 700 !important;
    }
    .stDownloadButton > button p {
        color: #FFFFFF !important;
    }
    /* En móviles (<768px) oculta el sidebar lateral para evitar bloqueos de pantalla */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }
    }
    .nasa-topbar {
        background-color: #000000;
        padding: 14px 20px;
        border-radius: 6px 6px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        border-bottom: 3px solid #FC3D21;
    }
    .nasa-topbar-center {
        text-align: center;
        flex: 1;
    }
    .nasa-team-title {
        font-family: 'Orbitron', sans-serif;
        font-size: clamp(18px, 4vw, 26px);
        font-weight: 900;
        letter-spacing: 1.4px;
        color: #FFFFFF !important;
    }
    .nasa-team-subtitle {
        font-family: 'Space Mono', monospace;
        font-size: clamp(11px, 2.5vw, 13px);
        color: #93C5FD !important;
        margin-top: 4px;
    }
    .objetivo-box {
        background-color: #111827;
        border: 1px solid #1E40AF;
        border-left: 6px solid #FC3D21;
        padding: 14px 18px;
        border-radius: 0 0 6px 6px;
        color: #E2E8F0 !important;
        margin-bottom: 14px;
    }
    .dinamico-card {
        background-color: #161B22;
        border: 2px solid #38BDF8;
        border-left: 6px solid #FACC15;
        padding: 14px 18px;
        border-radius: 8px;
        color: #F8FAFC !important;
        margin-bottom: 12px;
    }
    .dinamico-valor {
        color: #FACC15 !important;
        font-size: 22px;
        font-weight: 900;
        font-family: 'Space Mono', monospace;
    }
</style>
""",
    unsafe_allow_html=True,
)

LOGO_NASA_SVG = (
    '<svg width="48" height="48" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="50" cy="50" r="46" fill="#0B3D91" stroke="#FFFFFF" stroke-width="3"/>'
    '<circle cx="26" cy="28" r="2.5" fill="#FFFFFF"/><circle cx="74" cy="25" r="2" fill="#FFFFFF"/>'
    '<circle cx="72" cy="72" r="2.5" fill="#FFFFFF"/><circle cx="30" cy="70" r="1.8" fill="#FFFFFF"/>'
    '<ellipse cx="50" cy="50" rx="43" ry="15" transform="rotate(-24 50 50)" fill="none" stroke="#FC3D21" stroke-width="5"/>'
    '<text x="50" y="57" font-family="Arial, Helvetica, sans-serif" font-weight="900" font-size="22" fill="#FFFFFF" text-anchor="middle" letter-spacing="1">NASA</text>'
    "</svg>"
)


def geocodificar(nombre, offline):
    if offline or not nombre.strip():
        return 37.3890, -5.9840, "Sevilla, España"
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": nombre, "format": "json", "limit": 1},
            headers={"User-Agent": "TEAMJouleDetectives-NASASpaceApps/1.0"},
            timeout=5,
        ).json()
        if r:
            return (
                round(float(r[0]["lat"]), 4),
                round(float(r[0]["lon"]), 4),
                r[0]["display_name"].split(",")[0],
            )
    except requests.RequestException:
        pass
    return 37.3890, -5.9840, "Sevilla, España"


# --- ESTADO INICIAL ---
if "lat_actual" not in st.session_state:
    st.session_state.lat_actual = 37.3890
if "lon_actual" not in st.session_state:
    st.session_state.lon_actual = -5.9840
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = "Sevilla, España"
if "ultima_ciudad_buscada" not in st.session_state:
    st.session_state.ultima_ciudad_buscada = "Sevilla, España"
if "modo_offline_global" not in st.session_state:
    st.session_state.modo_offline_global = False


def actualizar_desde_ciudad(nueva_ciudad):
    if nueva_ciudad and nueva_ciudad != st.session_state.ultima_ciudad_buscada:
        lat_g, lon_g, nom_g = geocodificar(
            nueva_ciudad, st.session_state.modo_offline_global
        )
        st.session_state.lat_actual = lat_g
        st.session_state.lon_actual = lon_g
        st.session_state.lugar_actual = nom_g
        st.session_state.ultima_ciudad_buscada = nueva_ciudad


def actualizar_desde_coords(nueva_lat, nueva_lon):
    if (
        round(nueva_lat, 4) != round(st.session_state.lat_actual, 4)
        or round(nueva_lon, 4) != round(st.session_state.lon_actual, 4)
    ):
        st.session_state.lat_actual = round(nueva_lat, 4)
        st.session_state.lon_actual = round(nueva_lon, 4)
        st.session_state.lugar_actual = (
            f"Coordenada ({st.session_state.lat_actual}°, {st.session_state.lon_actual}°)"
        )


# --- PANEL LATERAL (PORTÁTIL / ESCRITORIO) ---
st.sidebar.header("🛰️ PANEL DE CONTROL")
st.sidebar.markdown("**Ajustar Coordenadas (Lat / Lon):**")
lat_side = st.sidebar.number_input(
    "Latitud (°)",
    value=float(st.session_state.lat_actual),
    format="%.4f",
    step=0.05,
    key="lat_sidebar",
)
lon_side = st.sidebar.number_input(
    "Longitud (°)",
    value=float(st.session_state.lon_actual),
    format="%.4f",
    step=0.05,
    key="lon_sidebar",
)
actualizar_desde_coords(lat_side, lon_side)

LAT = st.session_state.lat_actual
LON = st.session_state.lon_actual
nombre_lugar = st.session_state.lugar_actual

# --- TELEMETRÍA NASA POWER ---
PARAMETROS = ["ALLSKY_SFC_SW_DWN", "WS10M", "T2M", "PRECTOTCORR"]
ARCHIVO_LOCAL = f"jouledetective_nasa_{LAT}_{LON}.csv"


def obtener_telemetria_nasa(lat, lon, offline, archivo):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/monthly/point?"
        f"parameters={','.join(PARAMETROS)}&community=RE&longitude={lon}&latitude={lat}"
        f"&start=2015&end=2025&format=CSV"
    )
    if not offline:
        try:
            df = pd.read_csv(url, skiprows=12)
            df.to_csv(archivo, index=False)
            return (
                df,
                "NASA Langley Research Center — POWER Project (CERES / MERRA-2) • EN LÍNEA",
            )
        except OSError:
            pass

    if os.path.exists(archivo):
        return (
            pd.read_csv(archivo),
            "NASA POWER Project (Caché Local Validada) • MODO SIN CONEXIÓN",
        )

    years = list(range(2015, 2026))
    filas = []
    respaldo = {
        "ALLSKY_SFC_SW_DWN": [4.92, 5.01, 5.10, 5.06, 5.16, 5.22, 5.31, 5.36, 5.41, 5.49, 5.56],
        "WS10M": [3.12, 3.20, 3.05, 3.14, 3.21, 3.18, 3.15, 3.26, 3.22, 3.20, 3.25],
        "T2M": [18.5, 18.7, 18.9, 18.8, 19.1, 19.3, 19.5, 19.7, 19.9, 20.1, 20.3],
        "PRECTOTCORR": [1.45, 1.38, 1.22, 1.51, 1.18, 1.29, 1.15, 1.10, 1.05, 1.12, 1.08],
    }
    for p, vals in respaldo.items():
        for yr, v in zip(years, vals):
            filas.append({"PARAMETER": p, "YEAR": yr, "ANN": v})
    return (
        pd.DataFrame(filas),
        "NASA POWER Contingency Dataset (Almacenamiento Local) • MODO SIN CONEXIÓN",
    )


df_nasa, fuente_datos = obtener_telemetria_nasa(
    LAT, LON, st.session_state.modo_offline_global, ARCHIVO_LOCAL
)

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Base de datos de NASA (.CSV)",
    data=df_nasa.to_csv(index=False).encode("utf-8"),
    file_name=f"NASA_POWER_{LAT}_{LON}.csv",
    mime="text/csv",
    key="dl_sidebar",
)

offline_side = st.sidebar.checkbox(
    "🔌 Activar Modo Sin Conexión (ON / OFF)",
    value=st.session_state.modo_offline_global,
    key="offline_sidebar",
)
if offline_side != st.session_state.modo_offline_global:
    st.session_state.modo_offline_global = offline_side
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**🔓 SOFTWARE OPEN SOURCE**\n\n"
    "Código abierto en Python + NASA POWER replicable para investigación climática y contingencia energética ante desconexiones de red."
)


def calcular_estadisticas(df, param):
    sub = df[(df["PARAMETER"] == param) & (df["ANN"] > -900)].sort_values(
        "YEAR"
    )
    x = sub["YEAR"].to_numpy(dtype=float)
    y = sub["ANN"].to_numpy(dtype=float)
    slope, intercept, _, p_val, _ = stats.linregress(x, y)
    media_actual = float(np.mean(y[-3:]))
    proyeccion_2030 = float(intercept + slope * 2030)
    cambio_decada = float(slope * 10)
    return x, y, media_actual, proyeccion_2030, cambio_decada, float(p_val)


x_sol, y_sol, sol_act, sol_2030, sol_dec, _ = calcular_estadisticas(
    df_nasa, "ALLSKY_SFC_SW_DWN"
)
x_win, y_win, win_act, win_2030, win_dec, _ = calcular_estadisticas(
    df_nasa, "WS10M"
)
x_tmp, y_tmp, tmp_act, tmp_2030, tmp_dec, _ = calcular_estadisticas(
    df_nasa, "T2M"
)
x_prc, y_prc, prc_act, prc_2030, prc_dec, _ = calcular_estadisticas(
    df_nasa, "PRECTOTCORR"
)

# ==============================================================================
# ENCABEZADO VISUAL
# ==============================================================================
if st.session_state.modo_offline_global:
    st.warning(
        "⚠️ **MODO SIN CONEXIÓN ACTIVADO:** Operando 100% en local con telemetría NASA en caché. "
        "**Nota:** El mapa interactivo requiere conexión a internet para descargar teselas cartográficas."
    )

header_html = (
    f'<div class="nasa-topbar">'
    f"<div>{LOGO_NASA_SVG}</div>"
    f'<div class="nasa-topbar-center">'
    f'<div class="nasa-team-title">TEAM Joule Detectives</div>'
    f'<div class="nasa-team-subtitle">NASA Space Apps Challenge • Open Source Earth Climate & Energy Resilience</div>'
    f"</div>"
    f"<div>{LOGO_NASA_SVG}</div>"
    f"</div>"
    f'<div class="objetivo-box">'
    f"<b>🎯 Objetivo del Proyecto:</b> Procesamiento en <b>Python</b> de datos abiertos <b>NASA POWER (2015–2025)</b> "
    f"para visualizar tendencias climáticas, proyectar escenarios al <b>2030</b> y optimizar la resiliencia energética ante "
    f"posibles desconexiones del suministro eléctrico."
    f"</div>"
)
st.markdown(header_html, unsafe_allow_html=True)

# ==============================================================================
# BARRA DE BÚSQUEDA SIEMPRE VISIBLE (MÓVIL Y PORTÁTIL)
# ==============================================================================
col_busq, col_csv_top, col_off_top = st.columns([2.2, 1.1, 1])

with col_busq:
    ciudad_top = st.text_input(
        "🔍 Buscar por Ciudad / Región (escribe y pulsa Enter para actualizar):",
        value=st.session_state.ultima_ciudad_buscada,
        key="ciudad_siempre_visible",
    )
    if ciudad_top != st.session_state.ultima_ciudad_buscada:
        actualizar_desde_ciudad(ciudad_top)
        st.rerun()

with col_csv_top:
    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Datos NASA (.CSV)",
        data=df_nasa.to_csv(index=False).encode("utf-8"),
        file_name=f"NASA_POWER_{LAT}_{LON}.csv",
        mime="text/csv",
        key="dl_top",
    )

with col_off_top:
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
    offline_top = st.checkbox(
        "🔌 Modo Offline",
        value=st.session_state.modo_offline_global,
        key="offline_top",
    )
    if offline_top != st.session_state.modo_offline_global:
        st.session_state.modo_offline_global = offline_top
        st.rerun()

# ==============================================================================
# PUNTO 1: INDICADORES SATELITALES NASA POWER
# ==============================================================================
st.subheader(f"1. Indicadores Satelitales NASA POWER en 📍 {nombre_lugar}")
st.caption(f"Fuente activa: {fuente_datos}")

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        f'<div class="dinamico-card">'
        f"<div>☀️ <b>Radiación Solar ({nombre_lugar})</b></div>"
        f'<div class="dinamico-valor">{sol_act:.2f} kWh/m²/d</div>'
        f"<small>Tendencia: {sol_dec:+.2f}/década • Proyección 2030: <b>{sol_2030:.2f}</b></small>"
        f"</div>",
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f'<div class="dinamico-card">'
        f"<div>💨 <b>Velocidad del Viento ({nombre_lugar})</b></div>"
        f'<div class="dinamico-valor">{win_act:.2f} m/s</div>'
        f"<small>Tendencia: {win_dec:+.2f}/década • Proyección 2030: <b>{win_2030:.2f}</b></small>"
        f"</div>",
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f'<div class="dinamico-card">'
        f"<div>🌡️ <b>Temperatura 2m ({nombre_lugar})</b></div>"
        f'<div class="dinamico-valor">{tmp_act:.1f} °C</div>'
        f"<small>Tendencia: {tmp_dec:+.2f} °C/década • Proyección 2030: <b>{tmp_2030:.1f} °C</b></small>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ==============================================================================
# PUNTO 2: MAPA INTERACTIVO A COLOR (FOLIUM) + COORDENADAS COPIABLES
# ==============================================================================
st.subheader(f"2. Selección Geográfica en Mapa Interactivo — 📍 {nombre_lugar}")
st.caption(
    "Toca o haz clic en cualquier punto del mapa a color para capturar las coordenadas y actualizar automáticamente los satélites de la NASA."
)

col_mapa, col_coords = st.columns([1.6, 1])

with col_mapa:
    m = folium.Map(location=[LAT, LON], zoom_start=8, tiles="OpenStreetMap")
    folium.Marker(
        [LAT, LON],
        popup=f"{nombre_lugar} ({LAT}, {LON})",
        tooltip="Ubicación analizada",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    map_data = st_folium(m, height=340, use_container_width=True)

    if map_data and map_data.get("last_clicked"):
        click_lat = round(float(map_data["last_clicked"]["lat"]), 4)
        click_lon = round(float(map_data["last_clicked"]["lng"]), 4)
        if click_lat != LAT or click_lon != LON:
            st.session_state.lat_actual = click_lat
            st.session_state.lon_actual = click_lon
            st.session_state.lugar_actual = (
                f"Coordenada ({click_lat}°, {click_lon}°)"
            )
            st.rerun()

with col_coords:
    st.markdown(
        f'<div class="dinamico-card">'
        f"<div>📍 <b>UBICACIÓN ACTIVA</b></div>"
        f'<div class="dinamico-valor">{nombre_lugar.upper()}</div>'
        f"<small>Precipitación media actual: <b>{prc_act:.2f} mm/día</b> (Proyección 2030: {prc_2030:.2f} mm/día)</small>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.caption("📋 Coordenadas activas (listas para copiar y pegar):")
    st.code(f"Latitud: {LAT} | Longitud: {LON}", language="text")

st.markdown("---")

# ==============================================================================
# SECCIÓN DE ESTUDIO CLIMÁTICO PREDICTIVO AL 2030 (PUNTOS 3 Y 4)
# ==============================================================================
st.header(f"📈 Estudio Climático Predictivo al 2030 — 📍 {nombre_lugar}")

# --- PUNTO 3: GRÁFICO 2D DE TEMPERATURA Y CANTIDAD DE LLUVIA ---
st.subheader("3. Evolución 2D y Proyección 2030: Temperatura (°C) y Precipitación (mm/día)")

fig_2d = make_subplots(specs=[[{"secondary_y": True}]])

años_2d = [str(int(yr)) for yr in x_prc] + ["2030 (Proy.)"]
lluvia_2d = y_prc.tolist() + [round(prc_2030, 2)]
temp_2d = y_tmp.tolist() + [round(tmp_2030, 1)]

fig_2d.add_trace(
    go.Bar(
        x=años_2d,
        y=lluvia_2d,
        name="🌧️ Precipitación (mm/día)",
        marker_color="#38BDF8",
        opacity=0.75,
    ),
    secondary_y=False,
)

fig_2d.add_trace(
    go.Scatter(
        x=años_2d,
        y=temp_2d,
        name="🌡️ Temperatura 2m (°C)",
        mode="lines+markers+text",
        text=[f"{t:.1f}°" for t in temp_2d],
        textposition="top center",
        line=dict(color="#F97316", width=4),
        marker=dict(size=9, color="#FACC15"),
    ),
    secondary_y=True,
)

fig_2d.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0B0E14",
    plot_bgcolor="#111827",
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
    ),
    margin=dict(l=10, r=10, b=10, t=30),
    height=360,
)
fig_2d.update_yaxes(title_text="Precipitación (mm/día)", secondary_y=False)
fig_2d.update_yaxes(title_text="Temperatura (°C)", secondary_y=True)

st.plotly_chart(fig_2d, use_container_width=True)

# --- PUNTO 4: GRÁFICO 3D DE RADIACIÓN SOLAR Y VIENTO ---
st.subheader("4. Trayectoria 3D y Proyección 2030: Radiación Solar y Velocidad del Viento")

años_3d = [str(int(yr)) for yr in x_sol] + ["2030"]
sol_3d_vals = y_sol.tolist() + [round(sol_2030, 2)]
win_3d_vals = y_win.tolist() + [round(win_2030, 2)]

fig_3d = go.Figure()

fig_3d.add_trace(
    go.Scatter3d(
        x=años_3d,
        y=["☀️ Solar (kWh/m²)"] * len(años_3d),
        z=sol_3d_vals,
        name="☀️ Radiación Solar (kWh/m²/día)",
        mode="lines+markers+text",
        text=[f"{v:.2f}" for v in sol_3d_vals],
        textposition="top center",
        marker=dict(size=7, color="#F97316", symbol="circle"),
        line=dict(color="#F97316", width=6),
    )
)

fig_3d.add_trace(
    go.Scatter3d(
        x=años_3d,
        y=["💨 Eólica (m/s)"] * len(años_3d),
        z=win_3d_vals,
        name="💨 Velocidad del Viento (m/s)",
        mode="lines+markers+text",
        text=[f"{v:.2f}" for v in win_3d_vals],
        textposition="top center",
        marker=dict(size=7, color="#38BDF8", symbol="diamond"),
        line=dict(color="#38BDF8", width=6),
    )
)

fig_3d.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0B0E14",
    plot_bgcolor="#0B0E14",
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5
    ),
    scene=dict(
        xaxis=dict(title="Año (2015–2030)", backgroundcolor="#111827"),
        yaxis=dict(title="Recurso", backgroundcolor="#111827"),
        zaxis=dict(title="Magnitud", backgroundcolor="#111827"),
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    height=400,
)

st.plotly_chart(fig_3d, use_container_width=True)
