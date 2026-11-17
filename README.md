# 🐠 AquaLife — Proyecto Final de Base de Datos

Plataforma digital de red social y comercio electrónico dedicada a conectar a entusiastas del acuarismo a nivel global. Este repositorio contiene la solución integral desarrollada para el proyecto final de la asignatura **Bases de Datos** (Licenciatura en Ciencia de Datos, Curso 2026-2027).

---

## 📋 Descripción del Proyecto

**AquaLife** es una comunidad global donde los usuarios comparten experiencias sobre el cuidado de peces, invertebrados, plantas acuáticas y corales, además de operar un *marketplace* especializado.

Asumiendo el rol de analistas de datos en *AquaSolutions* tras una reestructuración sin documentación previa, este proyecto abarca:
* **Ingeniería inversa** y modelado conceptual/lógico de la base de datos heredada.
* **Analítica avanzada en SQL** sobre el comportamiento de usuarios, *influencers* y detección de fraudes en vendedores.
* **Arquitectura políglota (SQL + NoSQL)** combinando **MySQL**, **Neo4j** y **MongoDB** para resolver conversaciones anidadas y documentación jerárquica de especies.
* **Panel de control interactivo en Streamlit** conectado directamente mediante consultas SQL nativas (sin uso de ORM).

---

## 🛠️ Stack Tecnológico

* **Base de Datos Relacional:** MySQL (desplegado en Docker).
* **Bases de Datos NoSQL:** 
  * **Neo4j** (Base de datos orientada a grafos para hilos de conversaciones).
  * **MongoDB** (Base de datos documental para fichas y documentación variable de especies).
* **Backend y Analítica:** Python con drivers nativos (`mysql-connector-python` / `pymysql`, `neo4j`, `pymongo`) cumpliendo la restricción de **cero ORM**.
* **Frontend / Dashboard:** Streamlit.
* **Modelado y Documentación:** Diagrams.net (`draw.io`) y generación automatizada de reportes en PDF.

---

## 📂 Estructura del Repositorio

```text
aqualife/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── generate_init_sql.py
├── 000-hash-init.sh
├── zzz-cleanup.sh
│
├── app/
│   ├── main.py
│   ├── db.py
│   ├── hilos.py
│   ├── documentos.py
│   ├── requirements.txt
│   └── pages/
│
├── sql/
│   ├── 01_consultas/
│   ├── 02_... - 06_... (.sql)
│   ├── cargar_sql.sh
│   └── LEEME.md
│
├── nosql/
│   ├── hilos_neo4j/
│   └── documentos_mongo/
│
└── docs/
    ├── MERX.png / .pdf / .drawio
    ├── Diseno_logico.png
    ├── Diseno_MERX_y_Logico_AquaLife.pdf
    ├── Informe_Tecnico.pdf
    ├── README_provisto.md
    └── informe/

