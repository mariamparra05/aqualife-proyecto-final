-- =====================================================================
-- 05_mejoras_diseno.sql  -  Propuesta de mejora del diseño lógico de AquaLife
-- Se ejecuta UNA vez, sobre la base AquaLife recién cargada (MySQL 8.0).
-- =====================================================================
USE AquaLife;

-- ---------------------------------------------------------------------
-- 1) Fecha de publicación (necesaria para 3.g y 3.h: la tabla original no la tiene)
--    Relleno determinista repartido en ~5 años (sin RAND, reproducible).
-- ---------------------------------------------------------------------
ALTER TABLE Publicacion ADD COLUMN Fecha DATE NULL;
UPDATE Publicacion
   SET Fecha = DATE_ADD('2021-01-01', INTERVAL MOD(IDPub * 7919, 1800) DAY);
ALTER TABLE Publicacion MODIFY Fecha DATE NOT NULL;

-- ---------------------------------------------------------------------
-- 2) Comentar con identificador propio, comentario padre (hilos) y fecha
--    Paso a: índices para las FK actuales (la PK (IDU, IDPub) las sostenía)
-- ---------------------------------------------------------------------
ALTER TABLE Comentar
  ADD INDEX idx_comentar_usuario (IDU),
  ADD INDEX idx_comentar_pub (IDPub);
--    Paso b: nueva clave primaria IDC y columnas nuevas
ALTER TABLE Comentar
  DROP PRIMARY KEY,
  ADD COLUMN IDC INT NOT NULL AUTO_INCREMENT FIRST,
  ADD PRIMARY KEY (IDC),
  ADD COLUMN IDC_Padre INT NULL,
  ADD COLUMN Fecha DATETIME NULL;
--    Paso c: relleno de Fecha (después de la publicación, tope 2026-01-01) y restricciones
UPDATE Comentar c
  JOIN Publicacion p ON p.IDPub = c.IDPub
   SET c.Fecha = TIMESTAMP(LEAST(DATE_ADD(p.Fecha, INTERVAL MOD(c.IDC, 400) DAY), '2026-01-01'));
ALTER TABLE Comentar MODIFY Fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE Comentar
  ADD INDEX idx_comentar_padre (IDC_Padre),
  ADD CONSTRAINT fk_comentar_padre FOREIGN KEY (IDC_Padre)
      REFERENCES Comentar(IDC) ON DELETE CASCADE ON UPDATE CASCADE;

-- ---------------------------------------------------------------------
-- 3) Tabla de auditoría de precios (la llena el trigger de la tarea 3.f)
-- ---------------------------------------------------------------------
ALTER TABLE Producto MODIFY Precio DECIMAL(10,2) NOT NULL;
ALTER TABLE Compra   MODIFY Precio DECIMAL(10,2) NOT NULL;

CREATE TABLE IF NOT EXISTS Historial_Precios (
  IDH INT NOT NULL AUTO_INCREMENT,
  IDProd INT NOT NULL,
  PrecioAnterior DECIMAL(10,2) NOT NULL,
  PrecioNuevo DECIMAL(10,2) NOT NULL,
  PorcentajeCambio DECIMAL(10,2) NULL,
  FechaHora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  Usuario VARCHAR(100) NOT NULL,
  PRIMARY KEY (IDH),
  INDEX idx_hist_prod_fecha (IDProd, FechaHora),
  FOREIGN KEY fk_hist_prod (IDProd) REFERENCES Producto(IDProd) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- 4) Restricciones de calidad de datos
-- ---------------------------------------------------------------------
ALTER TABLE Compra
  ADD CONSTRAINT ck_compra_puntuacion CHECK (Puntuacion IS NULL OR Puntuacion BETWEEN 1 AND 5),
  ADD CONSTRAINT ck_compra_cantidad CHECK (Cantidad > 0);
ALTER TABLE Producto ADD CONSTRAINT ck_producto_precio CHECK (Precio > 0);

-- comprador <> vendedor: no puede ser un CHECK (MySQL no lo permite en columnas con FK ... ON UPDATE CASCADE)
DROP TRIGGER IF EXISTS trg_compra_comprador_distinto;
DELIMITER $$
CREATE TRIGGER trg_compra_comprador_distinto BEFORE INSERT ON Compra
FOR EACH ROW
BEGIN
  IF NEW.IDUC = NEW.IDUV THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El comprador no puede ser el vendedor';
  END IF;
END$$
DELIMITER ;

-- ---------------------------------------------------------------------
-- 5) Catálogo de reacciones (polaridad y peso; usado en 3.b y 3.h)  [opcional]
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS TipoReaccion (
  Tipo CHAR(21) NOT NULL,
  Polaridad ENUM('positiva','negativa') NOT NULL,
  Peso DECIMAL(3,1) NOT NULL,
  PRIMARY KEY (Tipo)
);
INSERT INTO TipoReaccion (Tipo, Polaridad, Peso) VALUES
  ('Me gusta','positiva',1.0), ('Me encanta','positiva',2.0), ('Me asombra','positiva',1.5),
  ('Me divierte','positiva',0.0), ('Me entristece','negativa',0.0), ('Me enoja','negativa',0.0);
ALTER TABLE Reaccionar
  ADD CONSTRAINT fk_reaccionar_tipo FOREIGN KEY (Tipo) REFERENCES TipoReaccion(Tipo) ON UPDATE CASCADE;

-- ---------------------------------------------------------------------
-- 6) Vista del subtipo implícito EQUIPO y índices para las consultas analíticas
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW Vista_Equipo AS
  SELECT p.IDProd, p.Nombre, p.Descripcion, p.Precio
    FROM Producto p LEFT JOIN Especie e ON e.IDProd = p.IDProd
   WHERE e.IDProd IS NULL;

CREATE INDEX idx_compra_prod_fecha ON Compra (IDProd, Fecha);
CREATE INDEX idx_compra_vend_punt  ON Compra (IDUV, Puntuacion);
CREATE INDEX idx_reaccionar_fecha  ON Reaccionar (Fecha);
CREATE INDEX idx_contribucion_fecha ON Contribucion (Fecha);
