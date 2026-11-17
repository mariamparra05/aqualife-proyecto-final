"""Tarea 5: carga fichas de especie (documento principal) con documentos secundarios en MongoDB.
Los datos de la ficha salen de MySQL, asi el especie_id coincide con Especie.IDProd.
Uso:  python nosql/documentos_mongo/cargar_fichas.py [--por-categoria 2]"""
import argparse, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
from db import run_query, get_mongo_db
from documentos import COLECCION

# parametros de agua tipicos segun el tipo de agua (busqueda por fragmento del nombre, en minusculas)
PARAMS_AGUA = [
    ("marin", dict(temperatura_c=(24, 26), ph=(8.1, 8.4), densidad=(1.023, 1.025), dureza_dkh=(7, 9))),
    ("salobre", dict(temperatura_c=(24, 28), ph=(7.8, 8.4), densidad=(1.005, 1.015), dureza_dkh=(10, 15))),
    ("fr", dict(temperatura_c=(14, 20), ph=(6.5, 7.5), dureza_gh=(5, 12))),
    ("negra", dict(temperatura_c=(24, 28), ph=(5.0, 6.5), dureza_gh=(1, 4))),
    ("lago", dict(temperatura_c=(24, 28), ph=(7.8, 8.6), dureza_gh=(10, 20))),
]
POR_DEFECTO = dict(temperatura_c=(24, 28), ph=(6.5, 7.5), dureza_gh=(4, 12))


def parametros(tipo_agua):
    t = (tipo_agua or "").lower()
    for clave, p in PARAMS_AGUA:
        if clave in t:
            return p
    return POR_DEFECTO


def rango(t):
    return {"min": t[0], "max": t[1]}


def analisis_agua(esp, rnd):
    p = parametros(esp["TipoAgua"])
    parametros_ = {k: rango(v) for k, v in p.items()}
    parametros_.update({"amoniaco_ppm": {"max": 0.0}, "nitritos_ppm": {"max": 0.0}, "nitratos_ppm": {"max": rnd.choice([10, 20, 25])}})
    if esp["Categoria"] == "Coral":
        parametros_.update({"calcio_ppm": rango((400, 450)), "magnesio_ppm": rango((1250, 1350))})
    if esp["Categoria"] == "Planta Acuática":
        parametros_.update({"fosfatos_ppm": rango((0.1, 1.0)), "hierro_ppm": rango((0.05, 0.2)), "co2_ppm": rango((15, 30))})
    return {"tipo": "analisis_agua", "fecha": "2026-10-15", "laboratorio": "Laboratorio AquaSolutions", "parametros": parametros_}


def certificado(esp, rnd):
    return {"tipo": "certificado_sanitario", "fecha_emision": "2026-10-20", "emitido_por": "Dra. M. Fuentes",
            "ejemplares_revisados": rnd.choice([3, 5, 10]), "resultado": "Apto para la venta",
            "enfermedades_descartadas": ["ich", "hongos", "parasitos internos"] if esp["Categoria"] == "Pez"
            else ["plagas", "algas invasoras"] if esp["Categoria"] == "Planta Acuática"
            else ["vibrio", "plaga de anemonas"] if esp["Categoria"] == "Coral" else ["parasitos", "bacterias"],
            "cuarentena_dias": rnd.choice([14, 21, 30])}


def guia_alimentacion(esp, rnd):
    if esp["Categoria"] == "Planta Acuática":
        est = {"primavera": "Fertilizante liquido semanal", "verano": "Fertilizante y CO2 diario", "otonio": "Fertilizante quincenal", "invierno": "Sin fertilizante"}
    elif esp["Categoria"] == "Coral":
        est = {"primavera": "Fitoplancton 3 veces por semana", "verano": "Fitoplancton diario", "otonio": "Zooplancton 2 veces por semana", "invierno": "Zooplancton 1 vez por semana"}
    else:
        est = {"primavera": {"alimento": "Escamas y congelado", "tomas_diarias": 2}, "verano": {"alimento": "Alimento vivo y escamas", "tomas_diarias": 3},
               "otonio": {"alimento": "Escamas", "tomas_diarias": 2}, "invierno": {"alimento": "Escamas", "tomas_diarias": 1}}
    return {"tipo": "guia_alimentacion_estacional", "estaciones": est, "advertencias": ["No sobrealimentar", "Retirar restos a los 5 minutos"]}


def manual_enfermedades(esp, rnd):
    if esp["Categoria"] == "Coral":
        enf = [{"nombre": "RTN/STN (necrosis de tejido)", "sintomas": ["perdida de tejido"], "tratamiento": "Fragmar y bano de yodo"}]
    elif esp["Categoria"] == "Planta Acuática":
        enf = [{"nombre": "Algas en hojas", "sintomas": ["manchas verdes"], "tratamiento": "Reducir luz y mejorar el flujo"},
               {"nombre": "Clorosis", "sintomas": ["hojas amarillas"], "tratamiento": "Aportar hierro"}]
    else:
        enf = [{"nombre": "Ich", "sintomas": ["puntos blancos", "roce contra objetos"], "tratamiento": "Subir temperatura a 28 C y sal 10 dias"},
               {"nombre": "Hongos", "sintomas": ["algodon blanco"], "tratamiento": "Banos con azul de metileno"},
               {"nombre": "Parasitos internos", "sintomas": ["perdida de peso", "heces blancas"], "tratamiento": "Antiparasitario en alimento"}]
    return {"tipo": "manual_tratamiento_enfermedades", "enfermedades": enf, "prevencion": ["Cuarentena", "Cambios de agua regulares"]}


