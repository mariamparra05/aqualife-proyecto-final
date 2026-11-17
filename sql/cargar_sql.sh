#!/bin/sh
# Carga todos los scripts en el orden correcto sobre el contenedor MySQL de AquaLife.
# Uso (desde la raiz del repo):  sh sql/cargar_sql.sh            (con casos de prueba de 3.i: sh cargar_sql.sh --pruebas)
cd "$(dirname "$0")"   # funciona desde cualquier carpeta
CONT=aqualife_mysql
run() { echo ">> $1"; docker exec -i $CONT mysql -uroot -proot --default-character-set=utf8mb4 AquaLife < "$1"; }
run 05_mejoras_diseno.sql
run 02_trigger_historial_precios.sql
run 03_sp_analisis_usuario.sql
run 04_hilos_comentarios.sql
[ "$1" = "--pruebas" ] && run 06_casos_prueba_3i.sql
echo "Listo."
