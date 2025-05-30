import streamlit as st
import psycopg2
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
load_dotenv(encoding='utf-8')

st.set_page_config(
    layout="wide"
)

def get_connection():
    return psycopg2.connect(host='dpg-d0kvhcbuibrs739t0bb0-a.oregon-postgres.render.com',
                            database="cdd_db",
                            user="cdd_user",
                            password="gXmnbB3JuFU3IpHYiwiZUdxbwxgHZY26", port='5432',
                            options="-c search_path=uninorte_db")
def login_user(user_id, password):
    conn = get_connection()
    cur = conn.cursor()
    
    # Establecer el esquema correcto
    cur.execute("SET search_path TO uninorte_db")
    
    cur.execute(
        """
        SELECT id, tipo_usuario 
        FROM usuario 
        WHERE id = %s AND contraseña = %s
        """,
        (user_id, password)
    )

    result = cur.fetchone()
    
    # Print debug info after query
    print(f"Database result: {result}")
    
    if result:
        # Create a tuple with stripped values
        session_data = (str(result[0]).strip(), str(result[1]).strip())
        print(f"Processed session data: {session_data}")
    else:
        session_data = None
        print("No session data - login failed")
    
    cur.close()
    conn.close()
    return session_data


def register_user(user_id, email, password, user_type):
    conn = get_connection()
    cur = conn.cursor()
    try:

        cur.execute(
            'INSERT INTO "uninorte_db"."usuario" (id, email, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s)',
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
        # Debug: Show when admin navigation is triggered
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
        # Debug: Show when student navigation is triggered
        pg = st.navigation({
        "Tu cuenta": [st.Page('general/account.py', title = 'Tu cuenta'), st.Page('general/logout.py', title = 'Cerrar sesión'),
                      st.Page('student/sub_main.py', title = 'Inscripciones')]
        }, expanded= False)
else:
    pg = st.navigation([st.Page("general/login.py", title = 'login')])

pg.run()
