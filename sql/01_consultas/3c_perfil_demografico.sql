-- 3.c Distribucion de edades por rangos de diez anios (11-20, 21-30, ...).
-- Edad = anios cumplidos hasta hoy. Porcentaje sobre el total de usuarios.
WITH edades AS (
    SELECT IDU, TIMESTAMPDIFF(YEAR, FechaDeNacimiento, CURDATE()) AS Edad
    FROM Usuario
), rangos AS (
    SELECT FLOOR((Edad - 1) / 10) * 10 + 1 AS Inicio FROM edades
)
SELECT CONCAT(Inicio, '-', Inicio + 9)                         AS RangoEdad,
       COUNT(*)                                                AS Usuarios,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)        AS Porcentaje
FROM rangos
GROUP BY Inicio
ORDER BY Inicio;
