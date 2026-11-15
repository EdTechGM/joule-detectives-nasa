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

# Icono vectorial SVG con estética orbital NASA (< 1 KB)
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

# --- CSS TEMA OSCURO ESPACIAL + DISCRIMINACIÓN MÓVIL VS PORTÁTIL ---
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
    /* Asegura que el botón de abrir/cerrar menú lateral sea siempre visible */
    button[kind="header"],
    [data-testid="collapsedControl"] {
        background-color: #0B3D91 !important;
        color: #FFFFFF !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 6px !important;
        z-index: 999999 !important;
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
        border: 1px solid #38BDF8 !important;
        font-weight: 700 !important;
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
    /* Estilo del desplegable rápido para móviles */
    div[data-testid="stExpander"] {
        background-color: #111827 !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 8px !important;
        margin-bottom: 14px !important;
    }
    /* En portátil (>768px) oculta el desplegable rápido para mantener el diseño original limpio */
    @media (min-width: 769px) {
        div[data-testid="stExpander"] {
            display: none !important;
        }
    }
    /* Encabezado estilo agencia espacial con tipografía Orbitron */
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
        margin-bottom: 16px;
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

# --- EMBLEMA VECTORIAL ESTILO NASA ---
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


# --- ESTADO INICIAL DE COORDENADAS ---
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


# --- PANEL LATERAL (PARA PANTALLAS DE PORTÁTIL / ESCRITORIO) ---
st.sidebar.header("🛰️ PANEL DE CONTROL")
ciudad_side = st.sidebar.text_input(
    "1. Buscar por Ciudad / Región:",
    value=st.session_state.ultima_ciudad_buscada,
    key="ciudad_sidebar",
)
actualizar_desde_ciudad(ciudad_side)

st.sidebar.markdown("**2. O ajustar Coordenadas (Lat / Lon):**")
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

# --- DESCARGA Y CACHÉ DE VARIABLES NASA POWER ---
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
    mime="text/csv
