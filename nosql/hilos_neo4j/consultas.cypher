// Modelo: (:Usuario {idu, nombre})-[:ESCRIBIO]->(:Comentario {idc, texto, fecha})
//         (:Comentario)-[:RESPONDE_A]->(:Comentario)     // el hijo apunta a su padre
// Los idc son los mismos Comentar.IDC de MySQL.

// Restricciones (unicidad)
CREATE CONSTRAINT usuario_idu IF NOT EXISTS FOR (u:Usuario) REQUIRE u.idu IS UNIQUE;
CREATE CONSTRAINT comentario_idc IF NOT EXISTS FOR (c:Comentario) REQUIRE c.idc IS UNIQUE;

// Conversacion completa a partir de un comentario inicial (ejemplo: 2000001)
MATCH path = (c:Comentario)-[:RESPONDE_A*0..]->(raiz:Comentario {idc: 2000001})
MATCH (u:Usuario)-[:ESCRIBIO]->(c)
RETURN c.idc, length(path) AS profundidad, u.nombre, c.texto
ORDER BY c.idc;

// Cuantos comentarios tiene el hilo
MATCH (c:Comentario)-[:RESPONDE_A*0..]->(:Comentario {idc: 2000001}) RETURN count(c);
