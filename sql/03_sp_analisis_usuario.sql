-- 3.g Procedimiento almacenado sp_analisis_usuario(usuario, fecha_ini, fecha_fin)
-- Devuelve DOS resultados:
--   1) una fila con las metricas del periodo
--   2) una fila con la especie mas comprada y la especie mas contribuida
-- Requiere 05_mejoras_diseno.sql (Publicacion.Fecha y Comentar.Fecha).
-- Monto gastado = suma de Precio * Cantidad de las compras del usuario como comprador.
USE AquaLife;
DROP PROCEDURE IF EXISTS sp_analisis_usuario;
DELIMITER $$
CREATE PROCEDURE sp_analisis_usuario(
    IN p_usuario_id INT, IN p_fecha_ini DATE, IN p_fecha_fin DATE)
BEGIN
    DECLARE v_fin DATETIME;

    IF p_fecha_ini > p_fecha_fin THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha inicial no puede ser mayor que la final';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM Usuario WHERE IDU = p_usuario_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El usuario no existe';
    END IF;
    SET v_fin = DATE_ADD(p_fecha_fin, INTERVAL 1 DAY);   -- incluye todo el ultimo dia

    -- Resultado 1: metricas
    SELECT
      (SELECT COUNT(*) FROM Publicacion
        WHERE IDU = p_usuario_id AND Fecha >= p_fecha_ini AND Fecha < v_fin)            AS TotalPublicaciones,
      (SELECT COUNT(*) FROM Reaccionar
        WHERE IDU = p_usuario_id AND Fecha >= p_fecha_ini AND Fecha < v_fin)            AS ReaccionesDadas,
      (SELECT COUNT(*) FROM Reaccionar r JOIN Publicacion p ON p.IDPub = r.IDPub
        WHERE p.IDU = p_usuario_id AND r.Fecha >= p_fecha_ini AND r.Fecha < v_fin)      AS ReaccionesRecibidas,
      (SELECT COUNT(*) FROM Comentar
        WHERE IDU = p_usuario_id AND Fecha >= p_fecha_ini AND Fecha < v_fin)            AS TotalComentarios,
      (SELECT COUNT(*) FROM Compra
        WHERE IDUC = p_usuario_id AND Fecha >= p_fecha_ini AND Fecha < v_fin)           AS TotalCompras,
      (SELECT COALESCE(SUM(Precio * Cantidad), 0) FROM Compra
        WHERE IDUC = p_usuario_id AND Fecha >= p_fecha_ini AND Fecha < v_fin)           AS MontoGastado,
      (SELECT COUNT(*) FROM Contribucion
        WHERE IDU = p_usuario_id AND Fecha >= p_fecha_ini AND Fecha < v_fin)            AS TotalContribuciones;

    -- Resultado 2: especie mas comprada y mas contribuida (NULL si no hay actividad)
    SELECT
      (SELECT e.NombreComun FROM Compra c JOIN Especie e ON e.IDProd = c.IDProd
        WHERE c.IDUC = p_usuario_id AND c.Fecha >= p_fecha_ini AND c.Fecha < v_fin
        GROUP BY e.IDProd, e.NombreComun
        ORDER BY SUM(c.Cantidad) DESC, e.IDProd LIMIT 1)                                AS EspecieMasComprada,
      (SELECT e.NombreComun FROM Contribucion co JOIN Especie e ON e.IDProd = co.IDProd
        WHERE co.IDU = p_usuario_id AND co.Fecha >= p_fecha_ini AND co.Fecha < v_fin
        GROUP BY e.IDProd, e.NombreComun
        ORDER BY COUNT(*) DESC, e.IDProd LIMIT 1)                                       AS EspecieMasContribuida;
END$$
DELIMITER ;
