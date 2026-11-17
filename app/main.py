import streamlit as st
from db import run_query, get_mongo_db, get_neo4j_driver

st.set_page_config(page_title="AquaLife - Panel de control", page_icon="🐠", layout="wide")
st.title("🐠 AquaLife - Panel de control")
st.write("Herramienta para los directivos de AquaSolutions y la comunidad de AquaLife. Usa el menú lateral:")
st.markdown(
    "- **Selector de consultas:** ejecuta las consultas analíticas (tareas 3.a a 3.i).\n"
    "- **Análisis de usuario:** perfil de actividad de un acuarista con el procedimiento `sp_analisis_usuario`.\n"
    "- **Gestión de conversaciones:** hilos de comentarios (MySQL y Neo4j) y respuestas.\n"
    "- **Explorador de documentos:** ficha de especie y documentos secundarios (MongoDB).\n"
    "- **Gestor de precios:** cambio de precios y auditoría con trigger.")

st.subheader("Estado de las conexiones")
if st.button("Probar conexiones"):
    try:
        run_query("SELECT 1 AS ok")
        st.success("MySQL conectado")
    except Exception as e:
        st.error(f"MySQL: {e}")
    try:
        get_mongo_db().command("ping")
        st.success("MongoDB conectado")
    except Exception as e:
        st.error(f"MongoDB: {e}")
    try:
        get_neo4j_driver().verify_connectivity()
        st.success("Neo4j conectado")
    except Exception as e:
        st.error(f"Neo4j: {e}")
