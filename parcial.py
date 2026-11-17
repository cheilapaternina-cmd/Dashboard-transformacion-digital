"""
Dashboard de indicadores clave de desempeño (KPI)
Estudio de caso: Transformación digital
Industrias Metalmecánicas del Caribe S.A.S. vs. SmartFlow Logistics S.A.S.

Datos: tablas "Indicadores actuales de la empresa" del Caso 1 y del Caso 2 del parcial.
Ejecutar localmente:  streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Dashboard KPI | Transformación digital", page_icon="📊", layout="wide")

AZUL, VERDE, GRIS = "#2563EB", "#16A34A", "#9CA3AF"
EMP1, EMP2 = "Industrias Metalmecánicas del Caribe", "SmartFlow Logistics"
NIVELES = {"Bajo": 1, "Medio": 2, "Alto": 3}

# ---------------------------------------------------------------------------
# Datos del parcial
# Conversiones para graficar: 5 minutos = 5/60 horas; tiempo real = 0 días.
# ---------------------------------------------------------------------------
DATOS_PARCIAL = pd.DataFrame({
    "Indicador": ["Productividad promedio", "Tiempo promedio de respuesta a clientes", "Nivel de automatización",
                  "Satisfacción del cliente", "Tiempo de generación de reportes", "Cumplimiento de entregas"],
    "Unidad": ["%", "horas", "%", "/100", "días", "%"],
    "Sentido": ["Mayor es mejor", "Menor es mejor", "Mayor es mejor", "Mayor es mejor", "Menor es mejor", "Mayor es mejor"],
    EMP1: [68.0, 48.0, 25.0, 70.0, 5.0, 72.0],
    EMP2: [92.0, 5 / 60, 85.0, 94.0, 0.0, 97.0],
})
USO_DATOS_PARCIAL = {EMP1: "Bajo", EMP2: "Alto"}


def texto(valor, unidad):
    """Muestra el valor como aparece en el parcial."""
    if unidad == "%":
        return f"{valor:.0f}%"
    if unidad == "/100":
        return f"{valor:.0f}/100"
    if unidad == "horas":
        return f"{valor * 60:.0f} minutos" if valor < 1 else f"{valor:g} horas"
    if unidad == "días":
        return "Tiempo real" if valor == 0 else f"{valor:g} días"
    return str(valor)


# ---------------------------------------------------------------------------
# Barra lateral: filtro y registro de nuevos valores (monitoreo)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Opciones")
    empresa = st.radio("Empresa a monitorear", [EMP1, EMP2], index=0)
    otra = EMP2 if empresa == EMP1 else EMP1
    mostrar_otra = st.checkbox(f"Comparar con {otra}", value=True)
    

st.title("📊 Dashboard de indicadores clave de desempeño")
st.markdown(f"Transformación digital · **{EMP1} S.A.S.** vs. **{EMP2} S.A.S.**")

with st.expander("✏️ Actualizar valores de los indicadores (monitoreo de un nuevo período)"):
    st.caption("Los valores iniciales son los del parcial. Si la empresa mide nuevos resultados, se escriben aquí "
               "y todo el tablero se recalcula.")
    editado = st.data_editor(
        DATOS_PARCIAL,
        hide_index=True,
        width="stretch",
        disabled=["Indicador", "Unidad", "Sentido"],
        column_config={
            EMP1: st.column_config.NumberColumn(EMP1, min_value=0.0, format="%.2f"),
            EMP2: st.column_config.NumberColumn(EMP2, min_value=0.0, format="%.2f"),
        },
    )
    c_a, c_b = st.columns(2)
    uso = {
        EMP1: c_a.selectbox(f"Uso de datos para decisiones – {EMP1}", list(NIVELES), index=0),
        EMP2: c_b.selectbox(f"Uso de datos para decisiones – {EMP2}", list(NIVELES), index=2),
    }

df = editado.copy()
df["Brecha"] = (df[EMP2] - df[EMP1]).abs()


def mejor(r):
    if r[EMP1] == r[EMP2]:
        return "Igual"
    gana_1 = r[EMP1] > r[EMP2] if r["Sentido"] == "Mayor es mejor" else r[EMP1] < r[EMP2]
    return EMP1 if gana_1 else EMP2


df["Mejor desempeño"] = df.apply(mejor, axis=1)
color_emp = {EMP1: AZUL, EMP2: VERDE}

# ---------------------------------------------------------------------------
# 1. Tarjetas de indicadores
# ---------------------------------------------------------------------------
st.subheader(f"1. Indicadores de {empresa}")
orden = ["Productividad promedio", "Tiempo promedio de respuesta a clientes", "Nivel de automatización",
         "Satisfacción del cliente", "Tiempo de generación de reportes", "Cumplimiento de entregas"]
filas = [orden[:4], orden[4:] + ["Uso de datos para decisiones"]]
for grupo in filas:
    cols = st.columns(4)
    for col, ind in zip(cols, grupo):
        if ind == "Uso de datos para decisiones":
            dif = NIVELES[uso[empresa]] - NIVELES[uso[otra]]
            col.metric(ind, uso[empresa],
                       delta=f"{otra.split()[0]}: {uso[otra]}" if mostrar_otra else None,
                       delta_color="off" if dif == 0 else ("normal" if dif > 0 else "inverse"),
                       delta_arrow="off" if dif == 0 else ("up" if dif > 0 else "down"),
                       border=True)
            continue
        r = df.set_index("Indicador").loc[ind]
        delta = None
        if mostrar_otra:
            d = r[empresa] - r[otra]
            if r["Unidad"] in ("%", "/100"):
                delta = f"{d:+.0f} pts vs. {otra.split()[0]}"
            else:
                delta = f"{otra.split()[0]}: {texto(r[otra], r['Unidad'])}"
            mejor_aqui = r["Mejor desempeño"] == empresa
        es_pts = r["Unidad"] in ("%", "/100")
        igual = not mostrar_otra or r["Mejor desempeño"] == "Igual"
        if es_pts:
            color = "off" if igual else "normal"
            flecha = "off" if igual else "auto"
        else:
            color = "off" if igual else ("normal" if mejor_aqui else "inverse")
            flecha = "off" if igual else ("up" if mejor_aqui else "down")
        col.metric(ind, texto(r[empresa], r["Unidad"]), delta=delta, delta_color=color, delta_arrow=flecha, border=True)
    if len(grupo) == 3:
        gana = (df["Mejor desempeño"] == empresa).sum() + (NIVELES[uso[empresa]] > NIVELES[uso[otra]])
        cols[3].metric("Indicadores en que supera a la otra empresa", f"{gana} de 7", border=True)

st.divider()

# ---------------------------------------------------------------------------
# 2. Comparación de indicadores porcentuales y perfil digital
# ---------------------------------------------------------------------------
pct = df[df["Unidad"].isin(["%", "/100"])].copy()
pct["Etiqueta"] = pct["Indicador"].map({"Productividad promedio": "Productividad", "Nivel de automatización": "Automatización",
                                        "Satisfacción del cliente": "Satisfacción (/100)", "Cumplimiento de entregas": "Cumplimiento de entregas"})
empresas = [empresa, otra] if mostrar_otra else [empresa]

c1, c2 = st.columns([3, 2])
with c1:
    st.subheader("2. Comparación de indicadores (escala 0–100)")
    fig = go.Figure()
    for e in empresas:
        fig.add_bar(x=pct["Etiqueta"], y=pct[e], name=e, marker_color=color_emp[e],
                    text=[f"{v:.0f}" for v in pct[e]], textposition="outside")
    fig.update_layout(barmode="group", height=400, xaxis=dict(tickangle=0), yaxis=dict(range=[0, 110], title="Valor"),
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, width="stretch")

with c2:
    st.subheader("3. Perfil de madurez digital")
    radar = go.Figure()
    cat = list(pct["Etiqueta"]) + [pct["Etiqueta"].iloc[0]]
    for e in empresas:
        vals = list(pct[e]) + [pct[e].iloc[0]]
        radar.add_scatterpolar(r=vals, theta=cat, fill="toself", name=e, line_color=color_emp[e], opacity=0.6)
    radar.update_layout(height=400, polar=dict(radialaxis=dict(range=[0, 100])),
                        margin=dict(l=120, r=120, t=30, b=20), legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(radar, width="stretch")

st.divider()

# ---------------------------------------------------------------------------
# 4. Brechas y tiempos
# ---------------------------------------------------------------------------
c3, c4 = st.columns(2)
with c3:
    st.subheader("4. Brecha entre las dos empresas (puntos)")
    br = pct.sort_values("Brecha")
    fig_b = go.Figure(go.Bar(
        y=br["Etiqueta"], x=br["Brecha"], orientation="h",
        marker_color=["#DC2626" if b == br["Brecha"].max() else GRIS for b in br["Brecha"]],
        text=[f"{b:.0f} pts" for b in br["Brecha"]], textposition="outside",
    ))
    fig_b.update_layout(height=360, xaxis=dict(range=[0, br["Brecha"].max() * 1.25 + 1], title="Diferencia en puntos"),
                        margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_b, width="stretch")
    mayor = br.iloc[-1]
    st.caption(f"La mayor brecha está en **{mayor['Indicador'].lower()}** ({mayor['Brecha']:.0f} puntos).")

with c4:
    st.subheader("5. Tiempos de respuesta y de reportes")
    tiempos = df[df["Unidad"].isin(["horas", "días"])]
    ta, tb = st.columns(2)
    for col, (_, r) in zip((ta, tb), tiempos.iterrows()):
        f = go.Figure(go.Bar(
            x=[e.split()[0] for e in empresas], y=[r[e] for e in empresas],
            marker_color=[color_emp[e] for e in empresas],
            text=[texto(r[e], r["Unidad"]) for e in empresas], textposition="outside",
        ))
        f.update_layout(title=dict(text=r["Indicador"].replace("Tiempo promedio de respuesta a clientes", "Respuesta a clientes")
                                   .replace("Tiempo de generación de reportes", "Generación de reportes"), font=dict(size=14)),
                        height=360, yaxis=dict(title=r["Unidad"], range=[0, max(r[EMP1], r[EMP2]) * 1.3 + 0.5]),
                        margin=dict(l=10, r=10, t=40, b=10))
        col.plotly_chart(f, width="stretch")
    st.caption("En los tiempos, un valor menor es mejor.")

st.divider()

# ---------------------------------------------------------------------------
# 6. Tabla comparativa
# ---------------------------------------------------------------------------
st.subheader("6. Tabla comparativa de los 7 indicadores")
tabla = pd.DataFrame({
    "Indicador": df["Indicador"],
    EMP1: [texto(v, u) for v, u in zip(df[EMP1], df["Unidad"])],
    EMP2: [texto(v, u) for v, u in zip(df[EMP2], df["Unidad"])],
    "Brecha": [f"{b:.0f} pts" if u in ("%", "/100") else f"{b:.1f} {u}" for b, u in zip(df["Brecha"], df["Unidad"])],
    "Criterio": df["Sentido"],
    "Mejor desempeño": df["Mejor desempeño"].replace({EMP1: "Metalmecánicas", EMP2: "SmartFlow"}),
})
fila_uso = pd.DataFrame([{
    "Indicador": "Uso de datos para decisiones", EMP1: uso[EMP1], EMP2: uso[EMP2],
    "Brecha": f"{abs(NIVELES[uso[EMP2]] - NIVELES[uso[EMP1]])} nivel(es)", "Criterio": "Mayor es mejor",
    "Mejor desempeño": "Igual" if uso[EMP1] == uso[EMP2] else ("Metalmecánicas" if NIVELES[uso[EMP1]] > NIVELES[uso[EMP2]] else "SmartFlow"),
}])
tabla = pd.concat([tabla.iloc[:2], fila_uso, tabla.iloc[2:]], ignore_index=True)
st.dataframe(tabla, hide_index=True, width="stretch")
st.download_button("⬇️ Descargar tabla (CSV)", tabla.to_csv(index=False).encode("utf-8-sig"),
                   file_name="indicadores_kpi.csv", mime="text/csv")

st.divider()
st.caption("Estudio de caso – Transformación digital.")
