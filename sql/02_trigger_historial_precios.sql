-- 3.f Trigger de auditoria de precios.
-- Ejecutar con el cliente mysql (usa DELIMITER). Requiere haber ejecutado 05_mejoras_diseno.sql
-- (Precio en DECIMAL), aunque tambien funciona con FLOAT.
USE AquaLife;

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

DROP TRIGGER IF EXISTS trg_auditoria_precios;
DELIMITER $$
CREATE TRIGGER trg_auditoria_precios
AFTER UPDATE ON Producto
FOR EACH ROW
BEGIN
    IF NOT (OLD.Precio <=> NEW.Precio) THEN
        INSERT INTO Historial_Precios
            (IDProd, PrecioAnterior, PrecioNuevo, PorcentajeCambio, Usuario)
        VALUES
            (OLD.IDProd, OLD.Precio, NEW.Precio,
             CASE WHEN OLD.Precio = 0 THEN NULL
                  ELSE ROUND((NEW.Precio - OLD.Precio) / OLD.Precio * 100, 2) END,
             -- la aplicacion hace SET @usuario_app = '...' antes del UPDATE; si no, el usuario de MySQL
             COALESCE(@usuario_app, USER()));
    END IF;
END$$
DELIMITER ;
