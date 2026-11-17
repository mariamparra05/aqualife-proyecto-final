# Tarea 5: justificación del modelo de datos para las fichas de especie

**Elección: base de datos documental (MongoDB).** Cada especie tiene un documento principal (Ficha de Especie) que contiene un arreglo `documentos_secundarios` (certificado sanitario, guía de alimentación estacional, manual de tratamiento de enfermedades, historial de crecimiento, análisis de agua). El campo `especie_id` es el mismo `Especie.IDProd` de MySQL.

**Por qué es la solución más apropiada**
- **Estructura variable.** Un análisis de agua de un coral incluye densidad, calcio y magnesio; el de una planta, CO2 y hierro; el de un pez de agua fría, otros rangos de temperatura. Cada categoría tiene además distintos tipos de documento (una planta no lleva certificado sanitario de parásitos). En un modelo relacional esto exigiría muchas columnas casi siempre nulas, una tabla por tipo de documento o un esquema clave-valor (EAV) difícil de consultar. En un documento, cada elemento guarda solo los campos que le corresponden.
- **Jerarquía natural.** La ficha y sus documentos forman un árbol (1 principal > N secundarios). Incrustar los secundarios en el documento principal refleja esa jerarquía y permite recuperar todo con una sola lectura (`find_one({"especie_id": id})`), sin uniones.
- **Patrón de acceso.** Siempre se consulta la ficha completa de una especie antes de comprarla o cuidarla; casi no hay consultas que crucen especies entre sí. Es el caso para el que están pensados los documentos.
- **Evolución.** Agregar un nuevo tipo de documento (por ejemplo, "Guía de reproducción") no requiere migrar el esquema.
- **Integridad mínima.** Se define un validador (`$jsonSchema`) que exige `especie_id`, `nombre_comun`, `categoria` y el arreglo de documentos, y un índice único sobre `especie_id`.

**Limitaciones.** No hay claves foráneas: la coincidencia del `especie_id` con MySQL la garantiza el script de carga (los datos de la ficha se leen de MySQL). Si los documentos secundarios crecieran mucho o necesitaran actualizarse de forma independiente, se podría pasar a referencias en una colección aparte.

**Datos de prueba.** 8 fichas (2 por categoría: pez, invertebrado, planta y coral), cada una con 3 a 5 documentos secundarios de tipos diferentes.
