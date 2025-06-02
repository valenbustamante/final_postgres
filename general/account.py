import streamlit as st
from utils import get_connection
from datetime import datetime
st.set_page_config(
    layout="wide"
)
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

st.markdown('<div class="title">Tu Cuenta</div>',
                    unsafe_allow_html=True)

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SET search_path TO uninorte_db;")
user_id = st.session_state.get("user_id", None)
# Consulta parametrizada para evitar SQL injection
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
    (user_id,)
)
fila = cursor.fetchone()

# -------------------------------------------------------
# 6. SI EXISTE, DESPAQUETAMOS; SI NO, TODO VACÍO
# -------------------------------------------------------
if fila:
    # fila = (documento, tipo_documento, telefono, país, ciudad, direccion, fecha_nacimiento, nombre, apellido)
    documento_db, tipo_doc_db, telefono_db, pais_db, ciudad_db, direccion_db, fn_db, nombre_db, apellido_db = fila

    # Convertir fecha a string "YYYY-MM-DD"
    if fn_db:
        try:
            fecha_nacimiento_db = fn_db.strftime("%Y-%m-%d")
        except:
            fecha_nacimiento_db = str(fn_db)
    else:
        fecha_nacimiento_db = ""
else:
    documento_db = ""
    tipo_doc_db = ""
    telefono_db = ""
    pais_db = ""
    ciudad_db = ""
    direccion_db = ""
    fecha_nacimiento_db = ""
    nombre_db = ""
    apellido_db = ""

# -------------------------------------------------------
# 7. DISEÑO DEL FORMULARIO EN 2 COLUMNAS
# -------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    documento = st.text_input("Número de Documento", value=documento_db)
    # Lista de opciones de ejemplo; adáptalas a tus necesidades
    opciones_tipo = ["CC", "CE", "TI", "PA"]
    if tipo_doc_db in opciones_tipo:
        idx = opciones_tipo.index(tipo_doc_db)
    else:
        idx = 0
    tipo_documento = st.selectbox("Tipo de Documento", options=opciones_tipo, index=idx)

    nombre = st.text_input("Nombre", value=nombre_db)
    apellido = st.text_input("Apellido", value=apellido_db)
    # Usamos text_input para la fecha a modo “YYYY-MM-DD”, igual que en tu screenshot
    fecha_nacimiento = st.text_input("Fecha de Nacimiento", value=fecha_nacimiento_db)

with col2:
    telefono = st.text_input("Teléfono", value=str(telefono_db) if telefono_db else "")
    pais = st.text_input("País", value=pais_db)
    ciudad = st.text_input("Ciudad", value=ciudad_db)
    direccion = st.text_input("Dirección", value=direccion_db)

# -------------------------------------------------------
# 8. BOTÓN PARA INSERTAR O ACTUALIZAR
# -------------------------------------------------------
if st.button("Actualizar Datos"):
    # Validación mínima: documento no puede quedar vacío, ni nombre/apellido, etc.
    if not documento.strip():
        st.warning("Debes ingresar un número de documento.")
    elif not nombre.strip() or not apellido.strip():
        st.warning("Nombre y Apellido no pueden estar vacíos.")
    elif not pais.strip() or not ciudad.strip() or not direccion.strip():
        st.warning("País, Ciudad y Dirección son obligatorios.")
    else:
        try:
            # Si 'fila' existía, hacemos UPDATE; si no, INSERT
            if fila:
                cursor.execute(
                    """
                    UPDATE datos
                    SET
                        documento = %s,
                        tipo_documento = %s,
                        telefono = %s,
                        "país" = %s,
                        ciudad = %s,
                        direccion = %s,
                        fecha_nacimiento = %s,
                        nombre = %s,
                        apellido = %s
                    WHERE id = %s
                    """,
                    (
                        int(documento),
                        tipo_documento,
                        int(telefono) if telefono.strip() else None,
                        pais,
                        ciudad,
                        direccion,
                        fecha_nacimiento if fecha_nacimiento.strip() else None,
                        nombre,
                        apellido,
                        user_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO datos (
                        documento,
                        tipo_documento,
                        id,
                        "país",
                        ciudad,
                        direccion,
                        telefono,
                        fecha_nacimiento,
                        nombre,
                        apellido
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        int(documento),
                        tipo_documento,
                        user_id,
                        pais,
                        ciudad,
                        direccion,
                        int(telefono),
                        fecha_nacimiento,
                        nombre,
                        apellido,
                    ),
                )
            conn.commit()
            st.success("¡Datos guardados correctamente!")
        except Exception as e:
            conn.rollback()
            st.error(f"Error al guardar en la base de datos:\n{e}")