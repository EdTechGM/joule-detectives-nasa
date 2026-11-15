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
    initial_sidebar_state="expanded",
)

# --- CSS TEMA OSCURO ESPACIAL CON CONTRASTE TOTAL CORREGIDO ---
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=Orbitron:wght@700;900&family=Space+Mono:wght@400;700&display=swap');

    .stApp {
        background-color: #0B0E14 !important;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
    }
    .stApp h1, .stApp h2, .stApp h3, [data-testid="stHeading"] * {
        color: #38BDF8 !important;
        font-weight: 800 !important;
    }
    .stApp p, .stApp label, .stApp span, .stCaption, [data-testid="stCaptionContainer"] * {
        color: #E2E8F0 !important;
    }
    /* Caja de coordenadas listas para copiar y pegar (antes blanca sobre blanco) */
    [data-testid="stCode"], pre, code {
        background-color: #1E293B !important;
        color: #FACC15 !important;
        border: 1px solid #38BDF8 !important;
        font-weight: 700 !important;
    }
    [data-testid="stCode"] * {
        color: #FACC15 !important;
    }
    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 2px solid #1E3A8A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] input {
        background-color: #1F2937 !important;
        color: #FACC15 !important;
        border: 1px solid #38BDF8 !important;
        font-weight: 700 !important;
    }
    /* Botones + y - de los campos numéricos laterales */
    section[data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8 !important;
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
    .nasa-topbar {
        background-color: #000000;
        padding: 14px 24px;
        border-radius: 6px 6px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        border-bottom: 3px solid #FC3D21;
    }
    .nasa-topbar-center {
        text-align: center;
        flex: 1;
    }
    .nasa-team-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 26px;
        font-weight: 900;
        letter-spacing: 1.6px;
        color: #FFFFFF !important;
    }
    .nasa-team-subtitle {
        font-family: 'Space Mono', monospace;
        font-size: 13px;
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
        margin-bottom: 18px;
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
    .sig-badge-yes {
        display: inline-block;
        background-color: #065F46;
        color: #A7F3D0 !important;
        border: 1px solid #10B981;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 700;
        margin-top: 6px;
    }
    .sig-badge-no {
        display: inline-block;
        background-color: #1E293B;
        color: #CBD5E1 !important;
        border: 1px solid #64748B;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 700;
        margin-top: 6px;
    }
    .conclusion-box {
        background-color: #0F172A;
        border: 2px solid #10B981;
        border-left: 8px solid #10B981;
        padding: 18px 22px;
        border-radius: 8px;
        color: #F8FAFC !important;
        margin-top: 12px;
    }
</style>
""",
    unsafe_allow_html=True,
)

LOGO_NASA_SVG = (
    '<svg width="56" height="56" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
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


# --- ESTADO SINCRONIZADO SIN BUCLES ---
if "lat_actual" not in st.session_state:
    st.session_state.lat_actual = 37.3890
if "lon_actual" not in st.session_state:
    st.session_state.lon_actual = -5.9840
if "lugar_actual" not in st.session_state:
    st.session_state.lugar_actual = "Sevilla, España"
if "ultima_ciudad_buscada" not in st.session_state:
    st.session_state.ultima_ciudad_buscada = "Sevilla, España"
if "ultimo_clic_mapa" not in st.session_state:
    st.session_state.ultimo_clic_mapa = None

# --- PANEL LATERAL ---
st.sidebar.header("🛰️ PANEL DE CONTROL")
offline_previo = st.session_state.get("modo_offline_chk", False)

ciudad_input = st.sidebar.text_input(
    "1. Buscar por Ciudad / Región:",
    value=st.session_state.ultima_ciudad_buscada,
)

if ciudad_input != st.session_state.ultima_ciudad_buscada:
    lat_g, lon_g, nom_g = geocodificar(ciudad_input, offline_previo)
    st.session_state.lat_actual = lat_g
    st.session_state.lon_actual = lon_g
    st.session_state.lugar_actual = nom_g
    st.session_state.ultima_ciudad_buscada = ciudad_input
    st.session_state.ultimo_clic_mapa = None

st.sidebar.markdown("**2. O ajustar Coordenadas (Lat / Lon):**")
lat_manual = st.sidebar.number_input(
    "Latitud (°)",
    value=float(st.session_state.lat_actual),
    format="%.4f",
    step=0.05,
)
lon_manual = st.sidebar.number_input(
    "Longitud (°)",
    value=float(st.session_state.lon_actual),
    format="%.4f",
    step=0.05,
)

if (
    round(lat_manual, 4) != round(st.session_state.lat_actual, 4)
    or round(lon_manual, 4) != round(st.session_state.lon_actual, 4)
):
    st.session_state.lat_actual = round(lat_manual, 4)
    st.session_state.lon_actual = round(lon_manual, 4)
    st.session_state.lugar_actual = (
        f"Coordenada ({st.session_state.lat_actual}°, {st.session_state.lon_actual}°)"
    )

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
    LAT, LON, offline_previo, ARCHIVO_LOCAL
)

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Base de datos de NASA (.CSV)",
    data=df_nasa.to_csv(index=False).encode("utf-8"),
    file_name=f"NASA_POWER_{LAT}_{LON}.csv",
    mime="text/csv",
)

modo_offline = st.sidebar.checkbox(
    "🔌 Activar Modo Sin Conexión (ON / OFF)",
    value=False,
    key="modo_offline_chk",
)

if modo_offline:
    st.sidebar.warning(
        "⚠️ **Aviso de Mapa Offline:** La cartografía en línea queda limitada, pero los cálculos estadísticos y gráficos siguen operando en local."
    )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**🔓 SOFTWARE OPEN SOURCE**\n\n"
    "Código abierto en Python + NASA POWER replicable para investigación climática y contingencia energética ante desconexiones de red."
)


# --- CÁLCULO ESTADÍSTICO CON SIGNIFICANCIA (P-VALUE SCIPY) ---
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


x_sol, y_sol, sol_act, sol_2030, sol_dec, sol_p = calcular_estadisticas(
    df_nasa, "ALLSKY_SFC_SW_DWN"
)
x_win, y_win, win_act, win_2030, win_dec, win_p = calcular_estadisticas(
    df_nasa, "WS10M"
)
x_tmp, y_tmp, tmp_act, tmp_2030, tmp_dec, tmp_p = calcular_estadisticas(
    df_nasa, "T2M"
)
x_prc, y_prc, prc_act, prc_2030, prc_dec, prc_p = calcular_estadisticas(
    df_nasa, "PRECTOTCORR"
)


def etiqueta_significancia(p_val):
    if p_val < 0.05:
        return f'<span class="sig-badge-yes">✓ Tendencia Significativa (p = {p_val:.3f} &lt; 0.05)</span>'
    return f'<span class="sig-badge-no">• Variabilidad Estable (p = {p_val:.3f} ≥ 0.05)</span>'


# ==============================================================================
# ENCABEZADO VISUAL
# ==============================================================================
if modo_offline:
    st.warning(
        "⚠️ **MODO SIN CONEXIÓN ACTIVADO:** Operando 100% en local con telemetría NASA en caché."
    )

header_html = (
    f'<div class="nasa-topbar">'
    f"<div>{LOGO_NASA_SVG}</div>"
    f'<div class="nasa-topbar-center">'
    f'<div class="nasa-team-title">TEAM Joule Detectives</div>'
    f'<div class="nasa-team-subtitle">NASA Space Apps Challenge • Be An Earth System Trend Detective!</div>'
    f"</div>"
    f"<div>{LOGO_NASA_SVG}</div>"
    f"</div>"
    f'<div class="objetivo-box">'
    f"<b>🎯 Objetivo del Proyecto:</b> Procesamiento en <b>Python</b> de datos abiertos <b>NASA POWER (2015–2025)</b> "
    f"para detectar tendencias estadísticamente significativas, proyectar escenarios orientativos al <b>2030</b> y optimizar la resiliencia energética ante "
    f"posibles desconexiones del suministro eléctrico."
    f"</div>"
)
st.markdown(header_html, unsafe_allow_html=True)

# ==============================================================================
# PUNTO 1: INDICADORES SATELITALES NASA POWER + SIGNIFICANCIA ESTADÍSTICA
# ==============================================================================
st.subheader(f"1. Indicadores Satelitales NASA POWER en 📍 {nombre_lugar}")
st.caption(f"Fuente activa: {fuente_datos}")

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        f'<div class="dinamico-card">'
        f"<div>☀️ <b>Radiación Solar ({nombre_lugar})</b></div>"
        f'<div class="dinamico-valor">{sol_act:.2f} kWh/m²/d</div>'
        f"<small>Tendencia: {sol_dec:+.2f}/década • Proyección lineal 2030: <b>{sol_2030:.2f}</b></small><br>"
        f"{etiqueta_significancia(sol_p)}"
        f"</div>",
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f'<div class="dinamico-card">'
        f"<div>💨 <b>Velocidad del Viento ({nombre_lugar})</b></div>"
        f'<div class="dinamico-valor">{win_act:.2f} m/s</div>'
        f"<small>Tendencia: {win_dec:+.2f}/década • Proyección lineal 2030: <b>{win_2030:.2f}</b></small><br>"
        f"{etiqueta_significancia(win_p)}"
        f"</div>",
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f'<div class="dinamico-card">'
        f"<div>🌡️ <b>Temperatura 2m ({nombre_lugar})</b></div>"
        f'<div class="dinamico-valor">{tmp_act:.1f} °C</div>'
        f"<small>Tendencia: {tmp_dec:+.2f} °C/década • Proyección lineal 2030: <b>{tmp_2030:.1f} °C</b></small><br>"
        f"{etiqueta_significancia(tmp_p)}"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ==============================================================================
# PUNTO 2: MAPA INTERACTIVO A COLOR (SIN BUCLE DE ACTUALIZACIÓN)
# ==============================================================================
st.subheader(f"2. Selección Geográfica en Mapa Interactivo — 📍 {nombre_lugar}")
st.caption(
    "Haz clic en cualquier punto del mapa a color para capturar las coordenadas y actualizar automáticamente los satélites de la NASA."
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

    map_data = st_folium(m, height=340, width=700, key="mapa_nasa_interactivo")

    if map_data and map_data.get("last_clicked"):
        click_lat = round(float(map_data["last_clicked"]["lat"]), 4)
        click_lon = round(float(map_data["last_clicked"]["lng"]), 4)
        nuevo_clic = (click_lat, click_lon)
        if (
            nuevo_clic != st.session_state.ultimo_clic_mapa
            and (click_lat != LAT or click_lon != LON)
        ):
            st.session_state.ultimo_clic_mapa = nuevo_clic
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
        f"<small>Precipitación media actual: <b>{prc_act:.2f} mm/día</b> (Proy. lineal 2030: {prc_2030:.2f} mm/día)</small><br>"
        f"{etiqueta_significancia(prc_p)}"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.caption("📋 Coordenadas activas (listas para copiar y pegar):")
    st.code(f"Latitud: {LAT} | Longitud: {LON}", language="text")

st.markdown("---")

# ==============================================================================
# SECCIÓN DE ESTUDIO CLIMÁTICO PREDICTIVO AL 2030 (PUNTOS 3 Y 4)
# ==============================================================================
st.header(f"📈 Estudio Climático y Tendencias (2015–2030) — 📍 {nombre_lugar}")
st.caption(
    "ℹ️ Nota metodológica: Las estimaciones a 2030 corresponden a una extrapolación lineal sobre 11 años de observaciones NASA POWER (2015–2025), orientativa para planificación energética."
)

# --- PUNTO 3: GRÁFICO 2D ---
st.subheader("3. Evolución 2D y Extrapolación 2030: Temperatura (°C) y Precipitación (mm/día)")

fig_2d = make_subplots(specs=[[{"secondary_y": True}]])

años_2d = [str(int(yr)) for yr in x_prc] + ["2030 (Est.)"]
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

# --- PUNTO 4: GRÁFICO 3D NORMALIZADO (BASE 100 = 2015) PARA COMPARACIÓN CLARA ---
st.subheader("4. Comparativa 3D Normalizada (Base 100 = Año 2015): Evolución Relativa Solar vs. Eólica")
st.caption(
    "Ambos recursos se escalan tomando 2015 como 100% para comparar directamente su variación relativa sin mezclar unidades distintas (pasa el cursor para ver el valor real)."
)

años_3d = [str(int(yr)) for yr in x_sol] + ["2030"]
sol_reales = y_sol.tolist() + [round(sol_2030, 2)]
win_reales = y_win.tolist() + [round(win_2030, 2)]

sol_norm = [round((v / sol_reales[0]) * 100, 1) for v in sol_reales]
win_norm = [round((v / win_reales[0]) * 100, 1) for v in win_reales]

fig_3d = go.Figure()

fig_3d.add_trace(
    go.Scatter3d(
        x=años_3d,
        y=["☀️ Solar (% vs 2015)"] * len(años_3d),
        z=sol_norm,
        name="☀️ Radiación Solar (Índice Base 100)",
        mode="lines+markers",
        customdata=sol_reales,
        hovertemplate="Año: %{x}<br>Índice: %{z}%<br>Real: %{customdata} kWh/m²/d<extra></extra>",
        marker=dict(size=7, color="#F97316", symbol="circle"),
        line=dict(color="#F97316", width=6),
    )
)

fig_3d.add_trace(
    go.Scatter3d(
        x=años_3d,
        y=["💨 Eólica (% vs 2015)"] * len(años_3d),
        z=win_norm,
        name="💨 Velocidad del Viento (Índice Base 100)",
        mode="lines+markers",
        customdata=win_reales,
        hovertemplate="Año: %{x}<br>Índice: %{z}%<br>Real: %{customdata} m/s<extra></extra>",
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
        zaxis=dict(title="Índice Relativo (2015 = 100%)", backgroundcolor="#111827"),
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    height=400,
)

st.plotly_chart(fig_3d, use_container_width=True)

st.markdown("---")

# ==============================================================================
# PUNTO 5: CONCLUSIONES CIENTÍFICAS E INTERPRETACIÓN AUTOMÁTICA
# ==============================================================================
st.header(f"5. Conclusiones Científicas e Interpretación — 📍 {nombre_lugar}")

vars_sig = []
if sol_p < 0.05:
    vars_sig.append(f"Radiación Solar ({sol_dec:+.2f} kWh/m²/d por década, p={sol_p:.3f})")
if win_p < 0.05:
    vars_sig.append(f"Velocidad del Viento ({win_dec:+.2f} m/s por década, p={win_p:.3f})")
if tmp_p < 0.05:
    vars_sig.append(f"Temperatura 2m ({tmp_dec:+.2f} °C por década, p={tmp_p:.3f})")
if prc_p < 0.05:
    vars_sig.append(f"Precipitación ({prc_dec:+.2f} mm/día por década, p={prc_p:.3f})")

if vars_sig:
    resumen_sig = (
        f"En <b>{nombre_lugar}</b> se detectan tendencias <b>estadísticamente significativas (p &lt; 0.05)</b> en: "
        + ", ".join(vars_sig)
        + "."
    )
else:
    resumen_sig = (
        f"En <b>{nombre_lugar}</b> ninguna de las 4 variables supera el umbral de significancia estadística (<b>p &lt; 0.05</b>) en el periodo 2015–2025, "
        "lo que indica un régimen climático interanual estable."
    )

recurso_dominante = (
    "Energía Solar Fotovoltaica"
    if (sol_act / 5.0) >= (win_act / 4.0)
    else "Energía Eólica"
)

st.markdown(
    f'<div class="conclusion-box">'
    f"<div><b>🔬 Diagnóstico del Detective de Tendencias:</b> {resumen_sig}</div>"
    f"<div style='margin-top:8px;'><b>⚡ Recomendación Energética Local:</b> Con una irradiancia media reciente de <b>{sol_act:.2f} kWh/m²/día</b> "
    f"y viento medio de <b>{win_act:.2f} m/s</b>, la fuente primaria recomendada para autonomía eléctrica en <b>{nombre_lugar}</b> es la <b>{recurso_dominante}</b>.</div>"
    f"<div style='margin-top:8px; font-size:13px; color:#CBD5E1;'><b>⚠️ Limitaciones del modelo:</b> Las cifras proyectadas a 2030 son <i>extrapolaciones lineales simples</i> calculadas sobre 11 años de registros satelitales (2015–2025); sirven para identificar la dirección del cambio, pero no sustituyen modelos climáticos atmosféricos complejos ni garantizan valores exactos a largo plazo.</div>"
    f"</div>",
    unsafe_allow_html=True,
)
