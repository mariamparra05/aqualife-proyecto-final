"""Dado el id de una especie, muestra su ficha y todos sus documentos secundarios de forma jerarquica.
Uso:  python nosql/documentos_mongo/consulta_especie.py 3"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
from documentos import get_documentos_especie, formatear_arbol

if __name__ == "__main__":
    idp = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    doc = get_documentos_especie(idp)
    print("\n".join(formatear_arbol(doc)) if doc else f"La especie {idp} no tiene ficha")
