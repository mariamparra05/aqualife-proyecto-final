# Scripts SQL de AquaLife

Orden de ejecucion (o simplemente `sh cargar_sql.sh`, y `sh cargar_sql.sh --pruebas` para incluir los casos de 3.i):

| Orden | Archivo | Tarea |
|---|---|---|
| 1 | `05_mejoras_diseno.sql` | Mejoras del diseno logico: Publicacion.Fecha, Comentar (IDC, IDC_Padre, Fecha), Historial_Precios, CHECKs, TipoReaccion, vista y indices |
| 2 | `02_trigger_historial_precios.sql` | 3.f trigger de auditoria de precios |
| 3 | `03_sp_analisis_usuario.sql` | 3.g procedimiento `sp_analisis_usuario` |
| 4 | `04_hilos_comentarios.sql` | 4.a hilo de prueba (22 respuestas), trigger y procedimiento `sp_hilo_comentarios` |
| 5 | `06_casos_prueba_3i.sql` | (opcional) vendedor sospechoso ficticio para ver resultados en 3.i |
| - | `01_consultas/*.sql` | 3.a, 3.b, 3.c, 3.d, 3.e, 3.h, 3.i: una sola sentencia SELECT cada una (las usa el Selector de Streamlit) |

Probado en MySQL 8.0 con una version reducida de los datos (300 usuarios, 5000 filas por tabla grande).
Con la base completa (1,1 millones de filas) las consultas 3.h y 3.i pueden tardar varios segundos.
Los scripts con DELIMITER (02, 03, 04, 05, 06) se cargan con el cliente mysql, no con Python.
