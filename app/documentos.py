"""Documentos jerarquicos de especies (MongoDB): ficha principal + documentos secundarios incrustados."""
from db import get_mongo_db, run_query

COLECCION = "fichas_especie"
TIPOS = ["certificado_sanitario", "guia_alimentacion_estacional", "manual_tratamiento_enfermedades",
         "historial_crecimiento", "analisis_agua"]
NOMBRES_TIPO = {
    "certificado_sanitario": "Certificado sanitario",
    "guia_alimentacion_estacional": "Guía de alimentación estacional",
    "manual_tratamiento_enfermedades": "Manual de tratamiento de enfermedades",
    "historial_crecimiento": "Historial de crecimiento",
    "analisis_agua": "Análisis de agua",
}


def get_documentos_especie(especie_id):
    """Ficha principal y documentos secundarios de una especie (o None si no tiene ficha)."""
    return get_mongo_db()[COLECCION].find_one({"especie_id": int(especie_id)}, {"_id": 0})


def ids_con_ficha():
    return {d["especie_id"] for d in get_mongo_db()[COLECCION].find({}, {"especie_id": 1, "_id": 0})}


def listar_especies_con_ficha():
    """Especies (de MySQL) que tienen ficha en MongoDB, para el desplegable de la app."""
    ids = sorted(ids_con_ficha())
    if not ids:
        return []
    marcas = ", ".join(["%s"] * len(ids))
    return run_query(f"SELECT IDProd, NombreComun, Categoria FROM Especie WHERE IDProd IN ({marcas}) ORDER BY NombreComun", tuple(ids))


def formatear_arbol(doc):
    """Representacion jerarquica en texto: ficha > documentos secundarios > campos."""
    def campos(v, nivel):
        sangria = "    " * nivel
        out = []
        if isinstance(v, dict):
            for k, x in v.items():
                if isinstance(x, (dict, list)):
                    out.append(f"{sangria}- {k}:"); out += campos(x, nivel + 1)
                else:
                    out.append(f"{sangria}- {k}: {x}")
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, (dict, list)):
                    out.append(f"{sangria}-"); out += campos(x, nivel + 1)
                else:
                    out.append(f"{sangria}- {x}")
        return out
    principal = {k: v for k, v in doc.items() if k != "documentos_secundarios"}
    lineas = [f"FICHA DE ESPECIE #{doc['especie_id']}: {doc['nombre_comun']}"] + campos(principal, 1)
    for d in doc.get("documentos_secundarios", []):
        lineas.append(f"  DOCUMENTO SECUNDARIO: {NOMBRES_TIPO.get(d['tipo'], d['tipo'])}")
        lineas += campos({k: v for k, v in d.items() if k != "tipo"}, 2)
    return lineas
