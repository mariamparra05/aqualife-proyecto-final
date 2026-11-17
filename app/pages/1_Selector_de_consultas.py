from pathlib import Path
import pandas as pd
import streamlit as st
from db import run_query, nativo

st.set_page_config(page_title="Selector de consultas", layout="wide")
st.title("Selector de consultas")

CARPETA = Path(__file__).resolve().parents[2] / "sql" / "01_consultas"
ETIQUETAS = {
    "3a": "3.a Termómetro de la comunidad (reacciones por publicación)",
    "3b": "3.b Publicaciones mejor recibidas",
    "3c": "3.c Perfil demográfico (rangos de edad)",
    "3d": "3.d Tendencias de contribución según el tipo de agua",
    "3e": "3.e Vendedores mejor calificados",
    "3h": "3.h Influencers e impacto en ventas",
    "3i": "3.i Vendedores con comportamiento anómalo",
}
archivos = {f.stem: f for f in sorted(CARPETA.glob("*.sql"))}
if not archivos:
    st.warning(f"No hay consultas en {CARPETA}")
    st.stop()

def etiqueta(stem):
    return ETIQUETAS.get(stem.split("_")[0], stem)

stem = st.selectbox("Elige una consulta", list(archivos), format_func=etiqueta)
sql = archivos[stem].read_text(encoding="utf-8")
with st.expander("Ver el SQL"):
    st.code(sql, language="sql")

if st.button("Ejecutar consulta", type="primary"):
    try:
        with st.spinner("Ejecutando consulta..."):
            filas = run_query(sql)
        st.session_state["sel_resultado"] = (stem, pd.DataFrame([{k: nativo(v) for k, v in f.items()} for f in filas]))
    except Exception as e:
        st.session_state.pop("sel_resultado", None)
        st.error(f"No se pudo ejecutar la consulta: {e}")

res = st.session_state.get("sel_resultado")
if res and res[0] == stem:
    df = res[1]
    st.success(f"{len(df)} filas")
    if df.empty:
        st.info("La consulta no devolvió filas (¿se cargaron los scripts de la carpeta sql/?)")
    else:
        st.dataframe(df)
        st.download_button("Descargar CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{stem}.csv", mime="text/csv")
        if {"Puntaje", "IncrementoVentasPct"} <= set(df.columns) and df["IncrementoVentasPct"].notna().sum() >= 3:
            r = df["Puntaje"].astype(float).corr(df["IncrementoVentasPct"].astype(float))
            st.metric("Correlación de Pearson (puntaje vs incremento de ventas)", f"{r:.2f}")
            st.caption("Calculada sobre solo 5 influencers: es una indicación, no una prueba estadística.")
