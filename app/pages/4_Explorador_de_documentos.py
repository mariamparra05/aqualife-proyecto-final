import streamlit as st
from documentos import get_documentos_especie, listar_especies_con_ficha, NOMBRES_TIPO

st.set_page_config(page_title="Explorador de documentos", layout="wide")
st.title("Explorador de documentos")
st.caption("Ficha de especie y documentos secundarios (MongoDB)")

try:
    especies = listar_especies_con_ficha()
except Exception as e:
    st.error(f"No se pudo consultar las fichas: {e}")
    st.stop()
if not especies:
    st.info("Aún no hay fichas. Ejecuta: python nosql/documentos_mongo/cargar_fichas.py")
    st.stop()

opciones = {f"{e['NombreComun']} ({e['Categoria']}) #{e['IDProd']}": e["IDProd"] for e in especies}
elegida = st.selectbox("Selecciona una especie", list(opciones))
try:
    doc = get_documentos_especie(opciones[elegida])
except Exception as e:
    st.error(f"No se pudo leer la ficha: {e}")
    st.stop()
if not doc:
    st.info("Esta especie no tiene ficha")
    st.stop()

st.header(doc["nombre_comun"])
st.caption(f"{doc['nombre_cientifico']}  ·  {doc['categoria']}  ·  {doc['tipo_agua']}")
st.subheader("Ficha de especie")
a, b, c = st.columns(3)
req = doc.get("requisitos", {})
a.metric("Temperatura (°C)", f"{req.get('temperatura_c', {}).get('min', '?')} - {req.get('temperatura_c', {}).get('max', '?')}")
b.metric("pH", f"{req.get('ph', {}).get('min', '?')} - {req.get('ph', {}).get('max', '?')}")
c.metric("Tanque mínimo (L)", req.get("litros_minimos_tanque", "?"))
st.write(f"**Sustrato:** {doc['tipo_sustrato']}  ·  **Temporada:** {doc['temporada']}")
st.write(f"**Cuidados específicos:** {doc['cuidados_especificos']}")

st.subheader("Documentos secundarios")
secundarios = doc.get("documentos_secundarios", [])
if not secundarios:
    st.info("Sin documentos secundarios")
else:
    pestanas = st.tabs([NOMBRES_TIPO.get(d["tipo"], d["tipo"]) for d in secundarios])
    for pestana, d in zip(pestanas, secundarios):
        with pestana:
            st.json({k: v for k, v in d.items() if k != "tipo"})
