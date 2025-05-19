import streamlit as st
from main import login_user, register_user

with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
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