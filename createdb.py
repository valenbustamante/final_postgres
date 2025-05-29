import psycopg2 as p
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

conn = p.connect(host='dpg-d0kvhcbuibrs739t0bb0-a.oregon-postgres.render.com',
                            database="cdd_db",
                            user="cdd_user",
                            password="gXmnbB3JuFU3IpHYiwiZUdxbwxgHZY26", port='5432')


cur = conn.cursor()
cur.execute("SET search_path TO uninorte_db;")
cur.execute("""CREATE TABLE IF NOT EXISTS usuario (
    id VARCHAR PRIMARY KEY,
    email VARCHAR NOT NULL,
    contraseña VARCHAR NOT NULL,
    creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_usuario VARCHAR NOT NULL
)
""")


cur.execute("""CREATE TABLE IF NOT EXISTS datos (
    documento BIGINT PRIMARY KEY,
    tipo_documento VARCHAR NOT NULL,
    id VARCHAR REFERENCES usuario(id),
    país VARCHAR NOT NULL,
    ciudad VARCHAR NOT NULL,
    direccion VARCHAR NOT NULL,
    telefono BIGINT NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    nombre VARCHAR NOT NULL,
    apellido VARCHAR NOT NULL)"""
)


cur.execute("""
CREATE TABLE IF NOT EXISTS oferta (
    programa VARCHAR NOT NULL,
    id_programa SERIAL PRIMARY KEY,
    periodo INT NOT NULL,
    semestres INT NOT NULL,
    titulo VARCHAR NOT NULL,
    inscripcion REAL NOT NULL,
    matricula REAL NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS formulario (
    id_solicitud SERIAL PRIMARY KEY,
    documento BIGINT REFERENCES datos(documento),
    periodo INT NOT NULL,
    id_programa INT NOT NULL references oferta(id_programa),
    tipo_estudiante VARCHAR NOT NULL,
    semestre INT NOT NULL,
    universidad VARCHAR NOT NULL
)
""")


"""
Para guardar los documentos desde Python, usar:

with open("documento_tal.pdf", "rb") as f:
    pdf = f.read()

cur.execute("INSERT INTO anexos (id_solicitud, id_documento, tipo_doc, archivo) VALUES (%s, %s, %s, %s)",
            (1, 1, 'documento_tal', psycopg2.Binary(pdf)))

"""

cur.execute("""
CREATE TABLE IF NOT EXISTS asignaturas (
    id_asignatura SERIAL PRIMARY KEY,
    id_programa INT NOT NULL REFERENCES oferta(id_programa),
    nombre VARCHAR NOT NULL,
    creditos INT NOT NULL,
    semestre INT NOT NULL,
    nombre_asignatura VARCHAR NOT NULL,
    descripcion TEXT NOT NULL    
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS homologar (
    id_solicitud INT REFERENCES formulario(id_solicitud),
    estado VARCHAR,
    id_asignatura INT REFERENCES asignaturas(id_asignatura),
    justificacion TEXT,
    decision TEXT
)
""")



cur.execute("""
CREATE TABLE IF NOT EXISTS requisitos (
    id_programa INT NOT NULL REFERENCES oferta(id_programa),
    nombre_doc VARCHAR,
    tipo_req TEXT
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS anexos (
    id_documento SERIAL PRIMARY KEY,
    id_solicitud INT REFERENCES formulario(id_solicitud),
    nombre_doc VARCHAR,
    archivo BYTEA,
    aprobacion TEXT
);
""")


cur.execute(
"""
CREATE TABLE IF NOT EXISTS pagos(
id_solicitud INT NOT NULL REFERENCES formulario(id_solicitud),
estado VARCHAR,
fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)


cur.execute(
"""
CREATE TABLE IF NOT EXISTS aprobados(
id_solicitud INT NOT NULL REFERENCES formulario(id_solicitud),
aprobado_por VARCHAR,
fecha_aprobacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)







conn.commit()

cur.close()
conn.close()