-- 3.a Termometro de la comunidad: total de reacciones recibidas por cada publicacion,
--     con la informacion de la publicacion y de su autor.
-- Requiere: 05_mejoras_diseno.sql (usa Publicacion.Fecha).
-- LEFT JOIN: las publicaciones sin reacciones tambien aparecen (total 0).
SELECT p.IDPub,
       p.Texto,
       p.Fecha            AS FechaPublicacion,
       p.IDV              AS IDVideo,
       u.IDU              AS IDAutor,
       u.Nombre           AS Autor,
       u.Email            AS EmailAutor,
       COUNT(r.IDU)       AS TotalReacciones
FROM Publicacion p
JOIN Usuario u          ON u.IDU = p.IDU
LEFT JOIN Reaccionar r  ON r.IDPub = p.IDPub
GROUP BY p.IDPub, p.Texto, p.Fecha, p.IDV, u.IDU, u.Nombre, u.Email
ORDER BY TotalReacciones DESC, p.IDPub;
