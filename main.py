import streamlit as st
import psycopg2
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
load_dotenv(encoding='utf-8')

def get_connection():
    return psycopg2.connect(host = 'localhost', database = os.getenv("DATABASE"), user = os.getenv("USER"), password = os.getenv("PASSWORD"), port = '5432')

def login_user(user_id, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, tipo_usuario FROM usuario WHERE id=%s AND contraseña=%s", (user_id, password))
    sesion = cur.fetchone()
    cur.close()
    conn.close()
    return sesion

def register_user(user_id, email, password, user_type):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuario (id, email, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s)",
            (user_id, email, password, user_type)
        )
        conn.commit()
        st.success("Usuario registrado exitosamente.")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        st.error("Ese ID o correo ya está registrado.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error: {e}")
    finally:
        cur.close()
        conn.close()



if 'logged_in' not in st.session_state:

    st.session_state.logged_in = False
    st.session_state.user_id = ''
    st.session_state.user_type = ''

if st.session_state.logged_in:

    if st.session_state.user_type == 'ADMINISTRADOR':
        pg = st.navigation({
        "Tu cuenta": [st.Page('general/account.py', title = 'Tu cuenta'), 
                      st.Page('general/logout.py', title = 'Cerrar sesión')],
        "Oferta académica": [st.Page('admin/oferta.py', title = 'Configurar oferta académica')],
        "Solicitudes": [st.Page('admin/solicitudes.py', title = 'Consultar solicitudes')],
        "Aprobaciones": [st.Page('admin/documentos.py', title = 'Aprobar documentos'), 
                          st.Page('admin/homologaciones.py', title = 'Aprobar homologaciones'),
                          st.Page('admin/ins_test.py', title = 'Aprobar solicitudes')],
        "Pagos": [st.Page('admin/pagos.py', title = 'Consulta de pagos')]
        }
        , expanded= False)
    

    else:
        pg = st.navigation({
        "Tu cuenta": [st.Page('general/account.py', title = 'Tu cuenta'), st.Page('general/logout.py', title = 'Cerrar sesión'),
                      st.Page('student/sub_main.py', title = 'Inscripciones')]
    }, expanded= False)

            
else:
    pg = st.navigation(['general/login.py'])

pg.run()
