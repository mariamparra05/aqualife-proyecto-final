from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, NextPageTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, Preformatted, ListFlowable, ListItem, Image)
from PIL import Image as PI

import os, json
from pathlib import Path
from xml.sax.saxutils import escape
HERE = Path(__file__).resolve().parent
DOCS = HERE.parent
OUT = os.environ.get("INFORME_OUT") or str(DOCS / "Informe_Tecnico.pdf")
try:
    D = json.load(open(HERE / "datos.json", encoding="utf-8"))
except Exception:
    D = {}
NAVY = colors.HexColor("#12355B"); TEAL = colors.HexColor("#1B7F8C"); LIGHT = colors.HexColor("#EAF3F6"); GREY = colors.HexColor("#F4F4F4")
ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["Normal"], fontName="Helvetica", fontSize=10, leading=14, spaceAfter=5, alignment=4)
cell = ParagraphStyle("c", parent=body, fontSize=8.6, leading=11, spaceAfter=0, alignment=0)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=10, spaceAfter=6, alignment=0)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=TEAL, spaceBefore=8, spaceAfter=3, alignment=0)
title = ParagraphStyle("t", parent=body, fontName="Helvetica-Bold", fontSize=26, leading=31, textColor=NAVY, spaceAfter=6, alignment=0)
sub = ParagraphStyle("s", parent=body, fontSize=12, leading=16, textColor=colors.HexColor("#444444"), alignment=0)
cs = ParagraphStyle("code", fontName="Courier", fontSize=7.8, leading=9.8)
def V(key, hint):
    v = str(D.get(key, '')).strip()
    return escape(v).replace('\n', '<br/>') if v else RED(hint)
RED = lambda t: f"<font color='#B00020'><b>[COMPLETAR: {t}]</b></font>"
F = lambda s: "<font face='Courier'>%s</font>" % s
def P(t, s=body): return Paragraph(t, s)
def B(items): return ListFlowable([ListItem(Paragraph(i, body), leftIndent=12) for i in items], bulletType="bullet", bulletFontSize=7, leftIndent=12, bulletOffsetY=-1)
def C(t):
    tb = Table([[Preformatted(t.strip("\n"), cs)]], colWidths=[17*cm])
    tb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),GREY),("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#CCCCCC")),("LEFTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    return tb
def T(rows, widths):
    data = [[Paragraph(str(c), cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w*cm for w in widths], repeatRows=1)
    st = [("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#BBBBBB")),("BACKGROUND",(0,0),(-1,0),NAVY),
          ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3)]
    for i in range(2, len(rows), 2): st.append(("BACKGROUND",(0,i),(-1,i),LIGHT))
    t.setStyle(TableStyle(st)); return t
def fig(path, maxw, maxh):
    w, h = PI.open(path).size; k = min(maxw*cm/w, maxh*cm/h); return Image(path, width=w*k, height=h*k)
