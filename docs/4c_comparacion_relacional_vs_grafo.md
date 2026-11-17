# 4.c Comparación: hilos de comentarios en MySQL (relacional) vs. Neo4j (grafo)

**Modelo relacional.** Lista de adyacencia: la tabla `Comentar` tiene `IDC` (clave) e `IDC_Padre` (clave foránea a sí misma; NULL en el comentario raíz). El hilo completo se obtiene con una consulta recursiva (`WITH RECURSIVE`, procedimiento `sp_hilo_comentarios`).

**Modelo de grafo.** Nodos `(:Comentario {idc})` y `(:Usuario {idu})`; relaciones `(:Usuario)-[:ESCRIBIO]->(:Comentario)` y `(:Comentario)-[:RESPONDE_A]->(:Comentario)`. El hilo se obtiene con un patrón de camino de longitud variable `(c)-[:RESPONDE_A*0..]->(raiz)`. Los `idc` son los mismos en ambas bases.

| Criterio | Relacional (MySQL) | Grafo (Neo4j) |
|---|---|---|
| Recuperar un hilo completo | Consulta recursiva (CTE); más larga de escribir y ordenar (ruta con LPAD) | Un patrón de camino de una línea; el recorrido es la operación natural del motor |
| Integridad | Claves foráneas al padre, al usuario y a la publicación; trigger que obliga a que la respuesta sea de la misma publicación | Restricción de unicidad del `idc`; las relaciones no validan por sí mismas la publicación (lo hace la aplicación) |
| Escritura de una respuesta | Un `INSERT` transaccional (ACID) | Crear nodo y relación; hay que mantener la sincronía con MySQL si MySQL es la fuente |
| Relación con el resto del negocio | `JOIN` directo con usuarios, publicaciones, compras y reacciones (todo está en MySQL) | Los datos de compras y publicaciones no están en el grafo; habría que duplicarlos o consultar dos sistemas |
| Consultas sobre la estructura (quién respondió a quién, profundidad, cadenas, comunidades) | Posibles pero con recursión pesada | Muy naturales (caminos, vecinos, recorridos) |
| Profundidad y volumen | La recursión tiene límite (`cte_max_recursion_depth`) y coste por nivel | Recorrido por adyacencia; escala bien con hilos profundos |
| Esquema y evolución | Rígido: cambiar columnas implica `ALTER TABLE` en 1,1 millones de filas | Flexible: se añaden propiedades o tipos de relación sin migrar |
| Complejidad operativa | Una sola base, ya existente | Un motor más que desplegar, aprender y mantener |

**Conclusión sugerida.** En este escenario los comentarios están fuertemente ligados a usuarios, publicaciones y compras, y se necesita integridad referencial y transacciones: el modelo relacional resuelve bien el caso con una consulta recursiva y es la fuente de verdad. El grafo aporta ventaja cuando se quieren analizar las conversaciones como red (cadenas de respuestas, influencia, hilos muy profundos). Una arquitectura razonable es MySQL como base principal y Neo4j como índice de lectura para análisis de hilos. *Completar con los tiempos medidos por el equipo (EXPLAIN ANALYZE en MySQL y PROFILE en Neo4j).*
