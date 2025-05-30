import streamlit as st
from main import login_user, register_user
import time

with st.container():
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        tabs = st.tabs(["Iniciar sesión", "Registrarse"])

        with tabs[0]:
            st.subheader("Iniciar sesión")
            user = st.text_input("ID de usuario", key="signin_user_input")
            password = st.text_input("Contraseña", type="password", key="signin_password_input")

            if st.button("Entrar", key="signin_button"):                
                session_data = login_user(user, password)

                if session_data:
                    user_id, user_type = session_data                    
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.user_type = user_type
                    
                    st.rerun()
                else:
                    st.error("ID o contraseña incorrectos.")

        with tabs[1]:
            st.subheader("Crear cuenta nueva")
            user_re = st.text_input("ID de usuario", key="signup_user_input")
            email_re = st.text_input("Correo electrónico", key="signup_email_input")
            password_re = st.text_input("Contraseña", type="password", key="signup_password_input")

            if st.button("Registrarse", key="signup_button"):
                if user_re and email_re and password:
                    register_user(user_re, email_re, password_re, 'ESTUDIANTE')
                else:
                    st.warning("Por favor, complete todos los campos.")