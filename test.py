import streamlit as st
import psycopg2
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
load_dotenv()

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

st.title("Proyecto final bases de datos")

if st.session_state.logged_in:

    with st.sidebar:
            if st.button("Cerrar sesión"):
                st.session_state.logged_in = False
                st.session_state.user_id = ''
                st.session_state.user_type = ''
                st.rerun()
            st.markdown("---")
            st.write(f"Bienvenido {st.session_state.user_id}")

            if st.session_state.user_type == 'ADMINISTRADOR':
                st.write('Opciones de administrador')
            else:
                st.write('Consulta de inscripción')


    if st.session_state.user_type == 'ADMINISTRADOR':
        st.write('Panel admin')
    else:
        st.write('Panel estudiante')

else:
    tabs = st.tabs(["Iniciar sesión", "Registrarse"])

    with tabs[0]:
        st.subheader("Iniciar sesión")
        user = st.text_input("ID de usuario", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_password")

        if st.button("Entrar"):
            sesion = login_user(user, password)
            if sesion:
                st.session_state.logged_in = True
                st.session_state.user_id = sesion[0]
                st.session_state.user_type = sesion[1]
                st.rerun()
            else:
                st.error("ID o contraseña incorrectos.")

    with tabs[1]:
        st.subheader("Crear cuenta nueva")
        user_id = st.text_input("ID de usuario", key="reg_user")
        email = st.text_input("Correo electrónico", key="reg_email")
        password = st.text_input("Contraseña", type="password", key="reg_password")

        if st.button("Registrarse"):
            if user_id and email and password:
                register_user(user_id, email, password, 'ESTUDIANTE')
            else:
                st.warning("Por favor, complete todos los campos.")
