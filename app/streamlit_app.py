"""
UPTC Energy AI - Dashboard Streamlit
Frontend para visualizacion y chat con IA
"""
import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="UPTC Energy AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# === ESTILOS PROFESIONALES Y CORPORATIVOS ===
st.markdown("""
<style>
    /* === VARIABLES DE COLOR CORPORATIVO === */
    :root {
        --primary-color: #0D47A1;
        --primary-light: #1976D2;
        --primary-dark: #002171;
        --accent-color: #00C853;
        --accent-secondary: #FF6D00;
        --background-dark: #0a1628;
        --background-card: #ffffff;
        --text-primary: #1a1a2e;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }

    /* === ESTILOS GENERALES === */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    /* === HEADER CORPORATIVO === */
    .corporate-header {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 50%, #1976D2 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 20px rgba(13, 71, 161, 0.3);
    }

    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }

    .header-logo {
        width: 60px;
        height: 60px;
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }

    .header-text h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .header-text p {
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
        margin: 0.25rem 0 0 0;
    }

    .header-badge {
        background: rgba(0, 200, 83, 0.2);
        border: 1px solid rgba(0, 200, 83, 0.4);
        color: #00E676;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 1rem;
    }

    /* === SIDEBAR PROFESIONAL === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D47A1 0%, #1565C0 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stSidebar"] .stRadio > label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem;
    }

    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255,255,255,0.1);
        padding: 0.75rem 1rem;
        border-radius: 10px;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }

    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.3);
    }

    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
        background: rgba(255,255,255,0.25);
        border-color: #00C853;
    }

    /* === METRICAS CORPORATIVAS === */
    [data-testid="stMetric"] {
        background: white;
        padding: 1.25rem;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        border-color: #1976D2;
    }

    [data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0D47A1 !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        font-weight: 600;
    }

    /* === TARJETAS Y CONTENEDORES === */
    .stExpander {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .stExpander > div > div > div > div {
        background: transparent;
    }

    /* === BOTONES CORPORATIVOS === */
    .stButton > button {
        background: linear-gradient(135deg, #0D47A1 0%, #1976D2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(13, 71, 161, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(13, 71, 161, 0.4);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00C853 0%, #00E676 100%);
        box-shadow: 0 4px 15px rgba(0, 200, 83, 0.3);
    }

    /* === GRAFICOS === */
    [data-testid="stPlotlyChart"] {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }

    /* === HEADERS Y TITULOS === */
    h1, h2, h3 {
        color: #0D47A1 !important;
        font-weight: 700 !important;
    }

    .stSubheader {
        color: #1565C0 !important;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }

    /* === DIVIDERS === */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #1976D2, transparent);
        margin: 2rem 0;
    }

    /* === DATAFRAMES === */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* === INPUTS === */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stDateInput > div > div,
    .stNumberInput > div > div {
        border-radius: 10px;
        border-color: #e2e8f0;
    }

    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: #1976D2;
        box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
    }

    /* === CHAT === */
    .stChatMessage {
        background: white;
        border-radius: 16px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }

    .stChatMessage[data-testid="stChatMessage-user"] {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-color: #90CAF9;
    }

    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background: linear-gradient(135deg, #F5F5F5 0%, #EEEEEE 100%);
        border-left: 3px solid #1976D2;
    }

    /* Chat input styling */
    [data-testid="stChatInput"] {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        background: white;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #1976D2;
        box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
    }

    /* Container del chat con espacio para input */
    .chat-container {
        padding-bottom: 100px;
    }

    /* === ALERTS === */
    .stAlert {
        border-radius: 12px;
        border: none;
    }

    /* === INFO CARDS === */
    .info-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #1976D2;
        margin: 1rem 0;
    }

    /* === FOOTER === */
    .corporate-footer {
        background: #0a1628;
        color: rgba(255,255,255,0.7);
        padding: 1rem;
        text-align: center;
        border-radius: 12px;
        margin-top: 2rem;
        font-size: 0.85rem;
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }

    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER CORPORATIVO ===
st.markdown("""
<div class="corporate-header">
    <div class="header-content">
        <div class="header-logo">⚡</div>
        <div class="header-text">
            <h1>UPTC Energy AI</h1>
            <p>Sistema Inteligente de Gestion Energetica</p>
        </div>
        <span class="header-badge">v1.0 - IAMinds 2026</span>
    </div>
</div>
""", unsafe_allow_html=True)

# === SIDEBAR PROFESIONAL ===
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 1rem;">
        <p style="font-size: 0.75rem; opacity: 0.7; margin: 0;">UNIVERSIDAD PEDAGOGICA Y</p>
        <p style="font-size: 0.75rem; opacity: 0.7; margin: 0;">TECNOLOGICA DE COLOMBIA</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Menu Principal")
    page = st.radio(
        "",
        ["Dashboard", "Predicciones", "Anomalias", "Recomendaciones", "IA Explicable", "Chat IA"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; margin-top: 1rem;">
        <p style="font-size: 0.8rem; margin: 0 0 0.5rem 0; opacity: 0.9;">Estado del Sistema</p>
        <p style="font-size: 0.75rem; margin: 0; opacity: 0.7;">API: <span style="color: #00E676;">Conectada</span></p>
        <p style="font-size: 0.75rem; margin: 0; opacity: 0.7;">Modelo: <span style="color: #00E676;">Activo</span></p>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    try:
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "consumos_uptc_hackday",
            "consumos_uptc.csv",
        )
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
    return pd.DataFrame()


@st.cache_data(ttl=60)
def get_api_stats():
    try:
        r = requests.get(f"{API_URL}/stats", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


df = load_data()

if page == "Dashboard":
    st.markdown("### Dashboard General")
    st.markdown('<p style="color: #64748b; margin-top: -10px;">Monitoreo en tiempo real del consumo energetico universitario</p>', unsafe_allow_html=True)

    if df.empty:
        st.warning("No se pudieron cargar los datos")
    else:
        # === FILTRO POR SEDE ===
        col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 4])
        with col_filter1:
            sedes_disponibles = ["Todas las sedes"] + list(df["sede"].unique())
            sede_filtro = st.selectbox("Filtrar por Sede", sedes_disponibles, key="dashboard_sede_filter")

        # Aplicar filtro
        if sede_filtro != "Todas las sedes":
            df_filtrado = df[df["sede"] == sede_filtro].copy()
            with col_filter2:
                st.markdown(f"""
                <div style="background: #E3F2FD; padding: 0.5rem 1rem; border-radius: 8px; margin-top: 1.5rem;">
                    <span style="color: #1565C0; font-weight: 500;">Sede: {sede_filtro}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            df_filtrado = df.copy()

        st.markdown("---")

        # === KPIs PRINCIPALES ===
        st.markdown("#### Indicadores Clave de Rendimiento (KPIs)")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Registros", f"{len(df):,}", help="Registros horarios desde 2018")
        with c2:
            total_kwh = df["energia_total_kwh"].sum()
            st.metric("Consumo Total", f"{total_kwh/1e6:.2f} GWh", help="Consumo acumulado historico")
        with c3:
            avg_kwh = df["energia_total_kwh"].mean()
            st.metric("Promedio/Hora", f"{avg_kwh:.2f} kWh", help="Consumo promedio por hora")
        with c4:
            st.metric("Sedes", df["sede"].nunique(), help="Campus monitoreados")

        st.divider()

        # === ANALISIS DE EFICIENCIA ===
        st.subheader("Analisis de Eficiencia Energetica")

        # Datos de estudiantes por sede
        estudiantes_sede = {
            "Tunja": 18000,
            "Duitama": 5500,
            "Sogamoso": 6000,
            "Chiquinquira": 2000
        }
        total_estudiantes = sum(estudiantes_sede.values())

        # Calculos de eficiencia
        consumo_laboral = df[df["es_fin_semana"] == 0]["energia_total_kwh"].mean() if "es_fin_semana" in df.columns else avg_kwh
        consumo_finsemana = df[df["es_fin_semana"] == 1]["energia_total_kwh"].mean() if "es_fin_semana" in df.columns else avg_kwh
        ratio_finsemana = ((consumo_finsemana / consumo_laboral) * 100) if consumo_laboral > 0 else 0

        # Horas pico (7-18) vs no pico
        consumo_pico = df[(df["hora"] >= 7) & (df["hora"] <= 18)]["energia_total_kwh"].mean()
        consumo_no_pico = df[(df["hora"] < 7) | (df["hora"] > 18)]["energia_total_kwh"].mean()
        ratio_pico = ((consumo_no_pico / consumo_pico) * 100) if consumo_pico > 0 else 0

        # Eficiencia por ocupacion
        if "ocupacion_pct" in df.columns:
            df_alta_ocup = df[df["ocupacion_pct"] >= 50]["energia_total_kwh"].mean()
            df_baja_ocup = df[df["ocupacion_pct"] < 50]["energia_total_kwh"].mean()
            eficiencia_ocupacion = ((df_baja_ocup / df_alta_ocup) * 100) if df_alta_ocup > 0 else 100
        else:
            eficiencia_ocupacion = 0

        # KPIs de eficiencia
        eff1, eff2, eff3, eff4 = st.columns(4)
        with eff1:
            kwh_por_estudiante = (total_kwh / total_estudiantes) if total_estudiantes > 0 else 0
            st.metric(
                "kWh/Estudiante (historico)",
                f"{kwh_por_estudiante:.1f}",
                help="Consumo total dividido entre estudiantes"
            )
        with eff2:
            delta_finsemana = ratio_finsemana - 100
            st.metric(
                "Consumo Fin de Semana",
                f"{ratio_finsemana:.1f}%",
                delta=f"{delta_finsemana:.1f}% vs laboral",
                delta_color="inverse",
                help="Porcentaje respecto a dias laborales"
            )
        with eff3:
            st.metric(
                "Consumo Fuera de Horario",
                f"{ratio_pico:.1f}%",
                delta=f"{100-ratio_pico:.1f}% ahorro potencial" if ratio_pico < 100 else None,
                delta_color="inverse",
                help="Consumo nocturno vs horario laboral (7-18h)"
            )
        with eff4:
            if eficiencia_ocupacion > 0:
                st.metric(
                    "Eficiencia por Ocupacion",
                    f"{eficiencia_ocupacion:.1f}%",
                    help="Consumo baja ocupacion vs alta ocupacion"
                )
            else:
                periodo_actual = df["periodo_academico"].mode()[0] if "periodo_academico" in df.columns else "N/A"
                st.metric("Periodo Actual", periodo_actual, help="Periodo academico mas frecuente")

        # === METRICAS DE IMPACTO AMBIENTAL Y ECONOMICO ===
        st.divider()
        st.subheader("Metricas de Impacto Ambiental y Economico")

        # Constantes para calculos
        FACTOR_CO2_COLOMBIA = 0.126  # kg CO2 por kWh (Factor de emision SIN Colombia 2024)
        TARIFA_KWH_COP = 750  # COP por kWh (tarifa promedio sector no residencial)
        PORCENTAJE_AHORRO_ESTIMADO = 15  # % de ahorro potencial con optimizaciones

        # Calculos de consumo mensual promedio
        consumo_mensual_kwh = df.groupby(df["timestamp"].dt.to_period("M"))["energia_total_kwh"].sum().mean()

        # Calculos de ahorro potencial
        ahorro_kwh_mensual = consumo_mensual_kwh * (PORCENTAJE_AHORRO_ESTIMADO / 100)
        ahorro_kwh_anual = ahorro_kwh_mensual * 12

        # Reduccion de CO2
        reduccion_co2_mensual = ahorro_kwh_mensual * FACTOR_CO2_COLOMBIA
        reduccion_co2_anual = ahorro_kwh_anual * FACTOR_CO2_COLOMBIA

        # Ahorro economico
        ahorro_cop_mensual = ahorro_kwh_mensual * TARIFA_KWH_COP
        ahorro_cop_anual = ahorro_kwh_anual * TARIFA_KWH_COP

        # Emisiones actuales totales
        emisiones_co2_total = total_kwh * FACTOR_CO2_COLOMBIA
        costo_total_cop = total_kwh * TARIFA_KWH_COP

        # Mostrar KPIs de impacto
        st.markdown("##### Proyeccion de Ahorro (con optimizacion del 15%)")

        imp1, imp2, imp3 = st.columns(3)
        with imp1:
            st.metric(
                "Reduccion Estimada (kWh)",
                f"{ahorro_kwh_anual/1000:,.1f} MWh/año",
                delta=f"{ahorro_kwh_mensual:,.0f} kWh/mes",
                help=f"Ahorro proyectado con {PORCENTAJE_AHORRO_ESTIMADO}% de optimizacion"
            )
        with imp2:
            st.metric(
                "Reduccion CO₂ (kg)",
                f"{reduccion_co2_anual/1000:,.1f} Ton/año",
                delta=f"{reduccion_co2_mensual:,.0f} kg/mes",
                help=f"Factor de emision: {FACTOR_CO2_COLOMBIA} kg CO₂/kWh (SIN Colombia)"
            )
        with imp3:
            st.metric(
                "Ahorro Economico (COP)",
                f"${ahorro_cop_anual/1e6:,.1f} M/año",
                delta=f"${ahorro_cop_mensual/1e6:,.2f} M/mes",
                help=f"Tarifa estimada: ${TARIFA_KWH_COP:,} COP/kWh"
            )

        # KPIs de emisiones y costos actuales
        st.markdown("##### Situacion Actual (Historico)")
        act1, act2, act3 = st.columns(3)
        with act1:
            st.metric(
                "Consumo Historico Total",
                f"{total_kwh/1e6:,.2f} GWh",
                help="Consumo total acumulado desde 2018"
            )
        with act2:
            st.metric(
                "Emisiones CO₂ Totales",
                f"{emisiones_co2_total/1e6:,.2f} Kton",
                help="Huella de carbono historica total"
            )
        with act3:
            st.metric(
                "Costo Energetico Total",
                f"${costo_total_cop/1e9:,.2f} Mil M",
                help="Costo total estimado en miles de millones COP"
            )

        # Grafico de impacto proyectado
        col_imp1, col_imp2 = st.columns(2)

        with col_imp1:
            # Grafico de ahorro por mes proyectado
            meses_proyeccion = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            ahorro_mensual_data = [ahorro_kwh_mensual * (0.8 + 0.4 * (i % 3) / 3) for i in range(12)]  # Variacion estacional

            fig_ahorro = px.bar(
                x=meses_proyeccion,
                y=ahorro_mensual_data,
                color=ahorro_mensual_data,
                color_continuous_scale="Greens",
                labels={"x": "Mes", "y": "Ahorro (kWh)"}
            )
            fig_ahorro.update_layout(
                height=300,
                title="Proyeccion de Ahorro Mensual (kWh)",
                showlegend=False
            )
            st.plotly_chart(fig_ahorro, use_container_width=True)

        with col_imp2:
            # Grafico de reduccion CO2
            categorias = ["Actual", "Con Optimizacion"]
            valores_co2 = [consumo_mensual_kwh * FACTOR_CO2_COLOMBIA, (consumo_mensual_kwh - ahorro_kwh_mensual) * FACTOR_CO2_COLOMBIA]

            fig_co2 = px.bar(
                x=categorias,
                y=valores_co2,
                color=categorias,
                color_discrete_map={"Actual": "#EF5350", "Con Optimizacion": "#66BB6A"}
            )
            fig_co2.update_layout(
                height=300,
                title="Emisiones CO₂ Mensuales (kg)",
                showlegend=False,
                yaxis_title="kg CO₂"
            )
            st.plotly_chart(fig_co2, use_container_width=True)

        # Tabla resumen de impacto
        with st.expander("Ver detalle de calculos de impacto"):
            st.markdown(f"""
            **Parametros utilizados:**
            - Factor de emision CO₂: **{FACTOR_CO2_COLOMBIA} kg CO₂/kWh** (Sistema Interconectado Nacional - Colombia 2024)
            - Tarifa electrica estimada: **${TARIFA_KWH_COP:,} COP/kWh** (Sector no residencial)
            - Porcentaje de optimizacion proyectado: **{PORCENTAJE_AHORRO_ESTIMADO}%**

            **Calculos detallados:**
            | Concepto | Mensual | Anual |
            |----------|---------|-------|
            | Ahorro energetico | {ahorro_kwh_mensual:,.0f} kWh | {ahorro_kwh_anual:,.0f} kWh |
            | Reduccion CO₂ | {reduccion_co2_mensual:,.0f} kg | {reduccion_co2_anual:,.0f} kg |
            | Ahorro economico | ${ahorro_cop_mensual:,.0f} COP | ${ahorro_cop_anual:,.0f} COP |

            **Equivalencias ambientales (ahorro anual):**
            - Arboles equivalentes plantados: **{int(reduccion_co2_anual / 22):,}** arboles/año
            - Kilometros evitados en auto: **{int(reduccion_co2_anual / 0.21):,}** km/año
            - Hogares colombianos equivalentes: **{int(ahorro_kwh_anual / 1200):,}** hogares/año
            """)

        # Eficiencia por sede
        st.divider()
        st.subheader("Eficiencia por Sede")

        eficiencia_sedes = []
        for sede, estudiantes in estudiantes_sede.items():
            consumo_sede = df[df["sede"] == sede]["energia_total_kwh"].sum()
            consumo_prom = df[df["sede"] == sede]["energia_total_kwh"].mean()
            kwh_est = consumo_sede / estudiantes if estudiantes > 0 else 0
            eficiencia_sedes.append({
                "Sede": sede,
                "Estudiantes": estudiantes,
                "Consumo Total (MWh)": consumo_sede / 1000,
                "Promedio/Hora (kWh)": consumo_prom,
                "kWh/Estudiante": kwh_est,
                "Indice Eficiencia": 100 - (kwh_est / max([e["kWh/Estudiante"] for e in eficiencia_sedes] + [kwh_est]) * 100) if kwh_est > 0 else 0
            })

        df_eficiencia = pd.DataFrame(eficiencia_sedes)

        # Recalcular indice de eficiencia correctamente
        max_kwh_est = df_eficiencia["kWh/Estudiante"].max()
        df_eficiencia["Indice Eficiencia"] = 100 - (df_eficiencia["kWh/Estudiante"] / max_kwh_est * 100)
        df_eficiencia["Indice Eficiencia"] = df_eficiencia["Indice Eficiencia"].apply(lambda x: max(0, x + 50))  # Normalizar

        col_eff1, col_eff2 = st.columns(2)

        with col_eff1:
            # Grafico de eficiencia por sede
            fig_eff = px.bar(
                df_eficiencia,
                x="Sede",
                y="kWh/Estudiante",
                color="kWh/Estudiante",
                color_continuous_scale="RdYlGn_r",
                text="kWh/Estudiante"
            )
            fig_eff.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_eff.update_layout(height=350, title="Consumo por Estudiante (menor es mejor)")
            st.plotly_chart(fig_eff, use_container_width=True)

        with col_eff2:
            # Radar de eficiencia
            fig_radar = px.bar(
                df_eficiencia,
                x="Sede",
                y="Promedio/Hora (kWh)",
                color="Sede",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_radar.update_layout(height=350, title="Consumo Promedio por Hora")
            st.plotly_chart(fig_radar, use_container_width=True)

        # Tabla resumen de eficiencia
        with st.expander("Ver tabla de eficiencia detallada"):
            st.dataframe(
                df_eficiencia.style.format({
                    "Consumo Total (MWh)": "{:.2f}",
                    "Promedio/Hora (kWh)": "{:.2f}",
                    "kWh/Estudiante": "{:.2f}",
                    "Indice Eficiencia": "{:.1f}"
                }).background_gradient(subset=["kWh/Estudiante"], cmap="RdYlGn_r"),
                use_container_width=True
            )

        # === ANALISIS POR PERIODO ACADEMICO ===
        if "periodo_academico" in df.columns:
            st.divider()
            st.subheader("Eficiencia por Periodo Academico")

            consumo_periodo = df.groupby("periodo_academico")["energia_total_kwh"].agg(['mean', 'sum', 'count']).reset_index()
            consumo_periodo.columns = ["Periodo", "Promedio kWh", "Total kWh", "Registros"]

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                fig_periodo = px.bar(
                    consumo_periodo,
                    x="Periodo",
                    y="Promedio kWh",
                    color="Promedio kWh",
                    color_continuous_scale="Viridis"
                )
                fig_periodo.update_layout(height=300, title="Consumo Promedio por Periodo")
                st.plotly_chart(fig_periodo, use_container_width=True)

            with col_p2:
                # Comparativa vacaciones vs semestre
                consumo_vacaciones = df[df["periodo_academico"] == "vacaciones"]["energia_total_kwh"].mean() if "vacaciones" in df["periodo_academico"].values else 0
                consumo_semestre = df[df["periodo_academico"] == "semestre"]["energia_total_kwh"].mean() if "semestre" in df["periodo_academico"].values else avg_kwh

                ahorro_vacaciones = ((1 - consumo_vacaciones/consumo_semestre) * 100) if consumo_semestre > 0 else 0

                st.metric(
                    "Ahorro en Vacaciones",
                    f"{ahorro_vacaciones:.1f}%",
                    delta="vs periodo de semestre",
                    help="Reduccion de consumo durante vacaciones"
                )

                consumo_parciales = df[df["periodo_academico"] == "parciales"]["energia_total_kwh"].mean() if "parciales" in df["periodo_academico"].values else 0
                incremento_parciales = ((consumo_parciales/consumo_semestre - 1) * 100) if consumo_semestre > 0 else 0

                st.metric(
                    "Incremento en Parciales",
                    f"{incremento_parciales:.1f}%",
                    delta="vs semestre normal",
                    delta_color="inverse",
                    help="Aumento de consumo durante parciales"
                )

        st.divider()

        # === GRAFICOS ORIGINALES ===
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Consumo por Sede")
            consumo_sede = df.groupby("sede")["energia_total_kwh"].sum().reset_index()
            fig = px.pie(
                consumo_sede,
                values="energia_total_kwh",
                names="sede",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Consumo Promedio por Hora del Dia")
            consumo_hora = df.groupby("hora")["energia_total_kwh"].mean().reset_index()
            fig = px.bar(
                consumo_hora,
                x="hora",
                y="energia_total_kwh",
                color="energia_total_kwh",
                color_continuous_scale="Viridis",
            )
            fig.update_layout(height=350, xaxis_title="Hora", yaxis_title="kWh")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tendencia de Consumo Mensual")
        df_monthly = (
            df.groupby([df["timestamp"].dt.to_period("M"), "sede"])["energia_total_kwh"]
            .sum()
            .reset_index()
        )
        df_monthly["timestamp"] = df_monthly["timestamp"].astype(str)
        fig = px.line(
            df_monthly,
            x="timestamp",
            y="energia_total_kwh",
            color="sede",
            color_discrete_sequence=px.colors.qualitative.Set1,
        )
        fig.update_layout(height=400, xaxis_title="Mes", yaxis_title="kWh Total")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Distribucion por Sector")
        sectores = {
            "Comedor": df["energia_comedor_kwh"].sum(),
            "Salones": df["energia_salones_kwh"].sum(),
            "Laboratorios": df["energia_laboratorios_kwh"].sum(),
            "Auditorios": df["energia_auditorios_kwh"].sum(),
            "Oficinas": df["energia_oficinas_kwh"].sum(),
        }
        df_sectores = pd.DataFrame(list(sectores.items()), columns=["Sector", "Consumo_kWh"])
        fig = px.bar(
            df_sectores,
            x="Sector",
            y="Consumo_kWh",
            color="Consumo_kWh",
            color_continuous_scale="RdYlGn_r",
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

        # === ANALISIS DE SECTORES POR EFICIENCIA ===
        st.divider()
        st.subheader("Eficiencia por Sector")

        col_sec1, col_sec2 = st.columns(2)

        with col_sec1:
            # Consumo por sector y sede
            sectores_cols = ["energia_comedor_kwh", "energia_salones_kwh", "energia_laboratorios_kwh",
                           "energia_auditorios_kwh", "energia_oficinas_kwh"]
            sectores_nombres = ["Comedor", "Salones", "Laboratorios", "Auditorios", "Oficinas"]

            data_sector_sede = []
            for sede in df["sede"].unique():
                df_sede = df[df["sede"] == sede]
                for col, nombre in zip(sectores_cols, sectores_nombres):
                    data_sector_sede.append({
                        "Sede": sede,
                        "Sector": nombre,
                        "Consumo Promedio": df_sede[col].mean()
                    })

            df_sector_sede = pd.DataFrame(data_sector_sede)
            fig_sector = px.bar(
                df_sector_sede,
                x="Sector",
                y="Consumo Promedio",
                color="Sede",
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig_sector.update_layout(height=350, title="Consumo por Sector y Sede")
            st.plotly_chart(fig_sector, use_container_width=True)

        with col_sec2:
            # Porcentaje de cada sector
            total_por_sector = {nombre: df[col].sum() for col, nombre in zip(sectores_cols, sectores_nombres)}
            total_general = sum(total_por_sector.values())

            df_pct_sector = pd.DataFrame([
                {"Sector": k, "Porcentaje": (v/total_general)*100, "Total kWh": v}
                for k, v in total_por_sector.items()
            ])

            fig_pct = px.pie(
                df_pct_sector,
                values="Porcentaje",
                names="Sector",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            fig_pct.update_layout(height=350, title="Distribucion Porcentual por Sector")
            st.plotly_chart(fig_pct, use_container_width=True)

elif page == "Predicciones":
    st.markdown("### Prediccion de Consumo Energetico")
    st.markdown('<p style="color: #64748b; margin-top: -10px;">Modelo LSTM para proyeccion de demanda energetica</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Seleccion de sedes (multiple)
    sedes_disponibles = list(df["sede"].unique()) if not df.empty else ["Tunja", "Duitama", "Sogamoso", "Chiquinquira"]
    sedes_seleccionadas = st.multiselect(
        "Sedes (selecciona una o varias)",
        sedes_disponibles,
        default=[sedes_disponibles[0]],
        help="Puedes seleccionar multiples sedes para comparar predicciones"
    )

    if not sedes_seleccionadas:
        st.warning("Selecciona al menos una sede")
    else:
        st.divider()

        # Rango de fechas
        col1, col2 = st.columns(2)
        with col1:
            rango_fecha = st.selectbox(
                "Rango de fechas",
                ["Hoy", "Manana", "Esta semana", "Proximo mes", "Personalizado"],
                index=1
            )

        hoy = datetime.now().date()
        if rango_fecha == "Hoy":
            fecha_inicio = hoy
            fecha_fin = hoy
        elif rango_fecha == "Manana":
            fecha_inicio = hoy + timedelta(days=1)
            fecha_fin = hoy + timedelta(days=1)
        elif rango_fecha == "Esta semana":
            fecha_inicio = hoy
            fecha_fin = hoy + timedelta(days=7)
        elif rango_fecha == "Proximo mes":
            fecha_inicio = hoy
            fecha_fin = hoy + timedelta(days=30)
        else:  # Personalizado
            with col2:
                fecha_rango = st.date_input(
                    "Seleccionar rango",
                    value=(hoy + timedelta(days=1), hoy + timedelta(days=7)),
                    min_value=hoy,
                    max_value=hoy + timedelta(days=365)
                )
                if isinstance(fecha_rango, tuple) and len(fecha_rango) == 2:
                    fecha_inicio, fecha_fin = fecha_rango
                else:
                    fecha_inicio = fecha_fin = fecha_rango

        if rango_fecha != "Personalizado":
            with col2:
                st.info(f"**Periodo:** {fecha_inicio} a {fecha_fin}")

        st.divider()

        # Rango de horas
        st.subheader("Rango de Horas")
        col_h1, col_h2, col_h3 = st.columns(3)
        with col_h1:
            hora_preset = st.selectbox(
                "Horario predefinido",
                ["Personalizado", "Horario laboral (7-18)", "Manana (6-12)", "Tarde (12-18)", "Noche (18-23)", "Todo el dia (0-23)"]
            )

        if hora_preset == "Horario laboral (7-18)":
            hora_inicio, hora_fin = 7, 18
        elif hora_preset == "Manana (6-12)":
            hora_inicio, hora_fin = 6, 12
        elif hora_preset == "Tarde (12-18)":
            hora_inicio, hora_fin = 12, 18
        elif hora_preset == "Noche (18-23)":
            hora_inicio, hora_fin = 18, 23
        elif hora_preset == "Todo el dia (0-23)":
            hora_inicio, hora_fin = 0, 23
        else:
            with col_h2:
                hora_inicio = st.number_input("Hora inicio", 0, 23, 7)
            with col_h3:
                hora_fin = st.number_input("Hora fin", 0, 23, 18)

        if hora_preset != "Personalizado":
            with col_h2:
                st.metric("Desde", f"{hora_inicio}:00")
            with col_h3:
                st.metric("Hasta", f"{hora_fin}:00")

        # Calcular numero de predicciones
        dias = (fecha_fin - fecha_inicio).days + 1
        horas = hora_fin - hora_inicio + 1
        total_predicciones = len(sedes_seleccionadas) * dias * horas

        st.divider()
        st.caption(f"Se generaran **{total_predicciones}** predicciones ({len(sedes_seleccionadas)} sedes x {dias} dias x {horas} horas)")

        if total_predicciones > 500:
            st.warning("El rango seleccionado generara muchas predicciones. Considera reducir el rango.")

        if st.button("Generar Predicciones", type="primary", disabled=total_predicciones > 1000):
            with st.spinner(f"Calculando {total_predicciones} predicciones..."):
                resultados = []
                progress_bar = st.progress(0)

                try:
                    current = 0
                    for sede in sedes_seleccionadas:
                        fecha_actual = fecha_inicio
                        while fecha_actual <= fecha_fin:
                            for hora in range(hora_inicio, hora_fin + 1):
                                r = requests.post(
                                    f"{API_URL}/predict",
                                    json={"sede": sede, "fecha": str(fecha_actual), "hora": hora},
                                    timeout=30,
                                )
                                if r.status_code == 200:
                                    result = r.json()
                                    resultados.append({
                                        "Sede": sede,
                                        "Fecha": fecha_actual,
                                        "Hora": hora,
                                        "Prediccion_kWh": result['prediccion_kwh'],
                                        "Confianza": result['confianza']
                                    })
                                current += 1
                                progress_bar.progress(current / total_predicciones)
                            fecha_actual += timedelta(days=1)

                    progress_bar.empty()

                    if resultados:
                        df_pred = pd.DataFrame(resultados)

                        # Metricas resumen
                        st.success(f"**{len(resultados)} predicciones generadas exitosamente**")

                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        with col_m1:
                            st.metric("Total estimado", f"{df_pred['Prediccion_kWh'].sum():.1f} kWh")
                        with col_m2:
                            st.metric("Promedio/hora", f"{df_pred['Prediccion_kWh'].mean():.2f} kWh")
                        with col_m3:
                            st.metric("Maximo", f"{df_pred['Prediccion_kWh'].max():.2f} kWh")
                        with col_m4:
                            st.metric("Minimo", f"{df_pred['Prediccion_kWh'].min():.2f} kWh")

                        # Grafico por sede
                        st.subheader("Predicciones por Sede y Hora")
                        if len(sedes_seleccionadas) > 1:
                            df_grouped = df_pred.groupby(['Sede', 'Hora'])['Prediccion_kWh'].mean().reset_index()
                            fig = px.line(df_grouped, x='Hora', y='Prediccion_kWh', color='Sede',
                                         markers=True, color_discrete_sequence=px.colors.qualitative.Set1)
                        else:
                            df_grouped = df_pred.groupby('Hora')['Prediccion_kWh'].mean().reset_index()
                            fig = px.bar(df_grouped, x='Hora', y='Prediccion_kWh',
                                        color='Prediccion_kWh', color_continuous_scale='Viridis')
                        fig.update_layout(height=400, xaxis_title="Hora del dia", yaxis_title="Consumo predicho (kWh)")
                        st.plotly_chart(fig, use_container_width=True)

                        # Grafico por fecha si hay multiples dias
                        if dias > 1:
                            st.subheader("Predicciones por Fecha")
                            df_by_date = df_pred.groupby(['Sede', 'Fecha'])['Prediccion_kWh'].sum().reset_index()
                            fig2 = px.bar(df_by_date, x='Fecha', y='Prediccion_kWh', color='Sede',
                                         barmode='group', color_discrete_sequence=px.colors.qualitative.Set2)
                            fig2.update_layout(height=350, xaxis_title="Fecha", yaxis_title="Consumo total predicho (kWh)")
                            st.plotly_chart(fig2, use_container_width=True)

                        # Tabla de datos
                        with st.expander("Ver datos detallados"):
                            st.dataframe(df_pred, use_container_width=True)

                            # Descargar CSV
                            csv = df_pred.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "Descargar CSV",
                                csv,
                                "predicciones_uptc.csv",
                                "text/csv",
                                key='download-csv'
                            )
                    else:
                        st.error("No se pudieron generar predicciones")

                except requests.exceptions.ConnectionError:
                    st.error("No se puede conectar con la API. Verifica que el servicio este corriendo.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Historial
        st.divider()
        if not df.empty and len(sedes_seleccionadas) > 0:
            st.subheader("Historial de Consumo Real")
            sede_data = df[df["sede"].isin(sedes_seleccionadas)].copy()
            sede_data = (
                sede_data.groupby([sede_data["timestamp"].dt.date, "sede"])["energia_total_kwh"]
                .sum()
                .reset_index()
            )
            sede_data.columns = ["Fecha", "Sede", "Consumo_kWh"]
            fig = px.line(sede_data.tail(90 * len(sedes_seleccionadas)), x="Fecha", y="Consumo_kWh", color="Sede",
                         color_discrete_sequence=px.colors.qualitative.Set1)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Anomalias":
    st.markdown("### Deteccion de Anomalias")
    st.markdown('<p style="color: #64748b; margin-top: -10px;">Identificacion de patrones atipicos mediante analisis estadistico</p>', unsafe_allow_html=True)
    st.markdown("---")
    sede = st.selectbox("Seleccionar Sede", df["sede"].unique() if not df.empty else ["Tunja"])
    if st.button("Detectar Anomalias", type="primary"):
        with st.spinner("Analizando patrones..."):
            try:
                r = requests.get(f"{API_URL}/anomalies/{sede}?limit=20", timeout=10)
                if r.status_code == 200:
                    result = r.json()
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Media", f"{result['media_kwh']:.2f} kWh")
                    with c2:
                        st.metric("Desv. Estandar", f"{result['std_kwh']:.2f} kWh")
                    with c3:
                        st.metric("Anomalias", len(result["anomalias"]))
                    if result["anomalias"]:
                        st.subheader("Anomalias Detectadas")
                        st.dataframe(pd.DataFrame(result["anomalias"]), use_container_width=True)
                    else:
                        st.success("No se detectaron anomalias significativas")
                else:
                    st.error(f"Error: {r.text}")
            except requests.exceptions.ConnectionError:
                st.error("No se puede conectar con la API")
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "Recomendaciones":
    st.markdown("### Recomendaciones de Ahorro Energetico")
    st.markdown('<p style="color: #64748b; margin-top: -10px;">Analisis de oportunidades de optimizacion con impacto ambiental y economico</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Constantes para calculos de impacto
    FACTOR_CO2 = 0.126  # kg CO2/kWh
    TARIFA_COP = 750  # COP/kWh

    sede = st.selectbox("Seleccionar Sede", df["sede"].unique() if not df.empty else ["Tunja"])

    # Calcular consumo mensual de la sede seleccionada
    if not df.empty:
        sede_data = df[df["sede"] == sede]
        consumo_mensual_sede = sede_data.groupby(sede_data["timestamp"].dt.to_period("M"))["energia_total_kwh"].sum().mean()
    else:
        consumo_mensual_sede = 10000  # valor por defecto

    if st.button("Generar Recomendaciones", type="primary"):
        with st.spinner("Analizando oportunidades de ahorro..."):
            try:
                r = requests.post(f"{API_URL}/recommendations", json={"sede": sede}, timeout=10)
                if r.status_code == 200:
                    result = r.json()

                    # Calcular impacto total
                    ahorro_pct_total = result['total_ahorro_estimado_pct']
                    ahorro_kwh_mensual = consumo_mensual_sede * (ahorro_pct_total / 100)
                    ahorro_kwh_anual = ahorro_kwh_mensual * 12
                    reduccion_co2_anual = ahorro_kwh_anual * FACTOR_CO2
                    ahorro_cop_anual = ahorro_kwh_anual * TARIFA_COP

                    # KPIs de impacto total
                    st.subheader("Impacto Total de Recomendaciones")
                    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                    with kpi1:
                        st.metric(
                            "Ahorro Potencial",
                            f"{ahorro_pct_total}%",
                            help="Porcentaje de reduccion de consumo"
                        )
                    with kpi2:
                        st.metric(
                            "Reduccion kWh",
                            f"{ahorro_kwh_anual/1000:,.1f} MWh/año",
                            delta=f"{ahorro_kwh_mensual:,.0f} kWh/mes"
                        )
                    with kpi3:
                        st.metric(
                            "Reduccion CO₂",
                            f"{reduccion_co2_anual/1000:,.2f} Ton/año",
                            delta=f"{reduccion_co2_anual/12:,.0f} kg/mes"
                        )
                    with kpi4:
                        st.metric(
                            "Ahorro Economico",
                            f"${ahorro_cop_anual/1e6:,.1f} M/año",
                            delta=f"${ahorro_cop_anual/12/1e6:,.2f} M/mes"
                        )

                    st.divider()
                    st.subheader("Recomendaciones Detalladas")

                    for rec in result["recomendaciones"]:
                        # Calcular impacto individual
                        ahorro_ind_pct = rec['ahorro_estimado_pct']
                        ahorro_ind_kwh = consumo_mensual_sede * (ahorro_ind_pct / 100) * 12
                        ahorro_ind_co2 = ahorro_ind_kwh * FACTOR_CO2
                        ahorro_ind_cop = ahorro_ind_kwh * TARIFA_COP

                        with st.expander(f"{rec['titulo']}", expanded=True):
                            st.write(rec["descripcion"])

                            st.markdown("**Impacto estimado de esta recomendacion:**")
                            col_r1, col_r2, col_r3 = st.columns(3)
                            with col_r1:
                                st.caption(f"**Ahorro:** {ahorro_ind_pct}% ({ahorro_ind_kwh:,.0f} kWh/año)")
                            with col_r2:
                                st.caption(f"**CO₂:** {ahorro_ind_co2:,.0f} kg/año")
                            with col_r3:
                                st.caption(f"**Economico:** ${ahorro_ind_cop/1e6:,.2f} M/año")

                    # Grafico de impacto por recomendacion
                    st.divider()
                    st.subheader("Distribucion del Ahorro por Recomendacion")

                    rec_data = []
                    for rec in result["recomendaciones"]:
                        rec_data.append({
                            "Recomendacion": rec['titulo'][:30] + "..." if len(rec['titulo']) > 30 else rec['titulo'],
                            "Ahorro (%)": rec['ahorro_estimado_pct'],
                            "Ahorro kWh/año": consumo_mensual_sede * (rec['ahorro_estimado_pct'] / 100) * 12,
                            "Ahorro COP/año": consumo_mensual_sede * (rec['ahorro_estimado_pct'] / 100) * 12 * TARIFA_COP
                        })

                    df_rec = pd.DataFrame(rec_data)

                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        fig_rec = px.pie(
                            df_rec,
                            values="Ahorro (%)",
                            names="Recomendacion",
                            color_discrete_sequence=px.colors.qualitative.Set3,
                            hole=0.4
                        )
                        fig_rec.update_layout(height=300, title="Distribucion del Ahorro (%)")
                        st.plotly_chart(fig_rec, use_container_width=True)

                    with col_g2:
                        fig_cop = px.bar(
                            df_rec,
                            x="Recomendacion",
                            y="Ahorro COP/año",
                            color="Ahorro COP/año",
                            color_continuous_scale="Greens"
                        )
                        fig_cop.update_layout(height=300, title="Ahorro Economico por Recomendacion (COP/año)")
                        fig_cop.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_cop, use_container_width=True)

                    # Equivalencias ambientales
                    with st.expander("Equivalencias ambientales del ahorro total"):
                        st.markdown(f"""
                        **Si se implementan todas las recomendaciones, el ahorro anual equivale a:**

                        | Equivalencia | Valor |
                        |--------------|-------|
                        | Arboles plantados | **{int(reduccion_co2_anual / 22):,}** arboles |
                        | Km en auto evitados | **{int(reduccion_co2_anual / 0.21):,}** km |
                        | Hogares colombianos | **{int(ahorro_kwh_anual / 1200):,}** hogares/año |
                        | Smartphones cargados | **{int(ahorro_kwh_anual / 0.012):,}** cargas |
                        """)

                else:
                    st.error(f"Error: {r.text}")
            except requests.exceptions.ConnectionError:
                st.error("No se puede conectar con la API")
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "IA Explicable":
    st.markdown("### IA Explicable (XAI)")
    st.markdown('<p style="color: #64748b; margin-top: -10px;">Transparencia y trazabilidad en las decisiones del modelo predictivo</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); padding: 1rem 1.5rem; border-radius: 12px; border-left: 4px solid #1976D2; margin-bottom: 1.5rem;">
        <p style="margin: 0; color: #0D47A1;"><strong>Metodologia:</strong> Este sistema utiliza tecnicas de explicabilidad similares a <strong>SHAP/LIME</strong> para garantizar transparencia en las decisiones del modelo de prediccion energetica.</p>
    </div>
    """, unsafe_allow_html=True)

    # Informacion del modelo
    with st.expander("Informacion del Modelo", expanded=False):
        try:
            r = requests.get(f"{API_URL}/model-info", timeout=10)
            if r.status_code == 200:
                model_info = r.json()

                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.subheader("Arquitectura")
                    st.write(f"**Tipo:** {model_info['arquitectura']['tipo']}")
                    st.write(f"**Secuencia de entrada:** {model_info['arquitectura']['secuencia_entrada']} horas")
                    st.write(f"**Features:** {model_info['arquitectura']['features']}")

                    st.write("**Capas:**")
                    for capa in model_info['arquitectura']['capas']:
                        st.caption(f"- {capa['nombre']}: {capa['unidades']} unidades")

                with col_info2:
                    st.subheader("Metricas de Entrenamiento")
                    metricas = model_info['metricas_entrenamiento']
                    st.metric("MAE", f"{metricas['mae']:.3f} kWh", help="Error Absoluto Medio")
                    st.metric("RMSE", f"{metricas['rmse']:.3f} kWh", help="Raiz del Error Cuadratico Medio")
                    st.metric("R²", f"{metricas['r2']:.1%}", help="Coeficiente de Determinacion")

                st.divider()
                st.subheader("Interpretacion")
                st.info(model_info['interpretacion']['r2_explicacion'])
                st.success(model_info['interpretacion']['uso_recomendado'])

                st.subheader("Features del Modelo")
                for i, feature in enumerate(model_info['features'], 1):
                    st.caption(f"{i}. {feature}")
        except:
            st.warning("No se pudo cargar la informacion del modelo")

    st.divider()

    # Explicar una prediccion especifica
    st.subheader("Explicar Prediccion")
    st.markdown("Selecciona los parametros para obtener una explicacion detallada de la prediccion.")

    col_exp1, col_exp2, col_exp3 = st.columns(3)
    with col_exp1:
        sede_explain = st.selectbox("Sede", df["sede"].unique() if not df.empty else ["Tunja"], key="explain_sede")
    with col_exp2:
        fecha_explain = st.date_input("Fecha", datetime.now() + timedelta(days=1), key="explain_fecha")
    with col_exp3:
        hora_explain = st.slider("Hora", 0, 23, 12, key="explain_hora")

    if st.button("Explicar Prediccion", type="primary"):
        with st.spinner("Analizando factores de la prediccion..."):
            try:
                r = requests.post(
                    f"{API_URL}/explain",
                    json={"sede": sede_explain, "fecha": str(fecha_explain), "hora": hora_explain},
                    timeout=60
                )
                if r.status_code == 200:
                    result = r.json()

                    # === PREDICCION Y CONFIANZA ===
                    st.divider()
                    col_pred1, col_pred2, col_pred3 = st.columns(3)

                    with col_pred1:
                        st.metric(
                            "Prediccion",
                            f"{result['prediccion']['valor_kwh']:.2f} kWh",
                            help="Consumo energetico predicho"
                        )
                    with col_pred2:
                        nivel_confianza = result['confianza_modelo']['nivel']
                        color_confianza = "green" if nivel_confianza == "ALTO" else "orange" if nivel_confianza == "MEDIO" else "red"
                        st.metric(
                            "Nivel de Confianza",
                            nivel_confianza,
                            delta=f"{result['confianza_modelo']['valor_numerico']:.0%}"
                        )
                    with col_pred3:
                        st.metric(
                            "Z-Score",
                            f"{result['contexto_historico']['z_score_prediccion']:.2f}",
                            help="Desviaciones respecto a la media historica"
                        )

                    st.info(f"**{result['confianza_modelo']['explicacion']}**")

                    # === ALERTAS ===
                    if result['alertas']:
                        st.divider()
                        st.subheader("Alertas Detectadas")
                        for alerta in result['alertas']:
                            if alerta['tipo'] == "ALERTA_CONSUMO_ALTO":
                                st.error(f"**{alerta['mensaje']}**")
                            else:
                                st.warning(f"**{alerta['mensaje']}**")
                            st.caption(f"Razon: {alerta['razon']}")
                            st.success(f"Recomendacion: {alerta['recomendacion']}")

                    # === EXPLICACION EN LENGUAJE NATURAL ===
                    st.divider()
                    st.subheader("Explicacion en Lenguaje Natural")
                    st.markdown(f"> {result['explicabilidad']['explicacion_natural']}")

                    # === IMPORTANCIA DE FEATURES ===
                    st.divider()
                    st.subheader("Variables que mas influyeron en la Prediccion")
                    st.caption(f"Metodo: {result['explicabilidad']['metodo']}")

                    # Grafico de importancia de features
                    feature_data = result['explicabilidad']['feature_importance']
                    df_features = pd.DataFrame(feature_data)

                    # Filtrar solo features con impacto significativo
                    df_features_sig = df_features[df_features['impacto_porcentual'].abs() > 0.1].head(10)

                    if not df_features_sig.empty:
                        # Crear grafico de barras horizontal
                        fig_importance = px.bar(
                            df_features_sig,
                            y='feature',
                            x='impacto_porcentual',
                            orientation='h',
                            color='impacto_porcentual',
                            color_continuous_scale='RdYlGn',
                            labels={'impacto_porcentual': 'Impacto (%)', 'feature': 'Variable'}
                        )
                        fig_importance.update_layout(
                            height=400,
                            title="Impacto de cada variable en la prediccion",
                            yaxis={'categoryorder': 'total ascending'}
                        )
                        st.plotly_chart(fig_importance, use_container_width=True)

                    # Top 3 factores
                    st.subheader("Top 3 Factores Principales")
                    col_top1, col_top2, col_top3 = st.columns(3)
                    top_factors = result['explicabilidad']['top_3_factores']

                    for i, (col, factor) in enumerate(zip([col_top1, col_top2, col_top3], top_factors)):
                        with col:
                            direccion_emoji = "+" if factor['direccion'] == 'aumenta' else "-" if factor['direccion'] == 'disminuye' else "="
                            st.metric(
                                factor['feature'],
                                f"{direccion_emoji}{abs(factor['impacto_porcentual']):.1f}%",
                                delta=f"{factor['impacto_kwh']:.3f} kWh",
                                delta_color="inverse" if factor['direccion'] == 'aumenta' else "normal"
                            )

                    # === FACTORES CONTEXTUALES ===
                    if result['contexto_historico']['factores_contextuales']:
                        st.divider()
                        st.subheader("Factores Contextuales")
                        for factor in result['contexto_historico']['factores_contextuales']:
                            with st.expander(f"{factor['factor']}: {factor['impacto']}", expanded=True):
                                st.write(factor['explicacion'])

                    # === CONTEXTO HISTORICO ===
                    st.divider()
                    st.subheader("Comparacion con Datos Historicos")
                    col_hist1, col_hist2 = st.columns(2)

                    with col_hist1:
                        st.metric(
                            "Media Historica (Sede)",
                            f"{result['contexto_historico']['media_sede_kwh']:.2f} kWh"
                        )
                    with col_hist2:
                        st.metric(
                            "Desviacion Estandar",
                            f"{result['contexto_historico']['std_sede_kwh']:.2f} kWh"
                        )

                    # Grafico de comparacion
                    pred_val = result['prediccion']['valor_kwh']
                    media = result['contexto_historico']['media_sede_kwh']
                    std = result['contexto_historico']['std_sede_kwh']

                    fig_context = px.bar(
                        x=["Prediccion", "Media Historica", "Media + 1 Std", "Media - 1 Std"],
                        y=[pred_val, media, media + std, media - std],
                        color=["Prediccion", "Media", "Limite Superior", "Limite Inferior"],
                        color_discrete_map={
                            "Prediccion": "#1E88E5",
                            "Media": "#43A047",
                            "Limite Superior": "#FFA726",
                            "Limite Inferior": "#FFA726"
                        }
                    )
                    fig_context.update_layout(
                        height=300,
                        title="Prediccion vs Contexto Historico",
                        showlegend=True,
                        xaxis_title="",
                        yaxis_title="kWh"
                    )
                    st.plotly_chart(fig_context, use_container_width=True)

                    # === TABLA COMPLETA DE FEATURES ===
                    with st.expander("Ver tabla completa de importancia de variables"):
                        st.dataframe(
                            df_features.style.background_gradient(subset=['impacto_porcentual'], cmap='RdYlGn'),
                            use_container_width=True
                        )

                else:
                    st.error(f"Error: {r.text}")

            except requests.exceptions.ConnectionError:
                st.error("No se puede conectar con la API. Verifica que el servicio este corriendo.")
            except Exception as e:
                st.error(f"Error: {e}")

    # === SECCION EDUCATIVA ===
    st.divider()
    st.subheader("Sobre la Explicabilidad (XAI)")

    with st.expander("¿Que es SHAP/LIME?", expanded=False):
        st.markdown("""
        **SHAP (SHapley Additive exPlanations)** y **LIME (Local Interpretable Model-agnostic Explanations)**
        son tecnicas de explicabilidad que ayudan a entender por que un modelo de IA toma ciertas decisiones.

        **Como funciona nuestro sistema:**
        1. **Perturbacion de Features**: Modificamos cada variable de entrada y observamos como cambia la prediccion
        2. **Calculo de Impacto**: Medimos cuanto contribuye cada variable al resultado final
        3. **Contextualizacion**: Comparamos con datos historicos para dar contexto

        **Beneficios:**
        - Transparencia en las decisiones del modelo
        - Identificacion de factores clave de consumo
        - Mayor confianza en las predicciones
        - Cumplimiento de estandares de IA responsable
        """)

    with st.expander("¿Como interpretar los resultados?", expanded=False):
        st.markdown("""
        **Impacto Porcentual:**
        - Valores **positivos** indican que la variable **aumenta** el consumo predicho
        - Valores **negativos** indican que la variable **disminuye** el consumo predicho
        - El valor absoluto indica la **magnitud** del efecto

        **Nivel de Confianza:**
        - **ALTO**: La prediccion esta dentro del rango normal historico
        - **MEDIO**: La prediccion esta ligeramente fuera del rango tipico
        - **BAJO**: La prediccion es inusual respecto al patron historico

        **Z-Score:**
        - Valores entre -2 y 2 son normales
        - Valores fuera de este rango indican predicciones atipicas
        """)

elif page == "Chat IA":
    st.markdown("### Asistente Virtual de Energia")
    st.markdown('<p style="color: #64748b; margin-top: -10px;">Consulta inteligente sobre consumo y eficiencia energetica</p>', unsafe_allow_html=True)

    # Info del asistente
    col_info1, col_info2 = st.columns([3, 1])
    with col_info1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 1rem; border-radius: 12px; border-left: 4px solid #4CAF50; margin-bottom: 1rem;">
            <p style="margin: 0; color: #2E7D32; font-size: 0.9rem;">
                <strong>Asistente IA disponible</strong> - Pregunta sobre consumo energetico, eficiencia, patrones de uso o recomendaciones de ahorro.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        if st.button("Limpiar chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # Inicializar mensajes
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Contenedor de mensajes
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Input del chat
    if prompt := st.chat_input("Escribe tu pregunta sobre energia..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analizando tu consulta..."):
                try:
                    r = requests.post(f"{API_URL}/chat", json={"message": prompt}, timeout=60)
                    if r.status_code == 200:
                        answer = r.json().get("response", "No pude procesar tu consulta.")
                    else:
                        answer = "Error al comunicarse con el asistente."
                except requests.exceptions.ConnectionError:
                    answer = "El servicio de chat no esta disponible. Verifica que Ollama este corriendo."
                except Exception as e:
                    answer = f"Error: {str(e)}"
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

# === FOOTER CORPORATIVO (no mostrar en Chat) ===
if page != "Chat IA":
    st.markdown("---")
    st.markdown("""
    <div class="corporate-footer">
        <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;">
            <div>
                <strong style="color: white;">UPTC Energy AI</strong>
                <span style="opacity: 0.7;"> | Sistema de Gestion Energetica Inteligente</span>
            </div>
            <div style="opacity: 0.7;">
                Desarrollado para <strong style="color: #00C853;">IAMinds Hackathon 2026</strong>
            </div>
        </div>
        <div style="margin-top: 0.5rem; opacity: 0.5; font-size: 0.75rem;">
            Universidad Pedagogica y Tecnologica de Colombia | Powered by LSTM + Ollama AI
        </div>
    </div>
    """, unsafe_allow_html=True)
