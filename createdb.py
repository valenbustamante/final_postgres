import psycopg2 as p
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = p.connect(
        host='localhost',
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        port='5432'
    )
    
    # Verificar la conexión
    if conn:
        cur = conn.cursor()
        
        cur.execute("CREATE SCHEMA IF NOT EXISTS uninorte_db;")
        cur.execute("SET search_path TO uninorte_db;")
        

        cur.execute("""CREATE TABLE IF NOT EXISTS usuario (
            id VARCHAR PRIMARY KEY,
            email VARCHAR NOT NULL,
            contraseña VARCHAR NOT NULL,
            creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo_usuario VARCHAR NOT NULL
        )""")
        print("Tabla usuario creada")

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

        
except p.Error as e:
    print(f"Error de PostgreSQL: {e}")
except Exception as e:
    print(f"Error general: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
        