import streamlit as st
import psycopg2
import pandas as pd
import datetime


def get_connection():
    return psycopg2.connect(host='dpg-d0kvhcbuibrs739t0bb0-a.oregon-postgres.render.com',
                            database="cdd_db",
                            user="cdd_user",
                            password="gXmnbB3JuFU3IpHYiwiZUdxbwxgHZY26", port='5432')


class Usuario:
    def _init_(self):
        pass

    def crear_solicitud(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SET search_path TO schema_data;")

        # Estilos mejorados con diseño institucional
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            .form-container {
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
                margin: 20px auto;
                max-width: 900px;
                display: flex;
                flex-direction: column;
                align-items: center;
                font-family: 'Roboto', sans-serif;
            }
            .title {
                font-size: 32px;
                color: #E31837;
                font-weight: 700;
                text-align: center;
                margin-bottom: 20px;
                text-transform: uppercase;
            }
            .subtitle {
                font-size: 20px;
                color: #424242;
                text-align: center;
                margin-bottom: 30px;
                font-weight: 400;
            }
            .university-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                margin-bottom: 20px;
            }
            .logo-container {
                display: flex;
                justify-content: flex-end;
            }
            .stButton>button {
                background-color: #E31837;
                color: white;
                border: 2px solid #FFC107;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: 700;
                transition: all 0.3s ease;
                margin: 5px;
            }
            .stButton>button:hover {
                background-color: #FFC107;
                color: #000000;
                border-color: #E31837;
            }
            .success-message {
                color: #2E7D32;
                text-align: center;
                font-weight: 700;
                margin-top: 15px;
            }
            .error-message {
                color: #D32F2F;
                text-align: center;
                font-weight: 700;
                margin-top: 15px;
            }
            .student-type-buttons {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-bottom: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Usar columnas para posicionar el logo en la esquina superior derecha
        col_logo1, col_logo2 = st.columns([4, 1])
        with col_logo1:
            pass  # Espacio vacío a la izquierda
        with col_logo2:
            st.image("Logo_uninorte_colombia.jpg", width=150, caption="")

        st.markdown('<div class="title">Solicitud de Admisión</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Bienvenido a la Universidad del Norte. Completa el formulario para iniciar tu proceso de admisión.</div>', unsafe_allow_html=True)

        st.markdown(
            "Seleccione el tipo de estudiante antes de completar el formulario:")

        # Inicializar estado si no existe
        if "tipo_estudiante" not in st.session_state:
            st.session_state.tipo_estudiante = "Regular"
        if "universidad" not in st.session_state:
            st.session_state.universidad = "Universidad del Norte"

        # Botones para seleccionar tipo de estudiante
        st.markdown('<div class="student-type-buttons">',
                    unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("Regular"):
                st.session_state.tipo_estudiante = "Regular"
                st.session_state.universidad = "Universidad del Norte"
        with col_btn2:
            if st.button("Reingreso"):
                st.session_state.tipo_estudiante = "Reingreso"
                st.session_state.universidad = "Universidad del Norte"
        with col_btn3:
            if st.button("Transferencia Externa"):
                st.session_state.tipo_estudiante = "Transferencia Externa"
                st.session_state.universidad = ""
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("Por favor, complete todos los campos a continuación:")

        with st.form(key="solicitud_form"):
            # Sección 1: Información Personal
            st.markdown(
                '<div class="section-title">Información Personal</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                id_solicitud = st.text_input(
                    "ID de Solicitud", help="Ingrese un ID único para su solicitud")
                documento = st.text_input(
                    "Número de Documento", help="Ingrese su número de documento")
                fecha_nacimiento = st.date_input("Fecha de Nacimiento", min_value=datetime.date(
                    1900, 1, 1), max_value=datetime.date.today())
            with col2:
                correo = st.text_input(
                    "Correo Electrónico", help="Ingrese su correo electrónico institucional o personal")
                telefono = st.text_input(
                    "Número de Teléfono", help="Ingrese un número de contacto (ej. +573001234567)")

            # Sección 2: Información Académica
            st.markdown(
                '<div class="section-title">Información Académica</div>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3:
                periodo = st.text_input(
                    "Periodo Académico", help="Ejemplo: 2025-1")
                id_programa = st.text_input(
                    "ID del Programa", help="Ingrese el ID del programa académico")
                modalidad = st.selectbox("Modalidad de Estudio", [
                                         "Presencial", "Virtual"], help="Seleccione la modalidad de su programa")
            with col4:
                st.markdown(
                    f"**Tipo de Estudiante Seleccionado:** {st.session_state.tipo_estudiante}")
                semestre = st.number_input(
                    "Semestre Actual", min_value=1, max_value=12, step=1, help="Ingrese su semestre actual (1-12)")
                if st.session_state.tipo_estudiante in ["Regular", "Reingreso"]:
                    st.text_input("Universidad", value=st.session_state.universidad, disabled=True,
                                  help="Este campo es automático para estudiantes regulares o de reingreso")
                else:  # Transferencia Externa
                    universidad = st.text_input("Universidad de Origen", value=st.session_state.universidad,
                                                help="Ingrese el nombre de su universidad de origen")
                    st.session_state.universidad = universidad

            # Sección 3: Documentos
            st.markdown(
                '<div class="section-title">Documentos Requeridos</div>', unsafe_allow_html=True)
            uploaded_files = st.file_uploader("Anexar Documentos", accept_multiple_files=True, type=["pdf", "jpg", "png"],
                                              help="Suba los documentos requeridos (certificados, identificación, etc.) en formato PDF, JPG o PNG")
            if uploaded_files:
                st.write("**Documentos Subidos:**")
                for uploaded_file in uploaded_files:
                    st.write(f"- {uploaded_file.name}")

            # Sección 4: Términos y Condiciones
            st.markdown(
                '<div class="section-title">Términos y Condiciones</div>', unsafe_allow_html=True)
            acepta_terminos = st.checkbox("Acepto los términos y condiciones de la Universidad del Norte",
                                          help="Debe aceptar los términos para continuar")

            # Botón de envío
            submit_button = st.form_submit_button("Enviar Solicitud")

            if submit_button:
                # Validaciones
                error_messages = []
                if not (1 <= semestre <= 12):
                    error_messages.append(
                        "El semestre debe estar entre 1 y 12.")
                if not correo or "@" not in correo:
                    error_messages.append(
                        "Por favor, ingrese un correo electrónico válido.")
                if not telefono or not telefono.strip():
                    error_messages.append(
                        "Por favor, ingrese un número de teléfono válido.")
                if not uploaded_files:
                    error_messages.append("Debe subir al menos un documento.")
                if not acepta_terminos:
                    error_messages.append(
                        "Debe aceptar los términos y condiciones.")

                if error_messages:
                    for msg in error_messages:
                        st.markdown(
                            f'<div class="error-message"> {msg}</div>', unsafe_allow_html=True)
                else:
                    solicitud_data = {
                        "id_solicitud": id_solicitud,
                        "documento": documento,
                        "fecha_nacimiento": fecha_nacimiento,
                        "correo": correo,
                        "telefono": telefono,
                        "periodo": periodo,
                        "id_programa": id_programa,
                        "modalidad": modalidad,
                        "tipo_estudiante": st.session_state.tipo_estudiante,
                        "semestre": semestre,
                        "universidad": st.session_state.universidad,
                        "documentos": [file.name for file in uploaded_files] if uploaded_files else []
                    }

                    try:
                        cursor.execute(
                            "INSERT INTO formulario (id_solicitud, documento, fecha_nacimiento, correo, telefono, periodo, id_programa, modalidad, tipo_estudiante, semestre, universidad) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (id_solicitud, documento, fecha_nacimiento, correo, telefono, periodo, id_programa,
                             modalidad, st.session_state.tipo_estudiante, semestre, st.session_state.universidad)
                        )
                        conn.commit()
                        st.markdown(
                            '<div class="success-message">✅ Su solicitud ha sido registrada exitosamente a las 05:18 PM -05 del 24 de mayo de 2025.</div>', unsafe_allow_html=True)
                        st.write("**Detalles de su solicitud:**")
                        st.write(solicitud_data)
                    except Exception as e:
                        conn.rollback()
                        st.markdown(
                            f'<div class="error-message">❌ Error al registrar la solicitud: {str(e)}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        cursor.close()
        conn.close()

        # debe aparecer formulario de incripcion creado por el administrador
    def solicitar_transferencia_externa(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SET search_path TO schema_data;")
        cursor.execute("SELECT * FROM materias_homologables")
        resultados = cursor.fetchall()
        result = {'Nombre': [], 'Descripción': []}
        for fila in resultados:
            result['Nombre'].append(fila[0])
            result['Descripción'].append(fila[1])

        # Estilos mejorados con diseño institucional
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            .form-container {
                background-color: #F5F7FA;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
                margin: 20px auto;
                max-width: 900px;
                display: flex;
                flex-direction: column;
                align-items: center;
                font-family: 'Roboto', sans-serif;
            }
            .title {
                font-size: 32px;
                color: #E31837;
                font-weight: 700;
                text-align: center;
                margin-bottom: 20px;
                text-transform: uppercase;
            }
            .subtitle {
                font-size: 20px;
                color: #424242;
                text-align: center;
                margin-bottom: 30px;
                font-weight: 400;
            }
            .university-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                margin-bottom: 20px;
            }
            .logo-container {
                display: flex;
                justify-content: flex-end;
            }
            .stButton>button {
                background-color: #E31837;
                color: white;
                border: 2px solid #FFC107;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: 700;
                transition: all 0.3s ease;
                margin: 5px;
            }
            .stButton>button:hover {
                background-color: #FFC107;
                color: #000000;
                border-color: #E31837;
            }
            .success-message {
                color: #2E7D32;
                text-align: center;
                font-weight: 700;
                margin-top: 15px;
            }
            .error-message {
                color: #D32F2F;
                text-align: center;
                font-weight: 700;
                margin-top: 15px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Usar columnas para posicionar el logo en la esquina superior derecha
        col_logo1, col_logo2 = st.columns([4, 1])
        with col_logo1:
            pass  # Espacio vacío a la izquierda
        with col_logo2:
            st.image("Logo_uninorte_colombia.jpg", width=150, caption="")

        st.markdown(
            '<div class="title">Solicitud de Transferencia Externa</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Solicite la homologación de materias para su transferencia a la Universidad del Norte.</div>', unsafe_allow_html=True)

        # Mostrar tabla de materias homologables
        st.markdown("**Materias Homologables Disponibles:**")
        df = pd.DataFrame(result)
        st.dataframe(df, use_container_width=True)

        st.markdown("Por favor, complete los campos a continuación:")

        with st.form(key="transferencia_form"):
            seleccion = st.selectbox("Programa Académico", options=list(
                result['Nombre']), help="Seleccione el programa para la homologación")
            justificacion = st.text_area("Justificación de la Homologación",
                                         help="Explique por qué solicita la homologación de materias", height=150)

            # Botón de envío
            submit_button = st.form_submit_button("Enviar Solicitud")

            if submit_button:
                # Validar que la justificación no esté vacía
                if not justificacion.strip():
                    st.markdown(
                        '<div class="error-message">❌ La justificación no puede estar vacía.</div>', unsafe_allow_html=True)
                else:
                    try:
                        # Aquí podrías agregar una inserción en la base de datos si es necesario
                        st.markdown(
                            '<div class="success-message">✅ Su solicitud de transferencia externa ha sido enviada exitosamente a las 05:15 PM -05 del 24 de mayo de 2025.</div>', unsafe_allow_html=True)
                        st.write("**Detalles de su solicitud:**")
                        st.write(f"- **Programa Seleccionado:** {seleccion}")
                        st.write(f"- **Justificación:** {justificacion}")
                    except Exception as e:
                        st.markdown(
                            f'<div class="error-message">❌ Error al enviar la solicitud: {str(e)}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        cursor.close()
        conn.close()

    def pago_fake(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SET search_path TO schema_data;")

        # Estilos para un diseño profesional
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            .payment-container {
                background-color: #F5F7FA;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
                margin: 20px auto;
                max-width: 900px;
                display: flex;
                flex-direction: column;
                align-items: center;
                font-family: 'Roboto', sans-serif;
            }
            .title {
                font-size: 32px;
                color: #E31837;
                font-weight: 700;
                text-align: center;
                margin-bottom: 20px;
                text-transform: uppercase;
            }
            .subtitle {
                font-size: 20px;
                color: #424242;
                text-align: center;
                margin-bottom: 30px;
                font-weight: 400;
            }
            .university-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
                margin-bottom: 20px;
            }
            .logo-container {
                position: absolute;
                top: 20px;
                right: 20px;
                max-width: 150px;
            }
            .stButton>button {
                background-color: #E31837;
                color: white;
                border: 2px solid #FFC107;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: 700;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                background-color: #FFC107;
                color: #000000;
                border-color: #E31837;
            }
            .success-message {
                color: #2E7D32;
                text-align: center;
                font-weight: 700;
                margin-top: 15px;
            }
            .error-message {
                color: #D32F2F;
                text-align: center;
                font-weight: 700;
                margin-top: 15px;
            }
            .payment-summary {
                background-color: #FFFFFF;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
                width: 100%;
                max-width: 600px;
                margin-top: 20px;
            }
            .payment-summary p {
                font-size: 16px;
                margin: 5px 0;
                color: #424242;
            }
            .payment-summary .amount {
                font-size: 24px;
                font-weight: 700;
                color: #E31837;
                margin-top: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

        col_logo1, col_logo2 = st.columns([4, 1])
        with col_logo1:
            pass  # Espacio vacío a la izquierda
        with col_logo2:
            st.image("Logo_uninorte_colombia.jpg", width=150, caption="")

        st.markdown('<div class="title">Simulación de Pago</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="subtitle">Ingrese el ID de su solicitud para simular el pago correspondiente.</div>', unsafe_allow_html=True)

        # Formulario para ingresar el ID de solicitud
        with st.form(key="pago_form"):
            id_solicitud = st.text_input(
                "ID de Solicitud", help="Ingrese el ID de la solicitud para consultar el monto a pagar")
            submit_button = st.form_submit_button("Consultar Pago")

            if submit_button:
                if not id_solicitud:
                    st.markdown(
                        '<div class="error-message"> Por favor, ingrese un ID de solicitud válido.</div>', unsafe_allow_html=True)
                else:
                    try:
                        # Consultar la solicitud en la base de datos
                        cursor.execute(
                            "SELECT tipo_estudiante, periodo FROM formulario WHERE id_solicitud = %s",
                            (id_solicitud,)
                        )
                        result = cursor.fetchone()

                        if not result:
                            st.markdown(
                                '<div class="error-message"> No se encontró una solicitud con el ID proporcionado.</div>', unsafe_allow_html=True)
                        else:
                            tipo_estudiante, periodo = result

                            # Determinar el monto a pagar según tipo_estudiante
                            if tipo_estudiante == "Regular":
                                monto = 50000
                            elif tipo_estudiante == "Reingreso":
                                monto = 40000
                            else:  # Transferencia Externa
                                monto = 70000

                            # Resumen del pago
                            st.markdown(
                                '<div class="payment-summary">', unsafe_allow_html=True)
                            st.markdown(
                                f'<p><strong>ID de Solicitud:</strong> {id_solicitud}</p>', unsafe_allow_html=True)
                            st.markdown(
                                f'<p><strong>Tipo de Estudiante:</strong> {tipo_estudiante}</p>', unsafe_allow_html=True)
                            st.markdown(
                                f'<p><strong>Periodo:</strong> {periodo}</p>', unsafe_allow_html=True)
                            st.markdown(
                                f'<p class="amount">Monto a Pagar: ${monto:,} COP</p>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                            st.markdown(
                                '<div class="success-message">✅ Pago simulado exitosamente a las 05:46 PM -05 del 24 de mayo de 2025.</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.markdown(
                            f'<div class="error-message">❌ Error al consultar la solicitud: {str(e)}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        cursor.close()
        conn.close()

    def retornar_linea_de_tiempo(self):
        # 1 .formulario recibido
        # 2. esperando pago
        # 3. Revision de documentos(detallar por documento cuales han sido aprobados o no)
        # 4. si es de transferencia externa,etc. detallar que materia fueron homologadas
        # 5. Decision de aprobacion al correo
        pass


usuario = Usuario()

page = st.query_params.get("page", "home")
st.write(f"Pagina actual: {page}")

# Estilo general para la página
st.markdown("""
    <style>
    body {
        margin: 0;
        padding: 0;
        width: 100vw;
        background-color: #FFFFFF;
        font-family: 'Roboto', Arial, sans-serif;
    }
    .header {
        background-color: #FFFFFF;
        padding: 20px 20px;
        border-bottom: 4px solid #E31837;
        text-align: center;
        width: 100%;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    .logo {
        max-width: 250px;
        margin-bottom: 10px;
    }
    .title {
        font-size: 42px;
        color: #E31837;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    .subtitle {
        font-size: 22px;
        color: #000000;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 20px;
        padding-top: 80px;
    }
    .welcome-banner {
        background-color: #E31837;
        color: #FFFFFF;
        padding: 20px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        margin-top: 120px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    .decorative-line {
        border: 0;
        height: 2px;
        background: linear-gradient(to right, #FFC107, #E31837, #000000);
        margin: 20px 0;
    }
    .info-section {
        background-color: #F5F5F5;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
        text-align: center;
        color: #000000;
    }
    .benefits-panel {
        background-color: #FFFFFF;
        padding: 20px;
        border: 2px solid #E31837;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
        text-align: center;
        color: #000000;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 20px 0;
        padding-top: 20px;
    }
    .stButton>button, .test-link {
        background-color: #E31837;
        color: #FFFFFF;
        border: 2px solid #FFC107;
        border-radius: 12px;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        display: inline-block;
        text-decoration: none;
        text-align: center;
    }
    .stButton>button:hover, .test-link:hover {
        background-color: #FFC107;
        color: #000000;
        border-color: #E31837;
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .content {
        min-height: 100vh;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .footer {
        background-color: #000000;
        color: #FFFFFF;
        padding: 20px;
        text-align: center;
        width: 100%;
        position: relative;
        bottom: 0;
        font-size: 16px;
        border-top: 4px solid #E31837;
    }
    .footer a {
        color: #FFC107;
        text-decoration: none;
        font-weight: bold;
    }
    .footer a:hover {
        color: #E31837;
    }
    .button-description {
        font-size: 14px;
        color: #000000;
        text-align: center;
        margin-top: 10px;
    }
    @media (max-width: 768px) {
        .title {
            font-size: 32px;
        }
        .subtitle {
            font-size: 18px;
            padding-top: 60px;
        }
        .welcome-banner {
            font-size: 16px;
            margin-top: 100px;
        }
        .button-container {
            flex-direction: column;
            gap: 15px;
            padding-top: 10px;
        }
        .stButton>button, .test-link {
            padding: 12px 30px;
            font-size: 16px;
        }
        .info-section, .benefits-panel {
            padding: 15px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Determinar qué página mostrar según el parámetro
if page == "crear_solicitud":
    usuario.crear_solicitud()
elif page == "transferencia_externa":
    usuario.solicitar_transferencia_externa()
elif page == "pago_fake":
    usuario.pago_fake()
else:
    # Contenido de la página principal
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.image("Logo_uninorte_colombia.jpg",
             width=500, use_container_width=False)
    st.markdown('<div class="title">Sistema de Gestión de Usuarios</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Bienvenidos a la Universidad del Norte - Registra tu solicitud como nuevo usuario</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("¡Hola, futuro estudiante de la Universidad del Norte! Regístrate hoy a las 02:16 PM -05 del 22 de mayo de 2025 y comienza tu camino académico con nosotros. Estamos emocionados de tenerte.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)

    st.markdown("""
        ### Información Importante para Nuevos Usuarios
        - Asegúrate de tener tu documento de identidad y datos académicos listos.
        - Revisa los requisitos en nuestra página oficial antes de registrarte.
        - Contacta a admisiones si necesitas ayuda: admisiones@uninorte.edu.co
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)

    st.markdown("""
        ### Beneficios para Nuevos Estudiantes
        - Acceso a tutorías personalizadas.
        - Descuentos en actividades culturales.
        - Biblioteca digital gratuita.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Botón que abre crear_solicitud en una nueva pestaña
        st.markdown('<a href="http://localhost:8501/?page=crear_solicitud" target="_blank" class="test-link">Quiero crear la solicitud</a>', unsafe_allow_html=True)
    with col2:
        # Botón que abre transferencia_externa en una nueva pestaña
        st.markdown('<a href="http://localhost:8501/?page=transferencia_externa" target="_blank" class="test-link">Quiero solicitar una transferencia externa</a>', unsafe_allow_html=True)
    with col3:
        # Botón que redirige al test de Graddus
        st.markdown(
            '<a href="https://graddus.com/" target="_blank" class="test-link">Descubre tu carrera ideal</a>', unsafe_allow_html=True)
        st.markdown(
            '<div class="button-description">Plataforma con IA para elegir tu carrera en 20 minutos</div>', unsafe_allow_html=True)
    with col4:
        # Botón para la página de pagos
        st.markdown('<a href="http://localhost:8501/?page=pago_fake" target="_blank" class="test-link">Ir a la página de pagos</a>', unsafe_allow_html=True)
        st.markdown(
            '<div class="button-description">Consulta tus pagos, recibos y obligaciones pendientes</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)

    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("""
        Universidad del Norte - Barranquilla, Colombia<br>
        Teléfono: +57 5 3509509 | Correo: admisiones@uninorte.edu.co<br>
        Dirección: Km. 5 Vía Puerto Colombia<br>
        <a href="https://www.uninorte.edu.co" target="_blank">Visita nuestra página oficial</a>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