def foot(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.HexColor("#777777")); pw, ph = c._pagesize
    if d.page > 1:
        c.drawString(1.8*cm, 0.9*cm, "Informe técnico - Proyecto AquaLife - Bases de Datos 2026-2027"); c.drawRightString(pw-1.8*cm, 0.9*cm, "Pág. %d" % d.page)
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, title="Informe técnico - Proyecto AquaLife", author="Equipo AquaLife")
doc.addPageTemplates([PageTemplate(id='p', frames=[Frame(2*cm, 1.7*cm, A4[0]-4*cm, A4[1]-3.5*cm)], onPage=foot, pagesize=A4),
                      PageTemplate(id='l', frames=[Frame(1*cm, 1.3*cm, landscape(A4)[0]-2*cm, landscape(A4)[1]-2.2*cm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=foot, pagesize=landscape(A4))])
S = []
# ---------------- portada
S += [Spacer(1, 3.5*cm), P("Informe técnico", title), P("Proyecto final: AquaLife", ParagraphStyle("x", parent=title, fontSize=20, leading=24, textColor=TEAL)),
      Spacer(1, 0.8*cm), P("Bases de Datos - Licenciatura en Ciencia de Datos<br/>Facultad de Matemática y Computación, Universidad de La Habana - Curso 2026-2027", sub),
      Spacer(1, 1.2*cm), P("Integrantes: " + V("integrantes", "nombre y apellidos de los tres integrantes"), sub),
      P("Profesor: " + V("profesor", "nombre del profesor"), sub), P("Fecha de entrega: " + V("fecha", "fecha"), sub),
      Spacer(1, 1.5*cm),
      P("Repositorio: " + V("repositorio", "enlace del repositorio de GitHub"), sub), PageBreak()]

# ---------------- 1
S += [P("1. Introducción", h1),
      P("AquaSolutions, creadora de la red social de acuarismo AquaLife, nos encargó entender una base de datos sin documentación, extraer información de uso, proponer mejoras al diseño y construir herramientas para sus directivos. "
        "Este informe describe cómo se hizo la ingeniería inversa, qué decisiones de diseño se tomaron, cómo se resolvió cada tarea y qué limitaciones tiene la solución."),
      P("<b>Tecnologías:</b> MySQL 8.0 (base relacional), MongoDB (documentos de especies), Neo4j (hilos de comentarios como grafo), Streamlit con <i>mysql-connector-python</i>, <i>pymongo</i> y <i>neo4j</i> (sin ORM) y Docker Compose para el despliegue."),
      P("<b>Estructura del repositorio:</b> " + F("docs/") + " (MERX, diseño lógico y este informe), " + F("sql/") + " (scripts de MySQL), " + F("nosql/") + " (Neo4j y MongoDB) y " + F("app/") + " (aplicación Streamlit). "
        "Las instrucciones de instalación están en el README.")]

# ---------------- 2
S += [P("2. Ingeniería inversa y MERX", h1),
      P("El archivo <i>init.sql</i> no está disponible dentro del contenedor (se genera durante la construcción de la imagen y luego se elimina). "
        "El esquema se obtuvo del script generador <i>generate_init_sql.py</i> y se comprobó contra la base cargada con " + F("SHOW CREATE TABLE") + " y las claves foráneas de " + F("information_schema") + ". "
        "La base tiene 17 tablas y, en la configuración por defecto, cerca de 1,1 millones de filas en las tablas de relaciones grandes (comentarios, reacciones, compras, entre otras)."),
      P("Hallazgos principales", h2),
      T([["Hallazgo","Consecuencia"],
         ["No existe una tabla de vendedores: el vendedor es un Usuario (Compra.IDUV). No hay \"tiendas\" ni \"criadores\".","Las consultas 3.e y 3.i usan Compra.IDUV; se documenta como suposición."],
         ["La calificación es Compra.Puntuacion (1 a 5, opcional); no hay tablas de calificaciones.","Las calificaciones de especies y equipos salen de Compra y Producto."],
         ["Los equipos no tienen tabla: son los Producto que no están en Especie.","Se modela como subclase implícita; se propone una vista."],
         ["Comentar tiene clave (IDU, IDPub): sin identificador de comentario y un solo comentario por usuario y publicación.","Se rediseña para permitir hilos (sección 4)."],
         ["Publicacion y Comentar no tienen fecha.","Se añaden para poder resolver 3.g y 3.h."],
         ["Las bitácoras de mantenimiento son Contribucion (clave: especie y fecha).","Solo cabe una contribución por especie y día."]],
        [9, 8]),
      P("Decisiones del MERX", h2),
      B(["<b>PRODUCTO se especializa en ESPECIE y EQUIPO</b> (disjunta y total). ESPECIE existe como tabla y hereda IDProd; EQUIPO es implícita.",
         "<b>CONTRIBUCIÓN es una entidad débil</b> de ESPECIE, identificada por (IDProd, Fecha); la relación identificadora es TIENE_CONTRIBUCIÓN.",
         "<b>COMPRA es una relación ternaria</b> (comprador, vendedor, producto) con Fecha, Opinion, Precio, Puntuacion y Cantidad; se identifica por (comprador, producto, fecha) y determina un único vendedor.",
         "<b>COMENTA y REACCIONA</b> son relaciones N:M entre USUARIO y PUBLICACIÓN con atributos; <b>Edad</b> es un atributo derivado de la fecha de nacimiento.",
         "Un mismo USUARIO cumple los roles de autor, comprador, vendedor y contribuyente."])]
S += [NextPageTemplate('l'), PageBreak(), fig(str(DOCS / 'MERX.png'), 27.6, 18.6), NextPageTemplate('p'), PageBreak()]

# ---------------- 3
S += [P("3. Diseño lógico", h1),
      P("El MERX se transformó al modelo relacional con estas reglas: entidades fuertes en una tabla con su clave; la subclase ESPECIE toma la clave de PRODUCTO (PK y FK a la vez); "
        "la entidad débil CONTRIBUCIÓN usa como clave la de ESPECIE más la fecha; las relaciones 1:N llevan una clave foránea en el lado N; las N:M se convierten en tablas intermedias con clave compuesta "
        "(con sus atributos cuando los tienen); la relación ternaria COMPRA se convierte en una tabla con las tres claves foráneas, y el atributo derivado Edad no se almacena."),
      P("<b>Normalización.</b> Con las dependencias funcionales deducidas del esquema, todas las relaciones están en forma normal de Boyce-Codd. En Compra, (IDUC, IDProd, Fecha) determina los demás atributos; "
        "Precio no es redundante respecto a Producto.Precio porque guarda el precio histórico pagado."),
      P("<b>Restricciones.</b> La base impone claves primarias y foráneas, unicidad del correo y comprobaciones de valores en tres columnas. No impone el rango de Puntuacion, que Cantidad y Precio sean positivos, ni que comprador y vendedor sean distintos; "
        "las mejoras de la sección 4 cubren estos casos.")]
S += [NextPageTemplate('l'), PageBreak(), fig(str(DOCS / 'Diseno_logico.png'), 27.6, 18.6), NextPageTemplate('p'), PageBreak()]

# ---------------- 4
S += [P("4. Propuesta de mejora del diseño (script 05_mejoras_diseno.sql)", h1),
      T([["#","Cambio","Motivo"],
         ["1","Publicacion.Fecha (DATE NOT NULL)","Sin fecha de publicación no se pueden contar publicaciones por período (3.g) ni medir ventas antes y después de una publicación (3.h)."],
         ["2","Comentar con IDC (clave), IDC_Padre (clave foránea a sí misma) y Fecha","Permite hilos (4.a), identifica cada comentario para compararlo con Neo4j (4.b) y habilita 3.g."],
         ["3","Tabla Historial_Precios y Precio FLOAT a DECIMAL(10,2)","Auditoría del trigger y cálculo exacto del porcentaje de cambio."],
         ["4","CHECK en Puntuacion (1 a 5), Cantidad (&gt; 0) y Precio (&gt; 0); trigger comprador distinto de vendedor","Calidad de datos. MySQL no permite un CHECK sobre columnas con claves foráneas ON UPDATE CASCADE; por eso es un trigger."],
         ["5","Tabla TipoReaccion (polaridad y peso) [opcional]","Clasifica reacciones positivas y negativas y pondera el puntaje de influencers."],
         ["6","Vista Vista_Equipo e índices en Compra, Reaccionar y Contribucion","Hace explícito el subtipo implícito y mejora las consultas con más de un millón de filas."]],
        [0.7, 6.3, 10]),
      P("<b>Supuestos.</b> Las fechas de publicación y de comentario de los datos existentes se rellenan de forma determinista y artificial, porque los datos originales no las tienen; "
        "las reacciones existentes tienen fechas aleatorias independientes, por lo que no siempre son posteriores a la publicación. La polaridad de las reacciones es positiva para Me gusta, Me encanta, Me asombra y Me divierte, y negativa para Me entristece y Me enoja. "
        "La contribución mantiene su clave original (una por especie y día), que se señala como limitación."),]

# ---------------- 5
S += [P("5. Consultas analíticas, trigger y procedimiento (tarea 3)", h1),
      T([["Ejercicio","Enfoque","Supuestos y decisiones"],
         ["3.a","JOIN de Publicacion, Usuario y un LEFT JOIN con Reaccionar, agrupado por publicación.","LEFT JOIN para que las publicaciones sin reacciones aparezcan con 0."],
         ["3.b","SUM de condiciones booleanas sobre el tipo de reacción y HAVING Positivas &gt; Negativas.","Polaridad definida en la sección 4."],
         ["3.c","Edad con TIMESTAMPDIFF; rango = FLOOR((edad-1)/10)*10+1; porcentaje con SUM(COUNT(*)) OVER ().","Edad calculada a la fecha actual."],
         ["3.d","CTE y ROW_NUMBER() OVER (PARTITION BY tipo de agua) para la especie y la categoría más populares.","Empates por IDProd o nombre de categoría. Bitácora = Contribucion."],
         ["3.e","Agregación sobre Compra por vendedor, LEFT JOIN con Especie para separar especies y equipos; TOP 5.","Vendedor = Usuario; mínimo 5 ventas calificadas."],
         ["3.f","Trigger AFTER UPDATE sobre Producto que escribe en Historial_Precios solo si el precio cambia (operador &lt;=&gt;).","Porcentaje = (nuevo-anterior)/anterior*100, NULL si el anterior es 0. Usuario = variable de sesión @usuario_app (la app) o USER()."],
         ["3.g","Procedimiento con parámetros IN, validación con SIGNAL (fechas invertidas y usuario inexistente) y dos resultados.","El último día se incluye completo (fecha &lt; fin + 1 día). Monto = suma de Precio por Cantidad."],
         ["3.h","Puntaje ponderado, TOP 5, especies de mayor interacción, ventas 14 días antes y después, y tasa de conversión.","Publicacion no se relaciona con especies: se usan contribuciones y compras. La correlación se calcula en la app."],
         ["3.i","Una CTE por patrón con puntuación de 0 a 1 y evidencia; índice = 0,30·P1 + 0,25·P2 + 0,25·P3 + 0,20·P4.","Umbrales: variación &gt; 30 % en el mismo mes; 10 o más ventas con más de 25 % de cada extremo; 5 o más compradores con 80 % exclusivos; z &gt; 2 en productos con 3 o más vendedores."]],
        [1.4, 8, 7.6]),
      P("<b>Nota sobre los datos.</b> Los datos generados son aleatorios, por lo que los patrones sospechosos de 3.i no aparecen de forma natural. Se incluye un script opcional (06_casos_prueba_3i.sql) que inserta un vendedor ficticio con los cuatro patrones para demostrar la consulta.")]

# ---------------- 6
S += [P("6. Hilos de comentarios (tarea 4)", h1),
      P("<b>4.a Modelo relacional.</b> Lista de adyacencia: " + F("Comentar(IDC, IDU, IDPub, Comentario, IDC_Padre, Fecha)") + ", con clave foránea de IDC_Padre a IDC y borrado en cascada. "
        "Un trigger exige que la respuesta pertenezca a la misma publicación que su padre. Se generó un hilo de diagnóstico de un caso de ich con 22 respuestas (IDC 2000001 a 2000023, profundidad 13) y el procedimiento " + F("sp_hilo_comentarios") + " devuelve la conversación completa con una consulta recursiva (WITH RECURSIVE) ordenada por una ruta con ceros a la izquierda."),
      P("<b>4.b Modelo de grafo (Neo4j).</b> Nodos " + F("(:Usuario)") + " y " + F("(:Comentario)") + ", con las relaciones " + F("ESCRIBIO") + " y " + F("RESPONDE_A") + " (del hijo al padre). Los identificadores son los mismos IDC. "
        "La conversación se obtiene con el patrón " + F("(c)-[:RESPONDE_A*0..]->(raiz {idc: $idc})") + ". La aplicación puede mostrar el hilo desde cualquiera de los dos modelos y verifica que devuelvan los mismos IDC."),
      P("4.c Comparación", h2),
      T([["Criterio","Relacional (MySQL)","Grafo (Neo4j)"],
         ["Recuperar un hilo","Consulta recursiva; más larga y con ordenamiento explícito","Un patrón de camino; es la operación natural"],
         ["Integridad","Claves foráneas, trigger de misma publicación, transacciones ACID","Unicidad del idc; el resto lo valida la aplicación"],
         ["Relación con el negocio","JOIN directo con usuarios, publicaciones y compras","Los demás datos no están en el grafo; hay que duplicarlos o usar dos sistemas"],
         ["Análisis de la red de respuestas","Posible con recursión pesada","Muy natural (caminos, vecinos, comunidades)"],
         ["Profundidad y volumen","Límite de recursión (cte_max_recursion_depth) y coste por nivel","Recorrido por adyacencia; escala bien en hilos profundos"],
         ["Esquema","Rígido; cambios con ALTER TABLE sobre más de un millón de filas","Flexible; propiedades y relaciones nuevas sin migrar"],
         ["Operación","Una sola base, ya existente","Un motor más que desplegar y mantener; hay que mantener la sincronía"]],
        [3.4, 6.8, 6.8]),
      Spacer(1, 4),
      P("<b>Conclusión.</b> En este escenario los comentarios están muy ligados a usuarios, publicaciones y compras, y se necesitan integridad referencial y transacciones. "
        "El modelo relacional con consulta recursiva resuelve bien el caso y debe ser la fuente de verdad. El grafo ofrece ventaja para analizar las conversaciones como red y para hilos muy profundos; "
        "una arquitectura razonable es MySQL como base principal y Neo4j como índice de lectura para análisis."),
      P("Mediciones: " + V("mediciones_hilos", "tiempo de la consulta recursiva en MySQL (EXPLAIN ANALYZE) y de la consulta en Neo4j (PROFILE) para el hilo de 23 comentarios") + ".")]

# ---------------- 7
S += [P("7. Documentos jerárquicos de especies (tarea 5)", h1),
      P("<b>Modelo elegido: base de datos documental (MongoDB).</b> Cada especie tiene un documento principal (Ficha de Especie) con un arreglo " + F("documentos_secundarios") + " incrustado. El campo " + F("especie_id") + " es el mismo Especie.IDProd de MySQL."),
      B(["<b>Estructura variable.</b> El análisis de agua de un coral incluye densidad, calcio y magnesio; el de una planta, CO2 y hierro; los rangos de temperatura cambian con el tipo de agua. Cada categoría tiene además tipos de documento distintos. "
         "En un modelo relacional esto exigiría columnas casi siempre nulas, una tabla por tipo de documento o un esquema clave-valor difícil de consultar.",
         "<b>Jerarquía natural.</b> La ficha y sus documentos forman un árbol; al incrustarlos se recupera todo con una sola lectura " + F("find_one({'especie_id': id})") + ", sin uniones.",
         "<b>Patrón de acceso.</b> Siempre se consulta la ficha completa de una especie; casi no hay consultas que crucen especies entre sí.",
         "<b>Evolución.</b> Un nuevo tipo de documento no requiere migrar el esquema. Se define un validador $jsonSchema y un índice único sobre especie_id."]),
      P("<b>Datos de prueba:</b> 8 fichas (2 por categoría: pez, invertebrado, planta y coral) con 3 a 5 documentos secundarios de tipos diferentes. Los datos de la ficha se leen de MySQL, lo que garantiza que los identificadores coincidan. "
        "<b>Limitaciones:</b> no hay claves foráneas entre MongoDB y MySQL; si los documentos secundarios crecieran mucho o se actualizaran por separado, convendría usar referencias en otra colección.")]

# ---------------- 8
S += [P("8. Aplicación Streamlit", h1),
      P("La aplicación tiene una página de inicio con prueba de conexiones y cinco pantallas, todas con manejo de errores mediante try/except y mensajes claros. "
        "El acceso a datos está en tres módulos: " + F("db.py") + " (conexiones y funciones <i>run_query</i>, <i>run_command</i>, <i>run_transaction</i> y <i>call_procedure</i>), " + F("hilos.py") + " y " + F("documentos.py") + "."),
      T([["Pantalla","Funcionalidad"],
         ["Selector de consultas","Desplegable que lee los archivos de sql/01_consultas, muestra el SQL, ejecuta y presenta una tabla con descarga CSV; para 3.h calcula la correlación de Pearson."],
         ["Análisis de usuario","Entrada de usuario y fechas; llama a sp_analisis_usuario y muestra métricas, un gráfico de reacciones y las especies destacadas."],
         ["Gestión de conversaciones","Hilos desde MySQL o Neo4j, navegación por ramas con sangría, respuesta a cualquier comentario y creación de comentarios nuevos."],
         ["Explorador de documentos","Selecciona una especie y muestra la ficha y los documentos secundarios en pestañas."],
         ["Gestor de precios","Lista y filtra productos, cambia el precio (SET @usuario_app y UPDATE en una misma transacción) y muestra el historial registrado por el trigger."]],
        [4.3, 12.7]),
      P("<b>Restricciones técnicas cumplidas:</b> no se usa ningún ORM; todo el acceso usa bibliotecas nativas (mysql-connector-python, pymongo, neo4j) con consultas SQL escritas explícitamente y siempre parametrizadas (marcadores %s), lo que evita la inyección de SQL.")]

# ---------------- 9
S += [P("9. Otras consideraciones técnicas", h1),
      B(["<b>Seguridad:</b> consultas parametrizadas; las credenciales por defecto son las del docker-compose provisto y pueden cambiarse con variables de entorno o un archivo .env que no se sube al repositorio (.gitignore).",
         "<b>Rendimiento:</b> índices compuestos en Compra (IDProd, Fecha) y (IDUV, Puntuacion), y en Reaccionar y Contribucion por fecha; las consultas 3.h y 3.i agregan sobre más de un millón de filas. " + V("tiempos_3h_3i", "tiempos medidos de 3.h y 3.i con la base completa"),
         "<b>Reproducibilidad:</b> la generación de datos usa una semilla fija; los scripts SQL se cargan en orden con sql/cargar_sql.sh y son repetibles (DROP IF EXISTS, INSERT IGNORE).",
         "<b>Limitaciones:</b> los datos son aleatorios (los patrones de 3.i requieren los casos de prueba); las fechas de publicaciones y comentarios existentes son un relleno artificial; no existe distinción entre tiendas y criadores; "
         "la clave de Contribucion limita a una contribución por especie y día; la sincronización con Neo4j es manual o disparada desde la aplicación.",
         "<b>Trabajo futuro:</b> perfil de vendedor (tienda o criador), clave propia en Contribucion, sincronización automática MySQL a Neo4j y catálogo de reacciones con FK obligatoria."])]

# ---------------- 10
S += [P("10. Pruebas realizadas", h1),
      T([["Prueba","Resultado esperado","Resultado obtenido"],
         ["Despliegue con docker compose up -d --build","Servicios en ejecución; MySQL healthy",V("prueba_1", "ok / observaciones")],
         ["Carga de scripts SQL (cargar_sql.sh --pruebas)","Sin errores; 19 tablas más la vista",V("prueba_2", "ok")],
         ["Consultas 3.a a 3.e, 3.h y 3.i en el Selector","Tablas con filas; 3.e y 3.h con 5 filas",V("prueba_3", "tiempos")],
         ["Trigger: UPDATE de un precio","Una fila en Historial_Precios con el porcentaje correcto",V("prueba_4", "captura")],
         ["Procedimiento sp_analisis_usuario","Métricas correctas; error con usuario inexistente o fechas invertidas",V("prueba_5", "captura")],
         ["Hilo de 23 comentarios en MySQL y en Neo4j","Mismos IDC en ambos modelos",V("prueba_6", "captura")],
         ["Fichas en MongoDB (8)","8 fichas con 3 o más tipos de documento",V("prueba_7", "captura")],
         ["Instalación desde un clon limpio siguiendo el README","Aplicación funcionando",V("prueba_8", "ok")]],
        [6, 6, 5]),
      P("11. Conclusiones", h1),
      P("Se reconstruyó el modelo conceptual y lógico de AquaLife, se detectaron carencias del diseño (fechas, identificador de comentarios, tipos de dato) y se propusieron mejoras comprobadas con scripts repetibles. "
        "Se resolvieron las nueve consultas, el trigger y el procedimiento; se compararon dos modelos para los hilos y se justificó el modelo documental para las fichas. "
        "La aplicación integra tres motores de bases de datos sin ORM. " + V("reflexion", "reflexión final y reparto de tareas del equipo"))]
doc.build(S); print("ok")
