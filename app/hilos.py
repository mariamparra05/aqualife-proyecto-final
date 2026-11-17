"""Hilos de comentarios: version relacional (MySQL) y version en grafo (Neo4j). Mismos IDC en ambas."""
from db import run_query, run_command, call_procedure, get_neo4j_driver, nativo

# ----------------------------------------------------------------------------- MySQL
def listar_raices_con_respuestas(limite=200):
    return run_query(
        "SELECT c.IDC, c.IDPub, LEFT(c.Comentario, 70) AS Texto FROM Comentar c "
        "WHERE c.IDC_Padre IS NULL AND c.IDC IN (SELECT DISTINCT IDC_Padre FROM Comentar WHERE IDC_Padre IS NOT NULL) "
        "ORDER BY c.IDC DESC LIMIT %s", (limite,))


def raices_de_publicacion(idpub, limite=100):
    return run_query(
        "SELECT IDC, LEFT(Comentario, 70) AS Texto FROM Comentar WHERE IDPub = %s AND IDC_Padre IS NULL "
        "ORDER BY IDC DESC LIMIT %s", (idpub, limite))


def get_hilo_sql(idc):
    """Conversacion completa a partir de un comentario (procedimiento sp_hilo_comentarios)."""
    res = call_procedure("sp_hilo_comentarios", (int(idc),))
    return res[0] if res else []


def responder(idc_padre, idu, texto):
    """Inserta una respuesta al comentario idc_padre (la publicacion se toma del padre). Devuelve el nuevo IDC."""
    padre = run_query("SELECT IDPub FROM Comentar WHERE IDC = %s", (int(idc_padre),))
    if not padre:
        raise ValueError("El comentario padre no existe")
    _, nuevo = run_command(
        "INSERT INTO Comentar (IDU, IDPub, Comentario, IDC_Padre) VALUES (%s, %s, %s, %s)",
        (int(idu), padre[0]["IDPub"], texto, int(idc_padre)))
    return nuevo


def nuevo_comentario_raiz(idu, idpub, texto):
    _, nuevo = run_command(
        "INSERT INTO Comentar (IDU, IDPub, Comentario, IDC_Padre) VALUES (%s, %s, %s, NULL)",
        (int(idu), int(idpub), texto))
    return nuevo

# ----------------------------------------------------------------------------- Neo4j
CY_CONSTRAINTS = [
    "CREATE CONSTRAINT usuario_idu IF NOT EXISTS FOR (u:Usuario) REQUIRE u.idu IS UNIQUE",
    "CREATE CONSTRAINT comentario_idc IF NOT EXISTS FOR (c:Comentario) REQUIRE c.idc IS UNIQUE",
]
CY_NODOS = """
UNWIND $filas AS f
MERGE (u:Usuario {idu: f.idu})
SET u.nombre = f.autor
MERGE (c:Comentario {idc: f.idc})
SET c.texto = f.comentario, c.fecha = f.fecha
MERGE (u)-[:ESCRIBIO]->(c)
"""
CY_RELACIONES = """
UNWIND $filas AS f
WITH f WHERE f.idc_padre IS NOT NULL
MATCH (c:Comentario {idc: f.idc}), (p:Comentario {idc: f.idc_padre})
MERGE (c)-[:RESPONDE_A]->(p)
"""
CY_HILO = """
MATCH path = (c:Comentario)-[:RESPONDE_A*0..]->(raiz:Comentario {idc: $idc})
MATCH (u:Usuario)-[:ESCRIBIO]->(c)
OPTIONAL MATCH (c)-[:RESPONDE_A]->(padre:Comentario)
RETURN c.idc AS idc, padre.idc AS idc_padre, length(path) AS profundidad,
       u.idu AS idu, u.nombre AS autor, c.texto AS comentario, c.fecha AS fecha,
       [n IN reverse(nodes(path)) | n.idc] AS ruta
"""


def sincronizar_hilo_neo4j(raiz_idc):
    """Copia a Neo4j el hilo que nace en raiz_idc (leyendo MySQL). Devuelve cuantos comentarios cargo."""
    hilo = get_hilo_sql(raiz_idc)
    filas = [{"idc": int(h["IDC"]), "idc_padre": None if h["IDC_Padre"] is None else int(h["IDC_Padre"]),
              "idu": int(h["IDU"]), "autor": h["Autor"], "comentario": h["Comentario"],
              "fecha": str(nativo(h["Fecha"])), "idpub": 0} for h in hilo]
    if not filas:
        return 0
    drv = get_neo4j_driver()
    with drv.session() as s:
        for q in CY_CONSTRAINTS:
            s.run(q)
        s.run(CY_NODOS, filas=filas)
        s.run(CY_RELACIONES, filas=filas)
    return len(filas)


def ordenar_hilo(filas):
    """Ordena en preorden (cada respuesta debajo de su padre) usando la ruta raiz->comentario."""
    return sorted(filas, key=lambda f: tuple(f["ruta"]))


def get_hilo_neo4j(idc):
    """Conversacion completa desde Neo4j. Devuelve las mismas columnas que sp_hilo_comentarios."""
    drv = get_neo4j_driver()
    with drv.session() as s:
        filas = s.run(CY_HILO, idc=int(idc)).data()
    return [{"IDC": f["idc"], "IDC_Padre": f["idc_padre"], "Profundidad": f["profundidad"], "IDU": f["idu"],
             "Autor": f["autor"], "Comentario": f["comentario"], "Fecha": f["fecha"]} for f in ordenar_hilo(filas)]


def comparar_hilos(idc):
    """Comprueba que MySQL y Neo4j devuelven los mismos identificadores de comentario."""
    a = [h["IDC"] for h in get_hilo_sql(idc)]
    b = [h["IDC"] for h in get_hilo_neo4j(idc)]
    return {"mysql": len(a), "neo4j": len(b), "mismos_ids": set(a) == set(b), "mismo_orden": a == b}
