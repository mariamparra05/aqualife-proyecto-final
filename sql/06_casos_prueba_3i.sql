-- Casos de prueba para 3.i (OPCIONAL). Los datos generados son aleatorios y no contienen vendedores
-- realmente sospechosos; este script inserta 1 vendedor y 10 compradores ficticios (IDU 2001 a 2011) que
-- cumplen los 4 patrones: precios con +40 % en el mismo mes, notas solo de 5 y 1,
-- compradores que solo compran a ese vendedor y precios 3 a 4 veces superiores al resto.
-- Se puede ejecutar varias veces: ignora los registros ya existentes.
USE AquaLife;
INSERT IGNORE INTO Usuario (IDU, Nombre, DireccionParticular, Email, FechaDeNacimiento, Notificaciones, ConfiguracionDePrivacidad)
VALUES (2001, 'Vendedor Sospechoso (prueba)', 'Calle Falsa 123', 'sospechoso.prueba@email.com', '1990-01-01', 'activada', 'No compartir');

INSERT IGNORE INTO Usuario (IDU, Nombre, DireccionParticular, Email, FechaDeNacimiento, Notificaciones, ConfiguracionDePrivacidad)
WITH RECURSIVE n AS (SELECT 2002 AS id UNION ALL SELECT id + 1 FROM n WHERE id < 2011)
SELECT id, CONCAT('Comprador Anillo ', id - 2001, ' (prueba)'), 'Calle Falsa 456',
       CONCAT('anillo', id - 2001, '.prueba@email.com'), '1992-05-05', 'activada', 'No compartir'
FROM n;

INSERT IGNORE INTO Compra (IDUC, IDUV, IDProd, Fecha, Opinion, Precio, Puntuacion, Cantidad)
WITH RECURSIVE k AS (SELECT 0 AS n UNION ALL SELECT n + 1 FROM k WHERE n < 5)
SELECT b.IDU, 2001, 1 + MOD(k.n, 3), DATE_ADD('2025-03-01', INTERVAL k.n DAY), 'Caso de prueba',
       ROUND(p.Precio * IF(MOD(k.n, 2) = 0, 3.0, 4.2), 2), IF(MOD(k.n, 2) = 0, 5, 1), 1
FROM Usuario b
CROSS JOIN k
JOIN Producto p ON p.IDProd = 1 + MOD(k.n, 3)
WHERE b.IDU BETWEEN 2002 AND 2011;
