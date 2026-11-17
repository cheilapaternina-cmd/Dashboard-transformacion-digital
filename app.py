"""
Dashboard de indicadores clave de desempeño (KPI)
Estudio de caso: Transformación digital
Industrias Metalmecánicas del Caribe S.A.S. vs. SmartFlow Logistics S.A.S.

Ejecutar localmente:  streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard KPI | Transformación digital",
    page_icon="📊",
    layout="wide",
)

AZUL = "#2563EB"      # Empresa tradicional (actual)
VERDE = "#16A34A"     # SmartFlow (referente digital)
GRIS = "#6B7280"      # Meta
ROJO = "#DC2626"
AMARILLO = "#F59E0B"

# ---------------------------------------------------------------------------
# Datos del caso
# ---------------------------------------------------------------------------
# Indicadores en escala 0-100 (porcentajes o puntos)
kpi = pd.DataFrame(
    {
        "Indicador": [
            "Productividad promedio",
            "Cumplimiento de entregas",
            "Satisfacción del cliente",
            "Nivel de automatización",
        ],
        "Unidad": ["%", "%", "/100", "%"],
        "Metalmecánicas": [68, 72, 70, 25],
        "Meta": [85, 95, 90, 70],
        "SmartFlow": [92, 97, 94, 85],
        # Límites del semáforo: verde >= meta; amarillo >= limite_amarillo; rojo < limite_amarillo
        "Límite amarillo": [70, 75, 75, 35],
    }
)
kpi["Brecha vs. SmartFlow"] = kpi["SmartFlow"] - kpi["Metalmecánicas"]
kpi["Brecha vs. meta"] = kpi["Meta"] - kpi["Metalmecánicas"]

# Indicadores de tiempo (menor es mejor), expresados en horas
tiempos = pd.DataFrame(
    {
        "Indicador": ["Tiempo de respuesta al cliente", "Tiempo de generación de reportes"],
        "Metalmecánicas (h)": [48, 5 * 24],
        "Meta (h)": [4, 24],
        "SmartFlow (h)": [5 / 60, 0],
        "Texto actual": ["48 horas", "5 días"],
        "Texto meta": ["< 4 horas", "1 día"],
        "Texto SmartFlow": ["5 minutos", "Tiempo real"],
    }
)

# Indicador cualitativo
uso_datos = {"Metalmecánicas": "Bajo", "Meta": "Alto", "SmartFlow": "Alto"}
NIVELES = {"Bajo": 1, "Medio": 2, "Alto": 2.5, "Alto": 3}

# Estrategias de transformación (hoja de ruta)
estrategias = pd.DataFrame(
    {
        "Estrategia": [
            "E1. Captura digital en planta",
            "E2. ERP + Power BI",
            "E3. Portal del cliente",
            "E4. Gestión del cambio (ADKAR)",
            "E5. Planta conectada (IoT)",
        ],
        "Inicio": [1, 3, 9, 1, 12],
        "Fin": [4, 12, 15, 18, 18],
        "Indicadores que mejora": [
            "Automatización, reportes, productividad",
            "Uso de datos, reportes, entregas",
            "Tiempo de respuesta, satisfacción",
            "Uso de datos (habilita todas)",
            "Productividad, entregas, automatización",
        ],
    }
)


def semaforo(valor, meta, amarillo):
    if valor >= meta:
        return "🟢 En meta"
    if valor >= amarillo:
        return "🟡 En riesgo"
    return "🔴 Crítico"


kpi["Estado"] = [
    semaforo(v, m, a) for v, m, a in zip(kpi["Metalmecánicas"], kpi["Meta"], kpi["Límite amarillo"])
]

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Opciones")
    vista = st.radio(
        "Vista",
        ["Empresa tradicional vs. meta", "Comparación entre empresas"],
        index=0,
    )
    mostrar_ref = st.checkbox("Mostrar referente SmartFlow", value=True)
    st.divider()
    st.markdown(
        "**Simulador de avance**  \n"
        "Mueve el control para ver cómo cambiarían los indicadores si la empresa "
        "cierra parte de la brecha frente a su meta."
    )
    avance = st.slider("Avance del plan de transformación (%)", 0, 100, 0, step=10)
    st.divider()
    st.caption(
        "Fuente: indicadores del estudio de caso (Caso 1 y Caso 2). "
        "Meta propuesta."
    )

# Valores simulados según el avance del plan
kpi["Simulado"] = kpi["Metalmecánicas"] + (kpi["Meta"] - kpi["Metalmecánicas"]) * avance / 100
kpi["Estado simulado"] = [
    semaforo(v, m, a) for v, m, a in zip(kpi["Simulado"], kpi["Meta"], kpi["Límite amarillo"])
]
col_valor = "Simulado" if avance > 0 else "Metalmecánicas"

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.title("📊 Dashboard de indicadores clave de desempeño")
st.markdown(
    "**Industrias Metalmecánicas del Caribe S.A.S.** · monitoreo de la transformación digital "
    "frente a sus metas y al referente digital **SmartFlow Logistics S.A.S.**"
)
if avance > 0:
    st.info(f"Escenario simulado: el plan de transformación avanza un {avance} % hacia las metas.")

# ---------------------------------------------------------------------------
# Tarjetas KPI
# ---------------------------------------------------------------------------
st.subheader("Resumen de indicadores")
cols = st.columns(4)
for col, (_, r) in zip(cols, kpi.iterrows()):
    valor = r[col_valor]
    col.metric(
        label=r["Indicador"],
        value=f"{valor:.0f}{r['Unidad']}",
        delta=f"{valor - r['Meta']:+.0f} vs. meta ({r['Meta']}{r['Unidad']})",
        delta_color="normal",
        border=True,
    )

cols2 = st.columns(3)
factor = 1 - avance / 100
for col, (_, r) in zip(cols2[:2], tiempos.iterrows()):
    actual_h = r["Meta (h)"] + (r["Metalmecánicas (h)"] - r["Meta (h)"]) * factor
    if avance == 0:
        texto = r["Texto actual"]
    elif actual_h < 24:
        texto = f"{actual_h:.0f} horas"
    else:
        dias = round(actual_h / 24, 1)
        texto = f"{dias:g} día" + ("" if dias == 1 else "s")
    col.metric(
        label=r["Indicador"],
        value=texto,
        delta=f"Meta {r['Texto meta']} · SmartFlow {r['Texto SmartFlow']}",
        delta_color="off",
        delta_arrow="off",
        border=True,
    )
cols2[2].metric(
    label="Uso de datos para decisiones",
    value=uso_datos["Metalmecánicas"] if avance < 50 else ("Medio" if avance < 100 else "Medio-alto"),
    delta=f"Meta {uso_datos['Meta']} · SmartFlow {uso_datos['SmartFlow']}",
    delta_color="off",
    delta_arrow="off",
    border=True,
)

st.divider()

# ---------------------------------------------------------------------------
# Gráfico principal
# ---------------------------------------------------------------------------
izq, der = st.columns([3, 2])

with izq:
    if vista == "Empresa tradicional vs. meta":
        st.subheader("Actual frente a meta y referente")
        orden = kpi.sort_values("Brecha vs. SmartFlow")
        fig = go.Figure()
        fig.add_bar(
            y=orden["Indicador"],
            x=orden[col_valor],
            orientation="h",
            name="Metalmecánicas (actual)" if avance == 0 else "Metalmecánicas (simulado)",
            marker_color=AZUL,
            text=[f"{v:.0f}{u}" for v, u in zip(orden[col_valor], orden["Unidad"])],
            textposition="inside",
            insidetextanchor="end",
            hovertemplate="%{y}: %{x:.0f}<extra></extra>",
        )
        fig.add_scatter(
            y=orden["Indicador"],
            x=orden["Meta"],
            mode="markers",
            name="Meta Propuesta",
            marker=dict(symbol="line-ns", size=28, line=dict(width=4, color=GRIS)),
            hovertemplate="Meta: %{x}<extra></extra>",
        )
        if mostrar_ref:
            fig.add_scatter(
                y=orden["Indicador"],
                x=orden["SmartFlow"],
                mode="markers",
                name="SmartFlow (referente)",
                marker=dict(symbol="diamond", size=13, color=VERDE),
                hovertemplate="SmartFlow: %{x}<extra></extra>",
            )
        fig.update_layout(
            xaxis=dict(range=[0, 100], title="Escala 0–100"),
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=-0.2),
            bargap=0.45,
        )
    else:
        st.subheader("Comparación entre empresas")
        fig = go.Figure()
        fig.add_bar(
            x=kpi["Indicador"], y=kpi["Metalmecánicas"], name="Metalmecánicas del Caribe",
            marker_color=AZUL, text=kpi["Metalmecánicas"], textposition="outside",
        )
        if mostrar_ref:
            fig.add_bar(
                x=kpi["Indicador"], y=kpi["SmartFlow"], name="SmartFlow Logistics",
                marker_color=VERDE, text=kpi["SmartFlow"], textposition="outside",
            )
        fig.update_layout(
            barmode="group",
            yaxis=dict(range=[0, 110], title="Escala 0–100"),
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=-0.25),
        )
    st.plotly_chart(fig, width="stretch")

with der:
    st.subheader("Brecha frente al referente digital")
    brecha = kpi.sort_values("Brecha vs. SmartFlow", ascending=True)
    colores = [ROJO if b == brecha["Brecha vs. SmartFlow"].max() else "#9CA3AF"
               for b in brecha["Brecha vs. SmartFlow"]]
    fig_b = go.Figure(
        go.Bar(
            y=brecha["Indicador"],
            x=brecha["Brecha vs. SmartFlow"],
            orientation="h",
            marker_color=colores,
            text=[f"{b} pts" for b in brecha["Brecha vs. SmartFlow"]],
            textposition="outside",
            hovertemplate="%{y}: %{x} puntos de brecha<extra></extra>",
        )
    )
    fig_b.update_layout(
        xaxis=dict(range=[0, 75], title="Puntos por debajo de SmartFlow"),
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_b, width="stretch")
    st.caption("La automatización es la brecha más grande y la causa raíz de las demás.")

st.divider()

# ---------------------------------------------------------------------------
# Indicadores de tiempo y cultura de datos
# ---------------------------------------------------------------------------
c1, c2 = st.columns(2)
with c1:
    st.subheader("Tiempos de respuesta y reporte (horas, escala log)")
    fig_t = go.Figure()
    fig_t.add_bar(
        x=tiempos["Indicador"], y=tiempos["Metalmecánicas (h)"], name="Metalmecánicas",
        marker_color=AZUL, text=tiempos["Texto actual"], textposition="outside",
    )
    fig_t.add_bar(
        x=tiempos["Indicador"], y=tiempos["Meta (h)"], name="Meta",
        marker_color=GRIS, text=tiempos["Texto meta"], textposition="outside",
    )
    if mostrar_ref:
        fig_t.add_bar(
            x=tiempos["Indicador"], y=[5 / 60, 0.05], name="SmartFlow",
            marker_color=VERDE, text=tiempos["Texto SmartFlow"], textposition="outside",
        )
    fig_t.update_layout(
        barmode="group",
        yaxis=dict(type="log", title="Horas (escala logarítmica)", range=[-1.6, 2.6], dtick=1),
        height=360,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=-0.2),
    )
    st.plotly_chart(fig_t, width="stretch")
    st.caption("SmartFlow responde 576 veces más rápido (5 minutos frente a 48 horas).")

with c2:
    st.subheader("Uso de datos para decisiones")
    fig_g = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=NIVELES[uso_datos["Metalmecánicas"]],
            number=dict(suffix=" / 3", font=dict(size=36)),
            title=dict(text="Nivel actual: <b>Bajo</b>", font=dict(size=16)),
            gauge=dict(
                axis=dict(range=[0, 3], tickvals=[1, 2, 3], ticktext=["Bajo", "Medio", "Alto"]),
                bar=dict(color=AZUL),
                steps=[
                    dict(range=[0, 1.5], color="#FEE2E2"),
                    dict(range=[1.5, 2.5], color="#FEF3C7"),
                    dict(range=[2.5, 3], color="#DCFCE7"),
                ],
                threshold=dict(line=dict(color=VERDE, width=4), value=NIVELES[uso_datos["SmartFlow"]]),
            ),
        )
    )
    fig_g.update_layout(height=360, margin=dict(l=30, r=30, t=60, b=10))
    st.plotly_chart(fig_g, width="stretch")
    st.caption("Línea verde: nivel de SmartFlow (Alto).")

st.divider()

# ---------------------------------------------------------------------------
# Semáforo
# ---------------------------------------------------------------------------
st.subheader("🚦 Semáforo de gestión")
tabla = kpi[["Indicador", "Metalmecánicas", "Meta", "SmartFlow", "Brecha vs. meta", "Estado"]].copy()
if avance > 0:
    tabla.insert(2, "Simulado", kpi["Simulado"].round(0))
    tabla["Estado"] = kpi["Estado simulado"]
st.dataframe(tabla, hide_index=True, width="stretch")
st.caption(
    "Regla: 🟢 valor ≥ meta · 🟡 entre el límite de riesgo y la meta · 🔴 por debajo del límite de riesgo. "
    "Límites de riesgo: productividad 70 %, entregas 75 %, satisfacción 75/100, automatización 35 %."
)

st.divider()
st.caption(
    "Estudio de caso – Transformación digital·)."
)
