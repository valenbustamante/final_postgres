import psycopg2 as p
import os
from dotenv import load_dotenv

load_dotenv()

conn = p.connect(host = 'localhost', database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("PASSWORD"), port = '5432')
cur = conn.cursor()

cur.execute("SET search_path TO uninorte_db;")
cur.execute("""
INSERT INTO usuario (id, email, contraseña, tipo_usuario) VALUES
('admin', 'admin@test.com', 'admin', 'ADMINISTRADOR'),
('valentus', 'valen@test.com', 'test', 'ESTUDIANTE'),
('maria123', 'maria@correo.com', 'clave123', 'ESTUDIANTE'),
('juanc', 'juan@correo.com', 'clave321', 'ESTUDIANTE'),
('linaM', 'lina@correo.com', 'pass456', 'ESTUDIANTE'),
('oscar77', 'oscar@correo.com', 'contraseña', 'ESTUDIANTE'),
('ana_rodriguez', 'ana@correo.com', '123ana', 'ESTUDIANTE'),
('diego_g', 'diego@correo.com', 'clave789', 'ESTUDIANTE'),
('laura_b', 'laura@correo.com', 'laura2025', 'ESTUDIANTE'),
('camilo_93', 'camilo@correo.com', 'camilo', 'ESTUDIANTE');
""")

# Datos personales
cur.execute("""
INSERT INTO datos 
(documento, tipo_documento, id, país, ciudad, direccion, telefono, fecha_nacimiento, nombre, apellido) VALUES
(1001, 'CC', 'valentus', 'Colombia', 'Bogotá', 'Calle 123', 3201234567, '2000-05-20', 'Valentina', 'Suárez'),
(1002, 'TI', 'maria123', 'Colombia', 'Medellín', 'Cra 45 #33', 3014567890, '2001-08-15', 'María', 'López'),
(1003, 'CC', 'juanc', 'Colombia', 'Cali', 'Av 9 #10', 3005678901, '1999-02-12', 'Juan', 'Castaño'),
(1004, 'CC', 'linaM', 'Colombia', 'Barranquilla', 'Calle 98 #54', 3223456789, '2002-11-03', 'Lina', 'Martínez'),
(1005, 'CE', 'oscar77', 'Colombia', 'Cartagena', 'Cra 12 #21', 3112223334, '1998-03-25', 'Oscar', 'Ramos'),
(1006, 'TI', 'ana_rodriguez', 'Colombia', 'Pereira', 'Cl 20 #15', 3123456789, '2003-07-19', 'Ana', 'Rodríguez'),
(1007, 'CC', 'diego_g', 'Colombia', 'Bucaramanga', 'Cl 33 #29', 3139876543, '2001-01-30', 'Diego', 'Gómez'),
(1008, 'CC', 'laura_b', 'Colombia', 'Manizales', 'Av 5 #11', 3154567890, '2000-06-08', 'Laura', 'Bonilla'),
(1009, 'CC', 'camilo_93', 'Colombia', 'Neiva', 'Cl 10 #30', 3109876543, '1997-09-14', 'Camilo', 'Rodríguez');
""")

# Oferta académica
cur.execute("""
INSERT INTO oferta 
(programa, periodo, semestres, titulo, inscripcion, matricula) VALUES
('Ingeniería de Sistemas', 202510, 8, 'Ingeniero de Sistemas', 100000, 3000000),
('Psicología', 202510, 10, 'Psicólogo', 80000, 2800000),
('Administración de Empresas', 202510, 9, 'Administrador', 95000, 2600000),
('Contaduría Pública', 202510, 9, 'Contador Público', 85000, 2400000),
('Ingeniería Civil', 202510, 10, 'Ingeniero Civil', 110000, 3500000),
('Derecho', 202510, 10, 'Abogado', 90000, 2700000);
""")

# Formularios
cur.execute("""
INSERT INTO formulario (documento, periodo, id_programa, tipo_estudiante, semestre, universidad) VALUES
(1001, 202510, 1, 'Nuevo', 1, 'UNIFUTURO'),
(1002, 202510, 2, 'Transferencia externa', 3, 'Universidad X'),
(1003, 202510, 3, 'Nuevo', 1, 'UNIFUTURO'),
(1004, 202510, 4, 'Nuevo', 1, 'UNIFUTURO'),
(1005, 202510, 5, 'Transferencia externa', 5, 'U. Nacional'),
(1006, 202510, 6, 'Nuevo', 1, 'UNIFUTURO'),
(1007, 202510, 1, 'Transferencia externa', 2, 'U. de Caldas'),
(1008, 202510, 3, 'Nuevo', 1, 'UNIFUTURO'),
(1009, 202510, 2, 'Nuevo', 1, 'UNIFUTURO');
""")

