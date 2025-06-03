import streamlit as st
from datetime import datetime, timezone
import os

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv(encoding="utf-8")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = ''
    st.session_state.user_type = ''

if st.session_state.logged_in:
    if st.session_state.user_type == 'ADMINISTRADOR':
        pg = st.navigation({
            "Tu cuenta": [st.Page('general/account.py', title='Tu cuenta'), 
                         st.Page('general/logout.py', title='Cerrar sesión')],
            "Oferta académica": [st.Page('admin/oferta.py', title='Configurar oferta académica')],
            "Solicitudes": [st.Page('admin/solicitudes.py', title='Consultar solicitudes')],
            "Aprobaciones": [st.Page('admin/documentos.py', title='Aprobar documentos'), 
                           st.Page('admin/homologaciones.py', title='Aprobar homologaciones'),
                           st.Page('admin/ins_test.py', title='Aprobar solicitudes')],
            "Pagos": [st.Page('admin/pagos.py', title='Consulta de pagos')]
        }, expanded=False)
    else:
        pg = st.navigation({
            "Tu cuenta": [st.Page('general/account.py', title='Tu cuenta'), 
                         st.Page('general/logout.py', title='Cerrar sesión'),
                         st.Page('student/sub_main.py', title='Inscripciones'),
                         st.Page('student/timeline.py', title='Estado de solicitudes')]
        }, expanded=False)
else:
    pg = st.navigation([st.Page("general/login.py", title='Login')], expanded=False)

pg.run()
