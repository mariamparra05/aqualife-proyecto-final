-- 3.e Cinco vendedores con mejor calificacion promedio (especies y equipos).
-- En la base no existen "tiendas" ni "criadores": el vendedor es un Usuario (Compra.IDUV)
-- y la calificacion es Compra.Puntuacion (puede ser NULL, se ignora).
-- Supuesto: se exigen al menos 5 ventas calificadas para evitar un 5.0 con una sola nota
-- (cambiar el 5 de HAVING o quitarlo si no se desea).
SELECT u.IDU                                   AS IDVendedor,
       u.Nombre,
       u.Email,
       u.DireccionParticular                   AS Direccion,
       SUM(c.Cantidad)                         AS TotalProductosVendidos,
       SUM(CASE WHEN e.IDProd IS NOT NULL THEN c.Cantidad ELSE 0 END) AS TotalEspecies,
       SUM(CASE WHEN e.IDProd IS NULL     THEN c.Cantidad ELSE 0 END) AS TotalEquipos,
       COUNT(c.Puntuacion)                     AS VentasCalificadas,
       ROUND(AVG(c.Puntuacion), 2)             AS CalificacionPromedio
FROM Compra c
JOIN Usuario u        ON u.IDU = c.IDUV
LEFT JOIN Especie e   ON e.IDProd = c.IDProd
GROUP BY u.IDU, u.Nombre, u.Email, u.DireccionParticular
HAVING COUNT(c.Puntuacion) >= 5
ORDER BY CalificacionPromedio DESC, TotalProductosVendidos DESC
LIMIT 5;
