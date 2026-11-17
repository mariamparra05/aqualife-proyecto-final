-- 3.d Contribuciones (bitacoras de mantenimiento) segun el tipo de agua.
-- Por cada tipo de agua: total de contribuciones, especie mas popular y categoria mas popular.
-- Empates: se resuelven por IDProd / nombre de categoria.
WITH base AS (
    SELECT e.IDTA, e.IDProd, e.NombreComun, e.Categoria
    FROM Contribucion c
    JOIN Especie e ON e.IDProd = c.IDProd
), total AS (
    SELECT IDTA, COUNT(*) AS Total FROM base GROUP BY IDTA
), por_especie AS (
    SELECT IDTA, IDProd, NombreComun, COUNT(*) AS Contribuciones,
           ROW_NUMBER() OVER (PARTITION BY IDTA ORDER BY COUNT(*) DESC, IDProd) AS Pos
    FROM base GROUP BY IDTA, IDProd, NombreComun
), por_categoria AS (
    SELECT IDTA, Categoria, COUNT(*) AS Contribuciones,
           ROW_NUMBER() OVER (PARTITION BY IDTA ORDER BY COUNT(*) DESC, Categoria) AS Pos
    FROM base GROUP BY IDTA, Categoria
)
SELECT ta.Tipo                  AS TipoAgua,
       t.Total                  AS TotalContribuciones,
       e.IDProd                 AS IDEspecieTop,
       e.NombreComun            AS EspecieMasPopular,
       e.Contribuciones         AS ContribucionesEspecie,
       c.Categoria              AS CategoriaMasPopular,
       c.Contribuciones         AS ContribucionesCategoria
FROM TipoAgua ta
JOIN total t          ON t.IDTA = ta.IDTA
JOIN por_especie e    ON e.IDTA = ta.IDTA AND e.Pos = 1
JOIN por_categoria c  ON c.IDTA = ta.IDTA AND c.Pos = 1
ORDER BY t.Total DESC;
