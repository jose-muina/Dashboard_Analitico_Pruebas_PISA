import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# CONFIGURACION GENERAL

st.set_page_config(page_title="Dashboard PISA Argentina", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-size: 18px; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

COLOR_NORMAL = "#2a6fb0"   # estratos con suficientes escuelas
COLOR_FRAGIL = "#e08a1e"   # estratos con pocas escuelas
NOMBRES_TERCIL = {"Bajo": "Menores recursos", "Medio": "Recursos medios", "Alto": "Mayores recursos"}
KPI_AZUL = "#4a90d9"   # indicadores informativos
KPI_ROJO = "#e5484d"   # indicador de alerta
KPI_GRIS = "#8a8a8a"   # dato de la muestra
UMBRAL_NIVEL2 = 420        # solo para el texto; la variable ya esta calculada



# DATOS Y FUNCIONES AUXILIARES

def cargar_datos():
    df = pd.read_csv("Dataset_procesado.csv", sep=";")  
    # Al leer el CSV se pierde el orden de los grupos, se define de vuelta
    df["tercil_nse"] = pd.Categorical(
        df["tercil_nse"], categories=["Bajo", "Medio", "Alto"], ordered=True
    )
    df["bajo_f"] = df["bajo_nivel2"].astype(float)  # 1 si esta bajo Nivel 2, 0 si no
    return df


def promedio_ponderado(valores, pesos):
    # Promedio donde cada estudiante cuenta segun su peso, ignorando faltantes
    ok = valores.notna()
    return np.average(valores[ok], weights=pesos[ok])


def promedio_por_grupo(d, grupo, col):
    # Promedio ponderado de una columna para cada grupo
    t = d.dropna(subset=[col, grupo]).copy()
    t["_wx"] = t[col] * t["peso"]
    g = t.groupby(grupo, observed=True).agg(wx=("_wx", "sum"), w=("peso", "sum"))
    return g["wx"] / g["w"]


def miles(n):
    # 11092 -> "11.092"
    return f"{n:,.0f}".replace(",", ".")


df = cargar_datos()

# Cantidad de escuelas de cada estrato (sobre todo el dataset)
esc_por_estrato = df.groupby("estrato")["id_escuela"].nunique()
fragil_por_estrato = df.groupby("estrato")["estrato_fragil"].first()


def etiqueta(estrato):
    marca = "*" if fragil_por_estrato[estrato] else ""
    return f"{estrato} ({esc_por_estrato[estrato]} esc.){marca}"


# ENCABEZADO Y SELECTOR DE MATERIA

st.markdown("## 📊 Como les fue a los estudiantes argentinos en las prueba PISA 2025")
st.markdown(
    "PISA es una prueba internacional que mide lo que saben estudiantes de 15 años. "
    "Mas puntos, suponen un mejor desempeño."
)

materia = st.radio("Elegi la materia que queres ver", ["Matematica", "Lectura"], horizontal=True)
col = materia.lower()


# FILTROS (barra lateral): afectan al ranking y al detalle, no a los KPIs

st.sidebar.header("Filtros")
st.sidebar.caption("Estos filtros afectan al ranking por estrato y al detalle. Los indicadores de arriba son nacionales.")
estratos_sel = st.sidebar.multiselect(
    "Estratos", sorted(df["estrato"].unique()), default=sorted(df["estrato"].unique())
)
ocultar_fragiles = st.sidebar.checkbox("Ocultar estratos con pocas escuelas (menos de 10)")

df_f = df[df["estrato"].isin(estratos_sel)]
if ocultar_fragiles:
    df_f = df_f[~df_f["estrato_fragil"]]


# CALCULOS NACIONALES (para resumen y KPIs)

prom_nacional = promedio_ponderado(df[col], df["peso"])
pct_bajo = promedio_ponderado(df["bajo_f"], df["peso"]) * 100
prom_tercil = promedio_por_grupo(df, "tercil_nse", col)
brecha = prom_tercil["Alto"] - prom_tercil["Bajo"]

prom_estrato = promedio_por_grupo(df[~df["estrato_fragil"]], "estrato", col)


# RESUMEN EN 3 FRASES (se calcula con los datos)

st.markdown("### Lo principal en tres frases")
st.markdown(
    f"- En matematica, unos **{pct_bajo:.0f} de cada 100** estudiantes no alcanzan el nivel basico.\n"
    f"- En {materia.lower()}, los estudiantes que provienen de familias con **mayores recursos** sacan "
    f"en promedio **{brecha:.0f} puntos mas** que aquellos que poseen menores recursos.\n"
    f"- Entre las estratos con suficientes escuelas evaluadas, el promedio en {materia.lower()} va de "
    f"**{prom_estrato.min():.0f}** a **{prom_estrato.max():.0f}** puntos."
)


# KPIs

def tarjeta(columna, titulo, valor, color):
    
    columna.markdown(
        f"""
        <div style="border-left: 6px solid {color}; background: {color}22;
                    padding: 12px 16px; border-radius: 6px;">
            <div style="font-size: 16px; opacity: 0.85;">{titulo}</div>
            <div style="font-size: 38px; font-weight: 600; color: {color};">{valor}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


c1, c2, c3, c4 = st.columns(4)
tarjeta(c1, f"Puntaje promedio en {materia.lower()}", f"{prom_nacional:.0f}", KPI_AZUL)
tarjeta(c2, "No alcanzan lo basico (matematica)", f"{pct_bajo:.0f}%", KPI_ROJO)
tarjeta(c3, "Diferencia por origen social", f"{brecha:.0f} puntos", KPI_AZUL)
tarjeta(c4, f"Estudiantes en {miles(df['id_escuela'].nunique())} escuelas", miles(len(df)), KPI_GRIS)

st.caption("Nivel basico: 420 puntos o mas (Nivel 2 de PISA, valor de referencia aproximado).")

# GRAFICO 1: BARRAS POR TERCIO DE RECURSOS

st.markdown("---")
st.markdown("### A mayores recursos familiares, mayores puntajes")
datos_t = prom_tercil.reset_index()
datos_t.columns = ["tercil", "puntaje"]
datos_t["Grupo"] = datos_t["tercil"].astype(str).map(NOMBRES_TERCIL)

fig1 = px.bar(datos_t, x="Grupo", y="puntaje", text=datos_t["puntaje"].round(0).astype(int))
fig1.update_traces(marker_color=COLOR_NORMAL, textposition="outside")
fig1.update_layout(hovermode=False)
fig1.update_layout(
    yaxis_title=f"Puntaje promedio en {materia.lower()}", xaxis_title="", font_size=16,
    yaxis_range=[0, datos_t["puntaje"].max() * 1.15],
)
st.plotly_chart(fig1, width="stretch")
st.caption(
    "Como leerlo: se ordena a los estudiantes segun el nivel socioeconomico de su familia y se los divide "
    "en tres grupos iguales. Cada barra es el puntaje promedio de un grupo."
)


# GRAFICO 2: RANKING POR ESTRATO

st.markdown("---")
st.markdown("### Hay diferencias grandes entre estratos")
if df_f.empty:
    st.info("No hay estratos seleccionadas. Elegi al menos una en la barra lateral.")
    st.stop()

rank = promedio_por_grupo(df_f, "estrato", col).sort_values(ascending=False).reset_index()
rank.columns = ["estrato", "puntaje"]
rank["Estrato"] = rank["estrato"].map(etiqueta)
rank["Escuelas evaluadas"] = rank["estrato"].map(
    lambda e: "Pocas escuelas (tomar con cuidado)" if fragil_por_estrato[e] else "Suficientes escuelas"
)

fig2 = px.bar(
    rank, x="puntaje", y="Estrato", orientation="h", color="Escuelas evaluadas",
    color_discrete_map={"Suficientes escuelas": COLOR_NORMAL, "Pocas escuelas (tomar con cuidado)": COLOR_FRAGIL},
    text=rank["puntaje"].round(0).astype(int),
)
fig2.update_yaxes(autorange="reversed", title="")
fig2.update_layout(hovermode=False)
fig2.update_layout(xaxis_title=f"Puntaje promedio en {materia.lower()}", font_size=16, height=max(350, 32 * len(rank)))
st.plotly_chart(fig2, width="stretch")
st.caption(
    "Como leerlo: cada barra es un estrato (un grupo de escuelas del estudio), de mayor a menor puntaje. "
    "Entre parentesis se indica cuantas escuelas se evaluaron. Las barras naranjas (*) tienen muy pocas "
    "escuelas: sus resultados son poco estables."
)


# DETALLE (desplegable)

with st.expander("🔍 Ver mas detalle"):
    st.markdown("#### Como se distribuyen los resultados dentro de cada estrato")
    df_b = df_f.copy()
    df_b["Estrato"] = df_b["estrato"].map(etiqueta)
    orden = rank["Estrato"].tolist()
    df_b["Escuelas evaluadas"] = df_b["estrato"].map(
        lambda e: "Pocas escuelas (tomar con cuidado)" if fragil_por_estrato[e] else "Suficientes escuelas"
    )
    fig3 = px.box(
        df_b, x="Estrato", y=col, color="Escuelas evaluadas", category_orders={"Estrato": orden},
        color_discrete_map={"Suficientes escuelas": COLOR_NORMAL, "Pocas escuelas (tomar con cuidado)": COLOR_FRAGIL},
    )
    fig3.update_layout(yaxis_title=f"Puntaje en {materia.lower()}", xaxis_title="", font_size=14)
    fig3.update_layout(hovermode=False)
    st.plotly_chart(fig3, width="stretch")
    st.caption(
        "Como leerlo: la caja contiene a la mitad de los estudiantes del estrato y la linea del medio es el "
"valor tipico. Las rayitas muestran hasta donde llegan los resultados habituales y cada punto suelto es "
"un estudiante con un puntaje poco frecuente para su estrato. Este grafico usa a los estudiantes de la "
"muestra, sin ajustar por el peso de cada uno el orden de los estratos si usa el promedio ajustado."
    )

    st.markdown("#### El puntaje segun los recursos de la familia, en mas detalle")
    df_n = df.dropna(subset=["nse"]).copy()
    df_n["decil"] = pd.qcut(df_n["nse"], q=10, labels=range(1, 11))  # 10 grupos iguales
    por_decil = promedio_por_grupo(df_n, "decil", col).reset_index()
    por_decil.columns = ["decil", "puntaje"]
    por_decil["decil"] = por_decil["decil"].astype(int)

    fig4 = px.line(
        por_decil, x="decil", y="puntaje", markers=True,
        text=por_decil["puntaje"].round(0).astype(int),
    )
    fig4.update_traces(line_color=COLOR_NORMAL, textposition="top center")
    fig4.update_layout(hovermode=False)
    fig4.update_xaxes(dtick=1)
    fig4.update_layout(
        xaxis_title="Grupo de recursos familiares (1 = menores recursos, 10 = mayores recursos)",
        yaxis_title=f"Puntaje promedio en {materia.lower()}", font_size=14,
    )
    st.plotly_chart(fig4, width="stretch")
    st.caption(
        "Como leerlo: se ordena a todos los estudiantes del pais segun los recursos de su familia y se los "
        "divide en 10 grupos iguales. Cada punto es el puntaje promedio de un grupo. Este grafico no cambia "
        "con los filtros de la barra lateral."
    )

    st.markdown("#### Tabla por estrato")
    tabla = pd.DataFrame({
        "Estrato": rank["estrato"],
        "Escuelas": rank["estrato"].map(esc_por_estrato),
        "Estudiantes": rank["estrato"].map(df.groupby("estrato")["id_estudiante"].count()),
        f"Puntaje {materia.lower()}": rank["puntaje"].round(0).astype(int),
        "No alcanzan lo basico, matematica (%)": rank["estrato"].map(
            promedio_por_grupo(df_f, "estrato", "bajo_f") * 100
        ).round(0).astype(int),
        "Pocas escuelas": rank["estrato"].map(lambda e: "Si" if fragil_por_estrato[e] else "No"),
    })
    st.dataframe(tabla, width="stretch", hide_index=True)


# NOTAS METODOLOGICAS

with st.expander("📝 Notas metodologicas"):
    st.markdown(
        "- **Ajuste por peso:** los promedios usan el peso de cada estudiante, de modo que representan a la "
        "poblacion y no solo a la muestra.\n"
        "- **Un solo valor plausible:** se usa un unico valor plausible de PISA por materia, por lo que los "
        "resultados son estimaciones puntuales, sin margen de error.\n"
        "- **Estratos:** los estratos (ARG01 a ARG20) no son provincias, equivalen a agrupaciones de escuelas con "   
        "caracteristicas similares. Algunos tienen muy pocas escuelas; se marcan con * cuando son menos de 10.\n"
        f"- **Nivel basico:** se toma {UMBRAL_NIVEL2} puntos en matematica como piso de competencia basica "
        "(Nivel 2 de PISA, valor de referencia aproximado).\n"
        "- **Nivel socioeconomico:** los tercios se calcularon sin ajustar por peso y aproximadamente un 11% de los estudiantes "
        "no tiene dato, por lo que no entra en esos calculos.\n"
        "- **Alcance:** el analisis describe diferencias, no prueba causas."
    )


# ANEXO: GESTION SINTETICA (aislado: ningun otro bloque la usa)

if "gestion" in df.columns:
    with st.expander("🧪 Anexo: comparacion por tipo de gestion (datos sinteticos)"):
        st.warning(
            "La variable de gestion (publica o privada) es SINTETICA: se asigno al azar y no refleja la "
            "realidad. Este grafico es solo una demostracion tecnica y no permite sacar conclusiones reales."
        )
        g = promedio_por_grupo(df, "gestion", col).reset_index()
        g.columns = ["Gestion", "puntaje"]
        g["Escuelas"] = g["Gestion"].map(df.groupby("gestion")["id_escuela"].nunique())
        g["Gestion"] = g["Gestion"] + " (sintetico, " + g["Escuelas"].astype(str) + " escuelas)"
        fig5 = px.bar(g, x="Gestion", y="puntaje", text=g["puntaje"].round(0).astype(int))
        fig5.update_traces(marker_color="#8a8a8a", textposition="outside")
        fig5.update_layout(hovermode=False)
        fig5.update_layout(
            yaxis_title=f"Puntaje promedio en {materia.lower()}", xaxis_title="", font_size=16,
            yaxis_range=[0, g["puntaje"].max() * 1.15],
        )
        st.plotly_chart(fig5, width="stretch")
        st.caption(
            "Las barras son casi iguales, lo esperable en una variable asignada al azar: cualquier diferencia "
            "sale del sorteo y no refleja la realidad."
        )