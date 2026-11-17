from decimal import Decimal
import pandas as pd
import streamlit as st
from db import run_query, run_transaction, nativo

st.set_page_config(page_title="Gestor de precios", layout="wide")
st.title("Gestor de precios")
st.caption("Cada cambio de precio queda registrado por el trigger trg_auditoria_precios en Historial_Precios")

c1, c2 = st.columns([1, 2])
tipo = c1.radio("Tipo de producto", ["Todos", "Especies", "Equipos"], horizontal=True)
busca = c2.text_input("Buscar por nombre")
filtro = {"Todos": "", "Especies": "AND e.IDProd IS NOT NULL", "Equipos": "AND e.IDProd IS NULL"}[tipo]
try:
    productos = run_query(
        "SELECT p.IDProd, p.Nombre, p.Precio, IF(e.IDProd IS NULL, 'Equipo', 'Especie') AS Tipo "
        "FROM Producto p LEFT JOIN Especie e ON e.IDProd = p.IDProd "
        f"WHERE p.Nombre LIKE CONCAT('%%', %s, '%%') {filtro} ORDER BY p.Nombre, p.IDProd LIMIT 300", (busca,))
except Exception as e:
    st.error(f"No se pudieron leer los productos: {e}")
    st.stop()
if not productos:
    st.info("No hay productos con ese filtro")
    st.stop()

st.dataframe(pd.DataFrame([{k: nativo(v) for k, v in p.items()} for p in productos]))
opciones = {f"#{p['IDProd']} - {p['Nombre']} ({p['Tipo']})": p for p in productos}
prod = opciones[st.selectbox("Producto", list(opciones))]
st.metric("Precio actual", f"{float(prod['Precio']):.2f}")
nuevo = st.number_input("Nuevo precio", min_value=0.01, value=float(prod["Precio"]), step=0.5, format="%.2f")
usuario = st.text_input("Administrador que realiza el cambio", value="admin")

if st.button("Actualizar precio", type="primary"):
    if not usuario.strip():
        st.error("Indica quién realiza el cambio")
    elif Decimal(str(nuevo)) == Decimal(str(prod["Precio"])).quantize(Decimal("0.01")):
        st.warning("El precio nuevo es igual al actual; el trigger no registra nada")
    else:
        try:
            run_transaction([("SET @usuario_app = %s", (usuario.strip(),)),
                             ("UPDATE Producto SET Precio = %s WHERE IDProd = %s", (nuevo, prod["IDProd"]))])
            st.success("Precio actualizado")
        except Exception as e:
            st.error(f"No se pudo actualizar el precio: {e}")

st.subheader("Historial de cambios de este producto")
try:
    hist = run_query("SELECT IDH, PrecioAnterior, PrecioNuevo, PorcentajeCambio, FechaHora, Usuario "
                     "FROM Historial_Precios WHERE IDProd = %s ORDER BY FechaHora DESC, IDH DESC LIMIT 50", (prod["IDProd"],))
    if hist:
        st.dataframe(pd.DataFrame([{k: nativo(v) for k, v in h.items()} for h in hist]))
    else:
        st.info("Aún no hay cambios registrados para este producto")
except Exception as e:
    st.error(f"No se pudo leer el historial (¿se ejecutó sql/02_trigger_historial_precios.sql?): {e}")