def historial_crecimiento(esp, rnd):
    if esp["Categoria"] == "Planta Acuática":
        etapas = [{"semanas": 2, "altura_cm": 5}, {"semanas": 6, "altura_cm": 15}, {"semanas": 12, "altura_cm": 30}]
    elif esp["Categoria"] == "Coral":
        etapas = [{"meses": 3, "diametro_cm": 3}, {"meses": 12, "diametro_cm": 8}, {"meses": 24, "diametro_cm": 15}]
    else:
        etapas = [{"etapa": "alevin", "semanas": 4, "longitud_cm": 1.5}, {"etapa": "juvenil", "semanas": 16, "longitud_cm": 4}, {"etapa": "adulto", "semanas": 40, "longitud_cm": rnd.choice([6, 8, 12])}]
    return {"tipo": "historial_crecimiento", "etapas": etapas}


# cada categoria lleva documentos secundarios distintos (estructuras variables)
TIPOS_POR_CATEGORIA = {
    "Pez": [certificado, guia_alimentacion, manual_enfermedades, historial_crecimiento, analisis_agua],
    "Invertebrado": [certificado, guia_alimentacion, analisis_agua],
    "Planta Acuática": [guia_alimentacion, manual_enfermedades, historial_crecimiento, analisis_agua],
    "Coral": [certificado, guia_alimentacion, manual_enfermedades, historial_crecimiento, analisis_agua],
}


def construir_ficha(esp):
    rnd = random.Random(esp["IDProd"])
    fabricas = TIPOS_POR_CATEGORIA.get(esp["Categoria"], [certificado, guia_alimentacion, analisis_agua])
    p = parametros(esp["TipoAgua"])
    return {
        "especie_id": esp["IDProd"],
        "tipo_documento": "ficha_especie",
        "nombre_comun": esp["NombreComun"],
        "nombre_cientifico": esp["NombreCientifico"],
        "categoria": esp["Categoria"],
        "tipo_agua": esp["TipoAgua"],
        "tipo_sustrato": esp["TipoSustrato"],
        "temporada": esp["Temporada"],
        "cuidados_especificos": esp["Cuidados"],
        "requisitos": {"horas_luz": esp["HorasLuz"], "litros_minimos_tanque": esp["LitrosMinimosTanque"],
                       "temperatura_c": rango(p["temperatura_c"]), "ph": rango(p["ph"])},
        "documentos_secundarios": [f(esp, rnd) for f in fabricas],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--por-categoria", type=int, default=2, help="fichas por categoria (4 categorias; minimo 2 para llegar a 5+)")
    a = ap.parse_args()
    especies = run_query(
        "SELECT e.IDProd, e.NombreComun, e.NombreCientifico, e.Categoria, e.TipoSustrato, e.HorasLuz, e.LitrosMinimosTanque, "
        "ta.Tipo AS TipoAgua, t.Nombre AS Temporada, ce.Descripcion AS Cuidados "
        "FROM Especie e JOIN TipoAgua ta ON ta.IDTA = e.IDTA JOIN Temporada t ON t.IDT = e.IDT "
        "JOIN Cuidados_Especificos ce ON ce.IDCE = e.IDCE "
        "WHERE (SELECT COUNT(*) FROM Especie x WHERE x.Categoria = e.Categoria AND x.IDProd < e.IDProd) < %s "
        "ORDER BY e.Categoria, e.IDProd", (a.por_categoria,))
    fichas = [construir_ficha(e) for e in especies]
    db = get_mongo_db()
    if COLECCION not in db.list_collection_names():
        try:   # validacion minima de la estructura (si el servidor la admite)
            db.create_collection(COLECCION, validator={"$jsonSchema": {
                "bsonType": "object", "required": ["especie_id", "nombre_comun", "categoria", "documentos_secundarios"],
                "properties": {"especie_id": {"bsonType": "int"}, "documentos_secundarios": {"bsonType": "array"}}}})
        except Exception:
            pass
    col = db[COLECCION]
    col.delete_many({})
    col.create_index("especie_id", unique=True)
    col.insert_many(fichas)
    print(f"Fichas cargadas: {col.count_documents({})}")
    for f in fichas:
        print(f"  #{f['especie_id']} {f['nombre_comun']} ({f['categoria']}): "
              + ", ".join(d['tipo'] for d in f['documentos_secundarios']))


if __name__ == "__main__":
    main()
