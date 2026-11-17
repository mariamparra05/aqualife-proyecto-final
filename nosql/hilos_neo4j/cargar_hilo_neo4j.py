"""Tarea 4.b: carga en Neo4j el hilo de comentarios (mismos IDC que en MySQL) y lo consulta.
Uso:  python nosql/hilos_neo4j/cargar_hilo_neo4j.py [IDC_raiz]      (por defecto 2000001, el hilo de prueba)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "app"))
from hilos import sincronizar_hilo_neo4j, get_hilo_neo4j, comparar_hilos

if __name__ == "__main__":
    raiz = int(sys.argv[1]) if len(sys.argv) > 1 else 2000001
    n = sincronizar_hilo_neo4j(raiz)
    print(f"Comentarios cargados en Neo4j: {n}")
    for h in get_hilo_neo4j(raiz):
        print("  " * h["Profundidad"] + f"#{h['IDC']} (usuario {h['IDU']}): {h['Comentario'][:60]}")
    print("Comparacion MySQL vs Neo4j:", comparar_hilos(raiz))
