-- 3.b Publicaciones con mas reacciones positivas que negativas.
-- Supuesto (documentar en el informe):
--   positivas = Me gusta, Me encanta, Me asombra, Me divierte
--   negativas = Me entristece, Me enoja
SELECT p.IDPub,
       p.Texto,
       p.Fecha                                   AS FechaPublicacion,
       u.Nombre                                  AS Autor,
       SUM(r.Tipo IN ('Me gusta','Me encanta','Me asombra','Me divierte')) AS Positivas,
       SUM(r.Tipo IN ('Me entristece','Me enoja'))                         AS Negativas,
       COUNT(*)                                  AS TotalReacciones
FROM Publicacion p
JOIN Usuario u    ON u.IDU = p.IDU
JOIN Reaccionar r ON r.IDPub = p.IDPub
GROUP BY p.IDPub, p.Texto, p.Fecha, u.Nombre
HAVING Positivas > Negativas
ORDER BY (Positivas - Negativas) DESC, p.IDPub;
