"""Conexiones y utilidades de acceso a datos de AquaLife (sin ORM: SQL escrito a mano).
Valores por defecto = los del docker-compose.yml provisto; se pueden cambiar con variables de entorno / .env."""
import os
from decimal import Decimal
from datetime import date, datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

_mongo_client = None
_neo4j_driver = None


def get_mysql_conn():
    import mysql.connector
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root"),
        database=os.getenv("MYSQL_DATABASE", "AquaLife"),
        charset="utf8mb4",
    )


def run_query(sql, params=None):
    """SELECT: devuelve una lista de diccionarios."""
    conn = get_mysql_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


def run_command(sql, params=None):
    """INSERT / UPDATE / DELETE: devuelve (filas afectadas, ultimo id autoincremental)."""
    conn = get_mysql_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        res = (cur.rowcount, cur.lastrowid)
        cur.close()
        return res
    finally:
        conn.close()


def run_transaction(pasos):
    """Ejecuta varias sentencias en UNA conexion y una transaccion. pasos = [(sql, params), ...].
    Necesario, por ejemplo, para fijar @usuario_app y luego hacer el UPDATE que dispara el trigger."""
    conn = get_mysql_conn()
    try:
        cur = conn.cursor()
        for sql, params in pasos:
            cur.execute(sql, params)
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def call_procedure(name, args=()):
    """CALL a un procedimiento almacenado. Devuelve una lista de resultados (cada uno, lista de diccionarios)."""
    conn = get_mysql_conn()
    try:
        cur = conn.cursor()
        cur.callproc(name, list(args))
        resultados = []
        for r in cur.stored_results():
            cols = r.column_names
            resultados.append([dict(zip(cols, fila)) for fila in r.fetchall()])
        cur.close()
        return resultados
    finally:
        conn.close()


def get_mongo_db():
    import pymongo
    global _mongo_client
    if _mongo_client is None:
        uri = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017/?authSource=admin")
        _mongo_client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=4000)
    return _mongo_client[os.getenv("MONGO_DB", "aqualife")]


def get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is None:
        from neo4j import GraphDatabase
        _neo4j_driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password")))
    return _neo4j_driver


def nativo(v):
    """Convierte Decimal a float y fechas a texto, para mostrarlos en pandas/Streamlit."""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, date):
        return v.isoformat()
    return v
