-- 3.h Top 5 influencers y su impacto en ventas.
-- Puntaje = reacciones recibidas ponderadas (Me gusta 1, Me encanta 2, Me asombra 1.5, otras 0)
--           + 2 por cada comentario recibido en sus publicaciones.
-- Especies de interaccion: la tabla Publicacion NO se relaciona con especies, por eso se miden
--   las contribuciones y las compras del influencer (se toman las 3 especies con mas interacciones).
-- Incremento de ventas: unidades vendidas de esas especies en los 14 dias posteriores a cada
--   fecha de publicacion o contribucion del influencer, frente a los 14 dias anteriores.
-- Tasa de conversion: % de usuarios que reaccionaron a sus publicaciones y despues compraron
--   alguna especie (compra con fecha >= fecha de su primera reaccion).
-- Correlacion: se calcula entre Puntaje e IncrementoVentasPct (por ejemplo en pandas con .corr()).
WITH pts_reac AS (
    SELECT p.IDU,
           SUM(CASE r.Tipo WHEN 'Me gusta' THEN 1 WHEN 'Me encanta' THEN 2
                           WHEN 'Me asombra' THEN 1.5 ELSE 0 END) AS pts
    FROM Publicacion p JOIN Reaccionar r ON r.IDPub = p.IDPub
    GROUP BY p.IDU
), pts_com AS (
    SELECT p.IDU, 2 * COUNT(*) AS pts
    FROM Publicacion p JOIN Comentar c ON c.IDPub = p.IDPub
    GROUP BY p.IDU
), top5 AS (
    SELECT u.IDU, u.Nombre,
           COALESCE(r.pts, 0) + COALESCE(c.pts, 0) AS Puntaje
    FROM Usuario u
    LEFT JOIN pts_reac r ON r.IDU = u.IDU
    LEFT JOIN pts_com  c ON c.IDU = u.IDU
    ORDER BY Puntaje DESC, u.IDU
    LIMIT 5
), interacciones AS (
    SELECT IDU, IDProd, COUNT(*) AS n
    FROM (SELECT co.IDU, co.IDProd FROM Contribucion co WHERE co.IDU IN (SELECT IDU FROM top5)
          UNION ALL
          SELECT c.IDUC, c.IDProd FROM Compra c JOIN Especie e ON e.IDProd = c.IDProd
          WHERE c.IDUC IN (SELECT IDU FROM top5)) x
    GROUP BY IDU, IDProd
), top_esp AS (
    SELECT i.IDU, i.IDProd, es.NombreComun, i.n,
           ROW_NUMBER() OVER (PARTITION BY i.IDU ORDER BY i.n DESC, i.IDProd) AS Pos
    FROM interacciones i JOIN Especie es ON es.IDProd = i.IDProd
), eventos AS (
    SELECT IDU, Fecha FROM Publicacion  WHERE IDU IN (SELECT IDU FROM top5)
    UNION
    SELECT IDU, Fecha FROM Contribucion WHERE IDU IN (SELECT IDU FROM top5)
), ventas AS (
    SELECT ev.IDU,
           SUM(CASE WHEN c.Fecha <  ev.Fecha THEN c.Cantidad ELSE 0 END) AS Antes,
           SUM(CASE WHEN c.Fecha >= ev.Fecha THEN c.Cantidad ELSE 0 END) AS Despues
    FROM eventos ev
    JOIN top_esp te ON te.IDU = ev.IDU AND te.Pos <= 3
    JOIN Compra c   ON c.IDProd = te.IDProd
                   AND c.Fecha >= DATE_SUB(ev.Fecha, INTERVAL 14 DAY)
                   AND c.Fecha <  DATE_ADD(ev.Fecha, INTERVAL 14 DAY)
    GROUP BY ev.IDU
), reactores AS (
    SELECT p.IDU AS Influencer, r.IDU AS Usuario, MIN(r.Fecha) AS Primera
    FROM Publicacion p JOIN Reaccionar r ON r.IDPub = p.IDPub
    WHERE p.IDU IN (SELECT IDU FROM top5) AND r.IDU <> p.IDU
    GROUP BY p.IDU, r.IDU
), conversion AS (
    SELECT re.Influencer, COUNT(*) AS Reactores,
           SUM(EXISTS (SELECT 1 FROM Compra c JOIN Especie e ON e.IDProd = c.IDProd
                       WHERE c.IDUC = re.Usuario AND c.Fecha >= re.Primera)) AS Convertidos
    FROM reactores re
    GROUP BY re.Influencer
), lista_esp AS (
    SELECT IDU, GROUP_CONCAT(CONCAT(NombreComun, ' (#', IDProd, ')') ORDER BY Pos SEPARATOR ', ') AS Especies
    FROM top_esp WHERE Pos <= 3 GROUP BY IDU
)
SELECT t.IDU AS IDInfluencer, t.Nombre, t.Puntaje,
       l.Especies                                          AS EspeciesMasInteractuadas,
       v.Antes                                             AS UnidadesAntes,
       v.Despues                                           AS UnidadesDespues,
       ROUND(100 * (v.Despues - v.Antes) / NULLIF(v.Antes, 0), 2)  AS IncrementoVentasPct,
       cv.Reactores,
       cv.Convertidos,
       ROUND(100 * cv.Convertidos / NULLIF(cv.Reactores, 0), 2)    AS TasaConversionPct
FROM top5 t
LEFT JOIN lista_esp l   ON l.IDU = t.IDU
LEFT JOIN ventas v      ON v.IDU = t.IDU
LEFT JOIN conversion cv ON cv.Influencer = t.IDU
ORDER BY t.Puntaje DESC;
