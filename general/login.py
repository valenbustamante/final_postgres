import streamlit as st
from utils import login_user, register_user

if 'login_form_key' not in st.session_state:
    st.session_state.login_form_key = 0

with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        tabs = st.tabs(["Iniciar sesión", "Registrarse"])

        with tabs[0]:
            st.subheader("Iniciar sesión")
            form_key = f"login_form_{st.session_state.login_form_key}"
            with st.form(key=form_key):
                user = st.text_input("ID de usuario", key=f"signin_user_input_{st.session_state.login_form_key}")
                password = st.text_input("Contraseña", type="password", key=f"signin_password_input_{st.session_state.login_form_key}")
                submit = st.form_submit_button("Entrar")

                if submit:
                    session_data = login_user(user, password)
                    if session_data:
                        user_id, user_type = session_data
                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.user_type = user_type
                        st.session_state.login_form_key += 1
                        st.rerun()
                    else:
                        st.error("ID o contraseña incorrectos.")

        with tabs[1]:
            st.subheader("Crear cuenta nueva")
            register_form_key = f"register_form_{st.session_state.login_form_key}"
            with st.form(key=register_form_key):
                user_re = st.text_input("ID de usuario", key=f"signup_user_input_{st.session_state.login_form_key}")
                email_re = st.text_input("Correo electrónico", key=f"signup_email_input_{st.session_state.login_form_key}")
                password_re = st.text_input("Contraseña", type="password", key=f"signup_password_input_{st.session_state.login_form_key}")
                register = st.form_submit_button("Registrarse")

                if register:
                    if user_re and email_re and password_re:
                        register_user(user_re, email_re, password_re, 'ESTUDIANTE')
                        st.session_state.login_form_key += 1
                    else:
                        st.warning("Por favor, complete todos los campos.")