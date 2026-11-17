-- 3.i Deteccion de vendedores con comportamiento anomalo.  Vendedor = Usuario (Compra.IDUV).
-- Cuatro patrones, cada uno con una puntuacion de 0 a 1 y una evidencia en texto.
-- Indice de sospecha = 0.30*P1 + 0.25*P2 + 0.25*P3 + 0.20*P4  (pesos que suman 1).
-- Umbrales (documentar en el informe; ajustables):
--   P1 variacion de precio > 30 % del mismo producto dentro de un mismo mes (sin justificacion temporal)
--   P2 al menos 10 ventas calificadas y mas del 25 % de cada extremo (5 y 1)
--   P3 al menos 5 compradores y 80 % o mas de ellos con 1 compra o menos a otros vendedores
--   P4 producto con 3 o mas vendedores, precio medio del vendedor a mas de 2 desviaciones del resto
-- Para ver casos reales con los datos aleatorios ejecutar antes 06_casos_prueba_3i.sql
WITH p1_det AS (
    SELECT IDUV, IDProd, anio, mes, variacion,
           ROW_NUMBER() OVER (PARTITION BY IDUV ORDER BY variacion DESC, IDProd) AS rn,
           COUNT(*)     OVER (PARTITION BY IDUV) AS casos
    FROM (SELECT IDUV, IDProd, YEAR(Fecha) AS anio, MONTH(Fecha) AS mes,
                 (MAX(Precio) - MIN(Precio)) / MIN(Precio) AS variacion
          FROM Compra
          GROUP BY IDUV, IDProd, YEAR(Fecha), MONTH(Fecha)
          HAVING MIN(Precio) > 0 AND (MAX(Precio) - MIN(Precio)) / MIN(Precio) > 0.30) v
), p1 AS (
    SELECT IDUV, LEAST(1, variacion / 0.60) AS score,
           CONCAT(casos, ' producto-mes con variacion de precio mayor al 30 % (maxima ',
                  ROUND(variacion * 100), ' % en producto #', IDProd, ', ', anio, '-', mes, ')') AS evidencia
    FROM p1_det WHERE rn = 1
), p2 AS (
    SELECT IDUV, LEAST(1, SUM(Puntuacion IN (1,5)) / COUNT(*)) AS score,
           CONCAT('Calificaciones polarizadas: ', ROUND(100 * SUM(Puntuacion = 5) / COUNT(*)), ' % de 5 y ',
                  ROUND(100 * SUM(Puntuacion = 1) / COUNT(*)), ' % de 1 en ', COUNT(*), ' ventas calificadas') AS evidencia
    FROM Compra
    WHERE Puntuacion IS NOT NULL
    GROUP BY IDUV
    HAVING COUNT(*) >= 10 AND SUM(Puntuacion = 5) / COUNT(*) > 0.25 AND SUM(Puntuacion = 1) / COUNT(*) > 0.25
), pares AS (
    SELECT IDUV, IDUC, COUNT(*) AS n FROM Compra GROUP BY IDUV, IDUC
), total_comprador AS (
    SELECT IDUC, COUNT(*) AS total FROM Compra GROUP BY IDUC
), p3 AS (
    SELECT pa.IDUV, SUM(tc.total - pa.n <= 1) / COUNT(*) AS score,
           CONCAT(ROUND(100 * SUM(tc.total - pa.n <= 1) / COUNT(*)), ' % de sus ', COUNT(*),
                  ' compradores casi nunca compra a otros vendedores') AS evidencia
    FROM pares pa JOIN total_comprador tc ON tc.IDUC = pa.IDUC
    GROUP BY pa.IDUV
    HAVING COUNT(*) >= 5 AND SUM(tc.total - pa.n <= 1) / COUNT(*) >= 0.80
), prod_vend AS (
    SELECT IDProd, IDUV, AVG(Precio) AS pm,
           AVG(AVG(Precio))        OVER (PARTITION BY IDProd) AS media,
           STDDEV_POP(AVG(Precio)) OVER (PARTITION BY IDProd) AS desv,
           COUNT(*)                OVER (PARTITION BY IDProd) AS vendedores
    FROM Compra GROUP BY IDProd, IDUV
), p4_det AS (
    SELECT IDUV, IDProd, pm, media, ABS(pm - media) / desv AS z,
           ROW_NUMBER() OVER (PARTITION BY IDUV ORDER BY ABS(pm - media) / desv DESC, IDProd) AS rn,
           COUNT(*)     OVER (PARTITION BY IDUV) AS casos
    FROM prod_vend
    WHERE vendedores >= 3 AND desv > 0 AND ABS(pm - media) / desv > 2
), p4 AS (
    SELECT IDUV, LEAST(1, z / 4) AS score,
           CONCAT('Precio atipico frente a otros vendedores en ', casos, ' producto(s); peor caso: producto #', IDProd,
                  ' a ', ROUND(pm, 2), ' contra media ', ROUND(media, 2)) AS evidencia
    FROM p4_det WHERE rn = 1
), todos AS (
    SELECT IDUV, 0.30 AS peso, score, evidencia FROM p1
    UNION ALL SELECT IDUV, 0.25, score, evidencia FROM p2
    UNION ALL SELECT IDUV, 0.25, score, evidencia FROM p3
    UNION ALL SELECT IDUV, 0.20, score, evidencia FROM p4
)
SELECT u.IDU AS IDVendedor, u.Nombre, u.Email,
       ROUND(SUM(t.peso * t.score), 2)             AS IndiceSospecha,
       COUNT(*)                                    AS PatronesDetectados,
       GROUP_CONCAT(t.evidencia SEPARATOR ' | ')   AS Evidencias
FROM todos t
JOIN Usuario u ON u.IDU = t.IDUV
GROUP BY u.IDU, u.Nombre, u.Email
ORDER BY IndiceSospecha DESC, u.IDU
LIMIT 50;
