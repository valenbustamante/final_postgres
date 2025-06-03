import streamlit as st
import psycopg2
import pandas as pd
import datetime
from utils import get_connection
from unidecode import unidecode
import re
fecha_actual = datetime.datetime.now().strftime("%I:%M %p -05 del %d de %B de %Y")
class Usuario:
    def _init_(self):
        pass

    def crear_solicitud(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SET search_path TO uninorte_db;")

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


        st.markdown('<div class="title">Solicitud de Admisión</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Bienvenido a la La Universidad para el Futuro . Completa el formulario para iniciar tu proceso de admisión.</div>', unsafe_allow_html=True)

        st.markdown(
            "Seleccione el tipo de estudiante antes de completar el formulario:")

        # Inicializar estado si no existe
        if "tipo_estudiante" not in st.session_state:
            st.session_state.tipo_estudiante = "Regular"
        if "universidad" not in st.session_state:
            st.session_state.universidad = "Universidad para el Futuro "

        # Botones para seleccionar tipo de estudiante
        st.markdown('<div class="student-type-buttons">', unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("Regular"):
                st.session_state.tipo_estudiante = "Regular"
                st.session_state.universidad = "Universidad para el Futuro "
        with col_btn2:
            if st.button("Reingreso"):
                st.session_state.tipo_estudiante = "Reingreso"
                st.session_state.universidad = "Universidad para el Futuro "
        with col_btn3:
            if st.button("Transferencia Externa"):
                st.session_state.tipo_estudiante = "Transferencia Externa"
                st.session_state.universidad = ""
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("Por favor, complete los campos a necesarios:")

        opciones_programas = {
                    "Ingeniería de Sistemas": 1,
                    "Psicología": 2,
                    "Administración de Empresas": 3,
                    "Contaduría Pública": 4,
                    "Ingeniería Civil": 5,
                    "Derecho": 6
                }
        max_semestres = {
                    1: 8,   # Ingeniería de Sistemas
                    2: 10,  # Psicología
                    3: 9,   # Administración de Empresas
                    4: 9,   # Contaduría Pública
                    5: 10,  # Ingeniería Civil
                    6: 10   # Derecho
                }
        programa_nombre = st.selectbox(
                    "Programa académico",
                    list(opciones_programas.keys()),
                    help="Seleccione el programa académico al que desea aplicar. El valor seleccionado se asignará automáticamente."
                )
        id_programa = opciones_programas[programa_nombre]
        max_sem = max_semestres.get(id_programa, 12)  # Valor por defecto: 12

        cursor.execute("""
            SELECT DISTINCT periodo
            FROM uninorte_db.oferta
            WHERE id_programa = %s
            ORDER BY periodo DESC
        """, (id_programa,))
        periodos_disponibles = [row[0] for row in cursor.fetchall()]
        user_id = st.session_state.get("user_id", None)
        cursor.execute(
            """
            SELECT 
                documento,
                tipo_documento,
                telefono,
                "país",
                ciudad,
                direccion,
                fecha_nacimiento,
                nombre,
                apellido
            FROM datos
            WHERE id = %s
            """,
            (user_id,),
        )
        fila = cursor.fetchone()

        # 2. Si fila no es None, desempacamos; si es None, dejamos valores vacíos / por defecto
        if fila is not None:
            documento_default       = fila[0] or ""
            tipo_documento_default  = fila[1] or ""
            telefono_default        = fila[2] or ""
            pais_default            = fila[3] or ""
            ciudad_default          = fila[4] or ""
            direccion_default       = fila[5] or ""
            # Para la fecha, verificamos que no sea mayor a hoy
            hoy = datetime.date.today()
            if fila[6] is not None and fila[6] <= hoy:
                fecha_nacimiento_default = fila[6]
            else:
                fecha_nacimiento_default = hoy
            nombre_default          = fila[7] or ""
            apellido_default        = fila[8] or ""
        else:
            documento_default       = ""
            tipo_documento_default  = ""
            telefono_default        = ""
            pais_default            = ""
            ciudad_default          = ""
            direccion_default       = ""
            fecha_nacimiento_default = datetime.date.today()
            nombre_default          = ""
            apellido_default        = ""

        with st.form(key="solicitud_form"):
        # Sección 1: Información Personal
            st.markdown('<div class="section-title">Información Personal</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)

            with col1:
                # Generar id_solicitud
                cursor.execute("SELECT MAX(CAST(id_solicitud AS INTEGER)) FROM formulario")
                ultimo_id = cursor.fetchone()[0]
                if ultimo_id is None:
                    nuevo_id = 1
                else:
                    nuevo_id = int(ultimo_id) + 1
                id_solicitud = str(nuevo_id)
                st.session_state.id_solicitud = id_solicitud

                st.text_input(
                    "ID de Solicitud (generado automáticamente)",
                    value=id_solicitud,
                    disabled=True
                )

                # Campo “Número de Documento” con valor por defecto
                documento = st.text_input(
                    "Número de Documento",
                    value=documento_default,
                    help="Ingrese su número de documento"
                )

                # Selectbox de Tipo de Documento, ubicando el índice según el default
                opciones_tipo = ["CC", "TI", "CE", "Pasaporte"]
                if tipo_documento_default in opciones_tipo:
                    idx_tipo = opciones_tipo.index(tipo_documento_default)
                else:
                    idx_tipo = 0
                tipo_documento = st.selectbox(
                    "Tipo de Documento",
                    opciones_tipo,
                    index=idx_tipo
                )

                # Date input para Fecha de Nacimiento, obligatoriamente dentro del rango
                fecha_nacimiento = st.date_input(
                    "Fecha de Nacimiento",
                    value=fecha_nacimiento_default,
                    min_value=datetime.date(1900, 1, 1),
                    max_value=datetime.date.today()
                )

                nombre = st.text_input("Nombre", value=nombre_default)
                apellido = st.text_input("Apellido", value=apellido_default)

            with col2:
                telefono = st.text_input("Teléfono de Contacto", value=telefono_default)
                correo = st.text_input("Correo Electrónico")  # Este no venía de 'datos'
                pais = st.text_input("País", value=pais_default)
                ciudad = st.text_input("Ciudad", value=ciudad_default)
                direccion = st.text_input("Dirección Residencial", value=direccion_default)

            # Sección 2: Información Académica
            st.markdown('<div class="section-title">Información Académica</div>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3:
                if periodos_disponibles:
                    periodo = st.selectbox(
                        "Periodo Académico",
                        periodos_disponibles,
                        help="Seleccione el periodo académico disponible para este programa"
                    )
                else:
                    st.warning("⚠️ No hay periodos disponibles para el programa seleccionado.")
                    periodo = None

                st.text_input(
                    "Nombre del programa escogido por usted",
                    value=programa_nombre,
                    disabled=True
                )

            with col4:
                st.text_input(
                    "Tipo de estudiante",
                    value=st.session_state.tipo_estudiante,
                    disabled=True
                )

                # Semestre según tipo de estudiante
                if st.session_state.tipo_estudiante == "Regular":
                    semestre = 1
                    st.number_input(
                        "Semestre",
                        value=1,
                        disabled=True,
                        help="Los estudiantes regulares comienzan en 1"
                    )
                else:
                    semestre = st.number_input(
                        "Semestre",
                        min_value=1,
                        max_value=max_sem,
                        step=1,
                        help=f"Este programa tiene un máximo de {max_sem} semestres."
                    )

                # Universidad según tipo de estudiante
                if st.session_state.tipo_estudiante in ["Regular", "Reingreso"]:
                    st.text_input(
                        "Universidad",
                        value=st.session_state.universidad,
                        disabled=True
                    )
                else:
                    universidad = st.text_input(
                        "Universidad de Origen",
                        value=st.session_state.universidad
                    )
                    st.session_state.universidad = universidad           


            # Sección 3: Documentos
            st.markdown('<div class="section-title">Documentos Requeridos</div>', unsafe_allow_html=True)

            try:
                # Consulta correcta según tu base de datos y esquema
                cursor.execute(
                    "SELECT nombre_doc, tipo_req FROM uninorte_db.requisitos WHERE id_programa = %s",
                    (id_programa,)
                )
                filas_req = cursor.fetchall()  # lista de tuplas: [(nombre_doc1, True), (nombre_doc2, False), ...]

                # Construimos un diccionario { 'campo': True/False, ... }
                tipo_req_dict = {}
                for nombre_doc, tipo_req_db in filas_req:
                    # si tu tabla almacena 1/0 o 'S'/'N', tendrías que convertirlo aquí. 
                    # Asumimos que tipo_req_db ya viene como BOOLEAN (True/False).
                    tipo_req_dict[nombre_doc] = tipo_req_db
                documentos_requeridos = tipo_req_dict
                if documentos_requeridos:

                        st.session_state["archivos_subidos"] = {}

                        for nombre_doc, es_obligatorio in documentos_requeridos.items():
                            # Creamos una llave “segura” para cada file_uploader
                            safe_key = "doc_" + re.sub(r"\W+", "_", unidecode(nombre_doc.lower().strip()))

                            # Ajustamos el label según obligatorio/opcional
                            label = f"Subir archivo para: {nombre_doc}"
                            if es_obligatorio == "Obligatorio":
                                label += "  *(Obligatorio)*"
                            else:
                                label += "  *(Opcional)*"

                            archivo = st.file_uploader(label=label, type=["pdf"], key=safe_key)

                            # Si se acaba de subir, lo guardamos en session_state
                            if archivo is not None:
                                st.session_state["archivos_subidos"][nombre_doc] = archivo
                                st.success(f"✅ Archivo cargado para «{nombre_doc}»")
                                st.write(f"• Nombre: `{archivo.name}` ({archivo.size/1024:.1f} KB)")

                            # Separador visual
                            st.markdown("---")
                    # Línea divisoria entre documentos

                else:
                    st.markdown(
                        '<div class="info-message">⚠️ Este programa no tiene documentos requeridos definidos.</div>',
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.markdown(
                    f'<div class="error-message">❌ Error al consultar los requisitos: {str(e)}</div>',
                    unsafe_allow_html=True
                )

            # Sección 4: Términos y Condiciones
            st.markdown(
                '<div class="section-title">Términos y Condiciones</div>', unsafe_allow_html=True)
            acepta_terminos = st.checkbox("Acepto los términos y condiciones de La Universidad para el Futuro ",
                                          help="Debe aceptar los términos para continuar")

            
            submit_button = st.form_submit_button("Enviar Solicitud")

            if submit_button:
                # Validaciones
                error_messages = []
                if not (1 <= semestre <= 12):
                    error_messages.append("El semestre debe estar entre 1 y 12.")
                if not correo or "@" not in correo:
                    error_messages.append("Por favor, ingrese un correo electrónico válido.")
                if not telefono or not telefono.strip():
                    error_messages.append("Por favor, ingrese un número de teléfono válido.")
                                                    # Validar si TODOS los documentos requeridos fueron subid
                if st.session_state["archivos_subidos"]:
                    for ndoc, uploaded_file in st.session_state["archivos_subidos"].items():

                        st.write(f"- **{ndoc}** → `{uploaded_file.name}` ({uploaded_file.size/1024:.1f} KB)")
                else:
                                st.info("Aún no se ha subido ningún archivo.")           
                if not acepta_terminos:
                    error_messages.append("Debe aceptar los términos y condiciones.")
                if "id_solicitud" not in st.session_state:
                    st.session_state.id_solicitud = None

                if error_messages:
                    for msg in error_messages:
                        st.markdown(
                            f'<div class="error-message"> {msg}</div>', unsafe_allow_html=True)
                else:
                    solicitud_data = {
                        "id_solicitud": st.session_state.get("id_solicitud"),
                        "documento": documento,
                        "fecha_nacimiento": fecha_nacimiento,
                        "correo": correo,
                        "telefono": telefono,
                        "periodo": periodo,
                        "id_programa": id_programa,
                        "tipo_estudiante": st.session_state.tipo_estudiante,
                        "semestre": semestre,
                        "universidad": st.session_state.universidad,
                        "documentos": [file.name for file in st.session_state["archivos_subidos"].values() if file]
                    }

                    try:


                        cursor.execute("""
                            INSERT INTO datos (documento, tipo_documento, id, país, ciudad, direccion, telefono, fecha_nacimiento, nombre, apellido)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (documento) DO NOTHING
                        """, (documento, tipo_documento, st.session_state.user_id, pais, ciudad, direccion, telefono, fecha_nacimiento, nombre, apellido  
                        ))
                        cursor.execute("""
                            INSERT INTO formulario (id_solicitud, documento, periodo, id_programa, tipo_estudiante, semestre, universidad)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (st.session_state.get("id_solicitud"), documento, periodo, id_programa, st.session_state.tipo_estudiante, semestre, st.session_state.universidad
                        ))

                        conn.commit()
                        for ndoc, uploaded_file in st.session_state["archivos_subidos"].items():
                            if tipo_req_dict[ndoc] == 'Opcional' and uploaded_file is not None:
                            # Leer el contenido binario del PDF
                                contenido_binario = uploaded_file.read()  # esto equivale a leer el archivo en 'rb'
                                # Construir la sentencia INSERT

                                cursor.execute(
                                    """
                                    INSERT INTO anexos (id_solicitud, nombre_doc, archivo)
                                    VALUES (%s, %s, %s);
                                    """,
                                    (
                                        int(st.session_state.get("id_solicitud")),                          #
                                        f"{ndoc}",   # 
                                        psycopg2.Binary(contenido_binario)
                                    )
                                )
                            else:
                                contenido_binario = uploaded_file.read()  # esto equivale a leer el archivo en 'rb'
                                # Construir la sentencia INSERT

                                cursor.execute(
                                    """
                                    INSERT INTO anexos (id_solicitud, nombre_doc, archivo)
                                    VALUES (%s, %s, %s);
                                    """,
                                    (
                                        int(st.session_state.get("id_solicitud")),                          #
                                        f"{ndoc}",   # 
                                        psycopg2.Binary(contenido_binario)
                                    )
                                )

                        conn.commit()
                        st.markdown(
                            f'<div class="success-message">✅ Su solicitud ha sido registrada exitosamente a las a las {fecha_actual}.</div>', unsafe_allow_html=True)
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
        cursor.execute("SET search_path TO uninorte_db;")
        cursor.execute("SELECT nombre, descripcion FROM asignaturas")
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

        st.markdown(
            '<div class="title">Solicitud de Transferencia Externa</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Solicite la homologación de materias para su transferencia a La Universidad para el Futuro.</div>', unsafe_allow_html=True)

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
                            '<div class="success-message">✅ Su solicitud de transferencia externa ha sido enviada exitosamente a las a las {fecha_actual}.</div>', unsafe_allow_html=True)
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
        cursor.execute("SET search_path TO uninorte_db;")

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
                        # Buscar datos de la solicitud
                        cursor.execute(
                            "SELECT tipo_estudiante, periodo, id_programa FROM formulario WHERE id_solicitud = %s",
                            (id_solicitud,)
                        )
                        result = cursor.fetchone()

                        if not result:
                            st.markdown(
                                '<div class="error-message"> No se encontró una solicitud con el ID proporcionado.</div>', unsafe_allow_html=True)
                        else:
                            tipo_estudiante, periodo, id_programa = result

                            # Buscar el nombre del programa y costo de inscripción
                            cursor.execute(
                                "SELECT programa, inscripcion FROM oferta WHERE id_programa = %s",
                                (id_programa,)
                            )
                            programa_result = cursor.fetchone()

                            if not programa_result:
                                st.markdown(
                                    '<div class="error-message"> No se encontró información del programa académico asociado.</div>', unsafe_allow_html=True)
                            else:
                                programa_nombre, inscripcion = programa_result

                                # Mostrar resumen de pago
                                st.markdown('<div class="payment-summary">', unsafe_allow_html=True)
                                st.markdown(f'<p><strong>ID de Solicitud:</strong> {id_solicitud}</p>', unsafe_allow_html=True)
                                st.markdown(f'<p><strong>Tipo de Estudiante:</strong> {tipo_estudiante}</p>', unsafe_allow_html=True)
                                st.markdown(f'<p><strong>Periodo:</strong> {periodo}</p>', unsafe_allow_html=True)
                                st.markdown(f'<p><strong>Programa:</strong> {programa_nombre}</p>', unsafe_allow_html=True)
                                st.markdown(f'<p class="amount">Monto a Pagar: ${inscripcion:,.2f} COP</p>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)

                                st.markdown(
                                    f'<div class="success-message">✅ Pago simulado exitosamente a las {fecha_actual}.</div>', unsafe_allow_html=True )
                    except Exception as e:
                        st.markdown(
                            f'<div class="error-message">❌ Error al consultar la solicitud: {str(e)}</div>', unsafe_allow_html=True)

        # Al final del archivo
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

# Inicialización del page actual
if 'page' not in st.session_state:
    st.session_state.page = st.query_params.get("page", "main")

# Lógica central de navegación
if st.session_state.page == "crear_solicitud":
    usuario.crear_solicitud()
    if st.button("Volver al inicio"):
        st.session_state.page = "main"
        st.rerun()
elif st.session_state.page == "transferencia_externa":
    usuario.solicitar_transferencia_externa()
    if st.button("Volver al inicio"):
        st.session_state.page = "main"
        st.rerun()
elif st.session_state.page == "pago_fake":
    usuario.pago_fake()
    if st.button("Volver al inicio"):
        st.session_state.page = "main"
        st.rerun()
else:
    # Página principal / menú
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown('<div class="title">Sistema de Gestión de Usuarios</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Bienvenidos a La Universidad para el Futuro  - Registra tu solicitud como nuevo usuario</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("¡Hola, futuro estudiante de La Universidad para el Futuro ! Regístrate hoy y comienza tu camino académico con nosotros. Estamos emocionados de tenerte.")
    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)

    st.markdown("""
        ### Información Importante para Nuevos Usuarios
        - Asegúrate de tener tu documento de identidad y datos académicos listos.
        - Revisa los requisitos en nuestra página oficial antes de registrarte.
        - Contacta a admisiones si necesitas ayuda: admisiones@UNIFUTURO.edu.co
    """)

    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)

    st.markdown("""
        ### Beneficios para Nuevos Estudiantes
        - Acceso a tutorías personalizadas.
        - Descuentos en actividades culturales.
    """)

    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)

    # Botones usando session_state para navegación interna
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button('Quiero crear la solicitud'):
            st.session_state.page = 'crear_solicitud'
            st.rerun()
    with col2:
        if st.button('Quiero solicitar una transferencia externa'):
            st.session_state.page = 'transferencia_externa'
            st.rerun()
    with col3:
        st.markdown(
            '<a href="https://graddus.com/" target="_blank" class="test-link">Descubre tu carrera ideal</a>', 
            unsafe_allow_html=True)
        st.markdown(
            '<div class="button-description">Plataforma con IA para elegir tu carrera en 20 minutos</div>', 
            unsafe_allow_html=True)
    with col4:
        if st.button('Ir a la página de pagos'):
            st.session_state.page = 'pago_fake'
            st.rerun()
        st.markdown(
            '<div class="button-description">Consulta tus pagos, recibos y obligaciones pendientes</div>', 
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="decorative-line">', unsafe_allow_html=True)
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("""
        La Universidad para el Futuro  - Barranquilla, Colombia<br>
        Teléfono: +57 5 3509509 | Correo: admisiones@UNIFUTURO.edu.co<br>
        Dirección: Km. 5 Vía Puerto Colombia<br>
        <a href="https://www.UNIFUTURO.edu.co" target="_blank">Visita nuestra página oficial</a>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)