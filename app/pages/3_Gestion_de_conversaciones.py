from html import escape
import streamlit as st
from db import run_query
import hilos

st.set_page_config(page_title="Gestión de conversaciones", layout="wide")
st.title("Gestión de conversaciones")

fuente = st.radio("Fuente del hilo", ["MySQL (relacional)", "Neo4j (grafo)"], horizontal=True)
try:
    raices = hilos.listar_raices_con_respuestas()
    usuarios = run_query("SELECT IDU, Nombre FROM Usuario ORDER BY Nombre")
except Exception as e:
    st.error(f"No se pudo leer MySQL: {e}")
    st.stop()

tab_ver, tab_nuevo = st.tabs(["Ver y responder", "Nuevo comentario"])

with tab_ver:
    if not raices:
        st.info("No hay hilos con respuestas. Ejecuta sql/04_hilos_comentarios.sql")
    else:
        opciones = {f"#{r['IDC']} (publicación {r['IDPub']}): {r['Texto']}": r["IDC"] for r in raices}
        raiz = opciones[st.selectbox("Hilo (comentario inicial)", list(opciones))]
        try:
            if fuente.startswith("Neo4j"):
                filas = hilos.get_hilo_neo4j(raiz)
                if not filas:
                    st.warning("Este hilo aún no está en Neo4j.")
                    if st.button("Cargar el hilo en Neo4j"):
                        n = hilos.sincronizar_hilo_neo4j(raiz)
                        st.success(f"{n} comentarios cargados")
                        st.rerun()
            else:
                filas = hilos.get_hilo_sql(raiz)
        except Exception as e:
            st.error(f"No se pudo leer el hilo: {e}")
            filas = []
        if filas:
            ids = {f["IDC"]: f for f in filas}
            foco = st.selectbox("Navegar: ver solo la rama que nace en", list(ids), format_func=lambda i: f"#{i}: {ids[i]['Comentario'][:50]}")
            vista = filas
            if foco != raiz:
                try:
                    vista = hilos.get_hilo_neo4j(foco) if fuente.startswith("Neo4j") else hilos.get_hilo_sql(foco)
                except Exception as e:
                    st.error(f"No se pudo leer la rama: {e}")
                    vista = []
            st.subheader(f"Conversación ({len(vista)} comentarios)")
            for f in vista:
                st.markdown(
                    f"<div style='margin-left:{min(f['Profundidad'], 12) * 22}px;border-left:3px solid #1B7F8C;padding:2px 8px;margin-bottom:6px'>"
                    f"<b>{escape(str(f['Autor']))}</b> · #{f['IDC']} · {escape(str(f['Fecha']))}<br>{escape(str(f['Comentario']))}</div>",
                    unsafe_allow_html=True)
            st.divider()
            st.subheader("Responder")
            destino = st.selectbox("Responder al comentario", list(ids), format_func=lambda i: f"#{i}: {ids[i]['Comentario'][:50]}", key="destino")
            nombres = {f"{u['IDU']} - {u['Nombre']}": u["IDU"] for u in usuarios}
            autor = nombres[st.selectbox("Autor de la respuesta", list(nombres))]
            texto = st.text_area("Tu respuesta", max_chars=400)
            if st.button("Publicar respuesta", type="primary"):
                if not texto.strip():
                    st.error("La respuesta no puede estar vacía")
                else:
                    try:
                        nuevo = hilos.responder(destino, autor, texto.strip())
                        try:
                            hilos.sincronizar_hilo_neo4j(raiz)
                        except Exception:
                            st.info("Respuesta guardada en MySQL; no se pudo actualizar Neo4j.")
                        st.success(f"Respuesta publicada (#{nuevo})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo publicar: {e}")

with tab_nuevo:
    st.write("Crea un comentario nuevo en una publicación (comentario inicial de un hilo).")
    idpub = st.number_input("ID de publicación", min_value=1, value=1, step=1)
    nombres2 = {f"{u['IDU']} - {u['Nombre']}": u["IDU"] for u in usuarios}
    autor2 = nombres2[st.selectbox("Autor", list(nombres2), key="autor2")]
    texto2 = st.text_area("Comentario", max_chars=400, key="texto2")
    if st.button("Crear comentario"):
        if not texto2.strip():
            st.error("El comentario no puede estar vacío")
        else:
            try:
                nuevo = hilos.nuevo_comentario_raiz(autor2, idpub, texto2.strip())
                st.success(f"Comentario creado (#{nuevo})")
            except Exception as e:
                st.error(f"No se pudo crear: {e}")
