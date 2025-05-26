import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host='localhost',
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        port='5432'
    )

def insert_test_data():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # 1. Insert test users
        test_users = [
            ('ADMIN001', 'admin@test.com', 'admin123', 'ADMINISTRADOR'),
            ('EST001', 'estudiante1@test.com', 'est123', 'ESTUDIANTE'),
            ('EST002', 'estudiante2@test.com', 'est123', 'ESTUDIANTE'),
            ('EST003', 'estudiante3@test.com', 'est123', 'ESTUDIANTE'),
            ('EST0073', 'estudiante3@test.com', 'est123', 'ESTUDIANTE')
        ]
        
        for user in test_users:
            cur.execute(
                "INSERT INTO usuario (id, email, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                user
            )
        
        # 2. Insert test personal data
        test_data = [
            (1234567890, 'CC', 'EST001', 'Colombia', 'Bogotá', 'Calle 123', 3001234567, '2000-01-01', 'Juan', 'Pérez'),
            (2345678901, 'CC', 'EST002', 'Colombia', 'Medellín', 'Carrera 456', 3002345678, '2000-02-02', 'María', 'González'),
            (3456789012, 'CC', 'EST003', 'Colombia', 'Cali', 'Avenida 789', 3003456789, '2000-03-03', 'Carlos', 'Rodríguez'),
            (3458888012, 'CC', 'EST0073', 'Coloombia', 'Calis', 'Avenwida 789', 300345678679, '2000-03-03', 'Cargglos', 'Rodríggguez')
        ]
        
        for data in test_data:
            cur.execute(
                "INSERT INTO datos (documento, tipo_documento, id, país, ciudad, direccion, telefono, fecha_nacimiento, nombre, apellido) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (documento) DO NOTHING",
                data
            )
        
        # 3. Insert test academic offer
        cur.execute(
            "INSERT INTO oferta (programa, periodo, semestres, titulo, inscripcion, matricula) VALUES ('Ingeniería de Sistemas', 2024, 10, 'Ingeniero de Sistemas', 500000, 5000000) ON CONFLICT DO NOTHING RETURNING id_programa"
        )
        programa_id = cur.fetchone()[0]
        
        # 4. Insert test requirements
        requisitos = ['Diploma de Bachiller', 'Acta de Grado', 'Documento de Identidad']
        for req in requisitos:
            cur.execute(
                "INSERT INTO requisitos (id_programa, nombre_doc) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (programa_id, req)
            )
        
        # 5. Insert test subjects
        asignaturas = [
            ('Programación I', 3, 1, 'PROG101', 'Fundamentos de programación'),
            ('Bases de Datos', 3, 2, 'BD101', 'Introducción a bases de datos'),
            ('Redes', 3, 3, 'RED101', 'Fundamentos de redes'),
            ('Redihs', 3, 3, 'RED101', 'Fundamentos duyye redes')
        ]
        
        for asig in asignaturas:
            cur.execute(
                "INSERT INTO asignaturas (id_programa, nombre, creditos, semestre, nombre_asignatura, descripcion) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING id_asignatura",
                (programa_id, asig[0], asig[1], asig[2], asig[3], asig[4])
            )
            if asig[0] == 'Programación I':  # Guardamos el ID de Programación I para las homologaciones
                id_programacion = cur.fetchone()[0]
        
        # 6. Insert test applications
        test_applications = [
            (1234567890, 2024, programa_id, 'NUEVO', 1, 'Universidad Nacional'),
            (2345678901, 2024, programa_id, 'TRANSFERIDO', 3, 'Universidad de Antioquia'),
            (3456789012, 2024, programa_id, 'NUEVO', 1, 'Universidad del Valle'),
            (3458888012, 2024, programa_id, 'NUEVO', 1, 'Universidad del Valleis')
        ]
        
        for app in test_applications:
            cur.execute(
                "INSERT INTO formulario (documento, periodo, id_programa, tipo_estudiante, semestre, universidad) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING RETURNING id_solicitud",
                app
            )
            solicitud_id = cur.fetchone()[0]
            
            # 7. Insert test documents for each application
            for req in requisitos:
                cur.execute(
                    "INSERT INTO anexos (id_solicitud, nombre_doc, archivo) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                    (solicitud_id, req, b'Test document content')
                )
            
            # 8. Insert test homologations
            cur.execute(
                "INSERT INTO homologar (id_solicitud, estado, id_asignatura, justificacion) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (solicitud_id, 'APROBADO', id_programacion, 'Aprobado por cumplir requisitos')
            )
            
            # 9. Insert test payments
            cur.execute(
                "INSERT INTO pagos (id_solicitud, estado) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (solicitud_id, 'Aprobada')
            )
        
        conn.commit()
        print("Datos de prueba insertados exitosamente!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error al insertar datos de prueba: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    insert_test_data() 