-- 4.a Hilos de conversacion en el modelo relacional (lista de adyacencia).
-- Requiere 05_mejoras_diseno.sql (Comentar con IDC, IDC_Padre y Fecha).
-- Contiene: (1) trigger de integridad, (2) hilo de prueba con 22 subcomentarios,
-- (3) procedimiento sp_hilo_comentarios(IDC) que devuelve la conversacion completa.
-- Los IDC del hilo de prueba (2000001 a 2000023) deben ser los mismos en Neo4j (tarea 4.b).
USE AquaLife;

-- (1) Una respuesta debe pertenecer a la misma publicacion que su comentario padre
DROP TRIGGER IF EXISTS trg_comentar_misma_publicacion;
DELIMITER $$
CREATE TRIGGER trg_comentar_misma_publicacion BEFORE INSERT ON Comentar
FOR EACH ROW
BEGIN
    DECLARE v_pub INT;
    IF NEW.IDC_Padre IS NOT NULL THEN
        SELECT IDPub INTO v_pub FROM Comentar WHERE IDC = NEW.IDC_Padre;
        IF v_pub IS NULL OR v_pub <> NEW.IDPub THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La respuesta debe pertenecer a la misma publicacion que el comentario padre';
        END IF;
    END IF;
END$$
DELIMITER ;

-- (2) Hilo de diagnostico colaborativo (ich en un acuario). Publicacion 1; usuarios 1 a 4.
INSERT IGNORE INTO Comentar (IDC, IDU, IDPub, Comentario, IDC_Padre, Fecha) VALUES
(2000001, 1, 1, 'Mi pez tiene puntitos blancos en las aletas y no come. Que puede ser?', NULL, '2026-01-02 09:00:00'),
(2000002, 2, 1, 'Parece ich. Cual es la temperatura del agua?', 2000001, '2026-01-02 09:17:00'),
(2000003, 1, 1, '26 grados. Agregue dos peces nuevos hace una semana.', 2000002, '2026-01-02 09:34:00'),
(2000004, 3, 1, 'Eso encaja: el estres del traslado favorece el ich. Mide amoniaco y nitritos.', 2000003, '2026-01-02 09:51:00'),
(2000005, 1, 1, 'Amoniaco 0, nitritos 0.25, nitratos 20.', 2000004, '2026-01-02 10:08:00'),
(2000006, 2, 1, 'Nitritos 0.25 ya es alto. Haz un cambio de agua del 30 por ciento hoy.', 2000005, '2026-01-02 10:25:00'),
(2000007, 1, 1, 'Hecho. Subo la temperatura?', 2000006, '2026-01-02 10:42:00'),
(2000008, 3, 1, 'Sube poco a poco hasta 28-29 grados, 1 grado cada 3 horas.', 2000007, '2026-01-02 10:59:00'),
(2000009, 4, 1, 'Ojo: si tienes invertebrados no uses cobre.', 2000008, '2026-01-02 11:16:00'),
(2000010, 1, 1, 'Solo hay peces y plantas. Que tratamiento recomiendan?', 2000009, '2026-01-02 11:33:00'),
(2000011, 2, 1, 'Sal de acuario o un tratamiento especifico para ich durante 10 dias.', 2000010, '2026-01-02 11:50:00'),
(2000012, 4, 1, 'Yo use 1 gramo de sal por litro y funciono. Retira el carbon activado.', 2000011, '2026-01-02 12:07:00'),
(2000013, 1, 1, 'Retire el carbon. Debo apagar la luz?', 2000012, '2026-01-02 12:24:00'),
(2000014, 3, 1, 'Luz tenue ayuda a reducir el estres, no hace falta oscuridad total.', 2000013, '2026-01-02 12:41:00'),
(2000015, 4, 1, 'La proxima vez pon en cuarentena a los peces nuevos.', 2000004, '2026-01-02 12:58:00'),
(2000016, 1, 1, 'Anotado, no tenia tanque de cuarentena.', 2000015, '2026-01-02 13:15:00'),
(2000017, 2, 1, 'Un recipiente de 20 litros con filtro de esponja es suficiente.', 2000016, '2026-01-02 13:32:00'),
(2000018, 4, 1, 'Y no compartas redes ni accesorios entre acuarios.', 2000017, '2026-01-02 13:49:00'),
(2000019, 3, 1, 'Alternativa: subir la temperatura y cambios de agua diarios del 20 por ciento.', 2000011, '2026-01-02 14:06:00'),
(2000020, 1, 1, 'Pruebo eso. Cuanto dura el ciclo del parasito?', 2000019, '2026-01-02 14:23:00'),
(2000021, 2, 1, 'A 28 grados, unos 4 a 6 dias por ciclo.', 2000020, '2026-01-02 14:40:00'),
(2000022, 1, 1, 'Gracias, en 3 dias ya veo mejoria. Les cuento.', 2000021, '2026-01-02 14:57:00'),
(2000023, 4, 1, 'Excelente. Mantén el tratamiento hasta completar los 10 dias.', 2000022, '2026-01-02 15:14:00');

-- (3) Conversacion completa a partir de un comentario inicial.
-- Devuelve cada comentario con su profundidad; el orden (ruta) deja cada respuesta bajo su padre.
DROP PROCEDURE IF EXISTS sp_hilo_comentarios;
DELIMITER $$
CREATE PROCEDURE sp_hilo_comentarios(IN p_idc INT)
BEGIN
    WITH RECURSIVE hilo AS (
        SELECT c.IDC, c.IDC_Padre, c.IDPub, c.IDU, c.Comentario, c.Fecha,
               0 AS Profundidad,
               CAST(LPAD(c.IDC, 10, '0') AS CHAR(1000)) AS Ruta
        FROM Comentar c WHERE c.IDC = p_idc
        UNION ALL
        SELECT c.IDC, c.IDC_Padre, c.IDPub, c.IDU, c.Comentario, c.Fecha,
               h.Profundidad + 1,
               CONCAT(h.Ruta, '/', LPAD(c.IDC, 10, '0'))
        FROM Comentar c JOIN hilo h ON c.IDC_Padre = h.IDC
    )
    SELECT h.IDC, h.IDC_Padre, h.Profundidad, h.IDU, u.Nombre AS Autor, h.Comentario, h.Fecha
    FROM hilo h JOIN Usuario u ON u.IDU = h.IDU
    ORDER BY h.Ruta;
END$$
DELIMITER ;