# Asignaturas
cur.execute("""
INSERT INTO asignaturas 
(id_programa, nombre, creditos, semestre, nombre_asignatura, descripcion) VALUES
(1, 'Introducción a la Programación', 3, 1, 'Prog 1', 'Conceptos básicos de programación'),
(1, 'Estructuras de Datos', 4, 2, 'Estructuras', 'Listas, pilas, colas, árboles'),
(1, 'Bases de Datos', 4, 3, 'BD', 'Diseño y consulta de bases de datos'),
(1, 'Sistemas Operativos', 4, 4, 'SO', 'Gestión de procesos y memoria'),
(1, 'Redes de Computadores', 3, 5, 'Redes', 'Fundamentos de redes LAN y WAN'),
(2, 'Psicología General', 3, 1, 'Psico 1', 'Introducción a la psicología'),
(2, 'Psicología del Desarrollo', 4, 2, 'Psico 2', 'Desarrollo humano en el ciclo vital'),
(2, 'Neurociencia', 4, 3, 'Neuro', 'Bases biológicas del comportamiento'),
(3, 'Introducción a la Administración', 3, 1, 'Admin 1', 'Principios de gestión'),
(3, 'Contabilidad Básica', 3, 2, 'Contab 1', 'Fundamentos de contabilidad'),
(4, 'Fundamentos de Contaduría', 3, 1, 'Conta Fund', 'Contabilidad y estados financieros'),
(5, 'Estática', 3, 1, 'Estática', 'Equilibrio de cuerpos'),
(6, 'Derecho Romano', 3, 1, 'Romano', 'Raíces del derecho moderno');
""")

# Homologar
cur.execute("""
INSERT INTO homologar (id_solicitud, estado, id_asignatura, justificacion, decision) VALUES
(1, 'Pendiente', 1, 'Solicitud enviada para revisión por parte del comité académico', 'Por definir'),
(2, 'Pendiente', 8, 'Asignatura cursada en Universidad X', 'Por definir'),
(3, 'Rechazada', 5, 'No se adjuntaron suficientes evidencias del contenido', 'Por definir'),
(4, 'Aprobada', 6, 'Materia vista en otra universidad acreditada', 'Homologación aprobada'),
(5, 'Aprobada', 13, 'Materia similar validada por U. Nacional', 'Homologación aprobada'),
(6, 'Pendiente', 10, 'Documentación en proceso de análisis', 'Por definir'),
(7, 'Rechazada', 3, 'No cumple con contenidos mínimos', 'Por definir'),
(8, 'Aprobada', 12, 'Curso aceptado por convenio internacional', 'Homologación aprobada'),
(9, 'Pendiente', 7, 'Se requiere revisión adicional de la malla curricular', 'Por definir');
""")

# Requisitos
cur.execute("""
INSERT INTO requisitos (id_programa, nombre_doc, tipo_req) VALUES
(1, 'Documento identidad', 'Obligatorio'),
(1, 'Certificado de notas', 'Obligatorio'),
(2, 'Certificado EPS', 'Obligatorio'),
(2, 'Historial académico', 'Obligatorio'),
(3, 'Carta motivación', 'Opcional'),
(4, 'Prueba saber 11', 'Obligatorio'),
(5, 'Soporte de homologación', 'Obligatorio'),
(6, 'Carta de recomendación', 'Opcional');
""")

# Pagos
cur.execute("""
INSERT INTO pagos (id_solicitud, estado) VALUES
(1, 'Completado'),
(2, 'Pendiente'),
(3, 'Completado'),
(4, 'Pendiente'),
(5, 'Completado'),
(6, 'Pendiente'),
(7, 'Completado'),
(8, 'Pendiente'),
(9, 'Completado');
""")

# Aprobados
cur.execute("""
INSERT INTO aprobados (id_solicitud, aprobado_por) VALUES
(1, 'admin'),
(3, 'admin'),
(5, 'admin'),
(7, 'admin'),
(9, 'admin');
""")

# Anexos - para insertar archivo PDF con psycopg2.Binary
with open('pdfprueba.pdf', 'rb') as f:
    pdf_bin = f.read()

cur.execute(f"""
INSERT INTO anexos (id_solicitud, nombre_doc, archivo) VALUES
(1, 'documento_identidad.pdf', %s);
""", (p.Binary(pdf_bin),))


conn.commit()

cur.close()
conn.close()