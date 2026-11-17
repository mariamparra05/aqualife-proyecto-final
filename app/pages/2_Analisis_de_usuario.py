from datetime import date
import pandas as pd
import streamlit as st
from db import call_procedure, run_query, nativo

st.set_page_config(page_title="Análisis de usuario", layout="wide")
st.title("Análisis de usuario")
st.caption("Usa el procedimiento almacenado sp_analisis_usuario")

c1, c2, c3 = st.columns(3)
uid = c1.number_input("ID de usuario", min_value=1, value=1, step=1)
ini = c2.date_input("Fecha inicial", value=date(2021, 1, 1))
fin = c3.date_input("Fecha final", value=date.today())

if st.button("Analizar", type="primary"):
    if ini > fin:
        st.error("La fecha inicial no puede ser mayor que la final")
    else:
        try:
            u = run_query("SELECT Nombre, Email FROM Usuario WHERE IDU = %s", (int(uid),))
            res = call_procedure("sp_analisis_usuario", (int(uid), ini, fin))
            if u:
                st.subheader(f"{u[0]['Nombre']}  ·  {u[0]['Email']}")
            if not res or not res[0]:
                st.info("Sin resultados")
            else:
                m = {k: nativo(v) for k, v in res[0][0].items()}
                items = list(m.items())
                for i in range(0, len(items), 4):
                    fila = st.columns(4)
                    for col, (k, v) in zip(fila, items[i:i + 4]):
                        etiqueta = "".join(" " + ch.lower() if ch.isupper() else ch for ch in k).strip().capitalize()
                        col.metric(etiqueta, f"{v:,.2f}" if isinstance(v, float) else v)
                st.subheader("Reacciones dadas y recibidas")
                st.bar_chart(pd.DataFrame({"cantidad": [m["ReaccionesDadas"], m["ReaccionesRecibidas"]]}, index=["Dadas", "Recibidas"]))
                if len(res) > 1 and res[1]:
                    st.subheader("Especies destacadas")
                    esp = res[1][0]
                    a, b = st.columns(2)
                    a.metric("Especie más comprada", esp["EspecieMasComprada"] or "Sin compras")
                    b.metric("Especie más contribuida", esp["EspecieMasContribuida"] or "Sin contribuciones")
        except Exception as e:
            st.error(f"No se pudo ejecutar el análisis: {e}")
