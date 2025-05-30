import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
from utils import get_connection
load_dotenv()


st.title('Gestión de homologaciones')

st.markdown("""
<style>
    /* Colores principales */
    :root {
        --primary-color: #FF5A5F;
        --secondary-color: #00A699;
        --warning-color: #FFB400;
        --background-color: #F7F7F7;
        --text-color: #484848;
        --border-color: #EBEBEB;
    }

    /* Estilo general */
    .stApp {
        background-color: var(--background-color);
    }

    /* Títulos y texto */
    h1, h2, h3, h4 {
        color: var(--text-color);
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, Helvetica Neue, sans-serif;
    }

    h4 {
        font-size: 0.9rem;
        margin: 0 0 8px 0;
        font-weight: 600;
    }

    /* Barra de búsqueda personalizada */
    .stTextInput input {
        border-radius: 24px !important;
        border: 2px solid var(--border-color) !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
    }

    .stTextInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(255,90,95,0.2) !important;
    }

    /* Selectbox personalizado */
    .stSelectbox select {
        border-radius: 8px !important;
        border: 2px solid var(--border-color) !important;
        padding: 8px 16px !important;
    }

    .stSelectbox select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(255,90,95,0.2) !important;
    }

    /* Dashboard cards */
    .dashboard-card {
        padding: 20px;
        border-radius: 16px;
        margin: 10px 0;
        transition: all 0.3s ease;
        color: white;
    }

    .dashboard-card h3 {
        color: white !important;
        margin: 0 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    .dashboard-card p {
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin: 10px 0 0 0 !important;
    }

    .card-pendientes {
        background: linear-gradient(135deg, var(--warning-color) 0%, #FF9800 100%);
        box-shadow: 0 4px 20px rgba(255, 180, 0, 0.2);
    }

    .card-aprobadas {
        background: linear-gradient(135deg, var(--secondary-color) 0%, #008B80 100%);
        box-shadow: 0 4px 20px rgba(0, 166, 153, 0.2);
    }

    .card-rechazadas {
        background: linear-gradient(135deg, var(--primary-color) 0%, #E31C3D 100%);
        box-shadow: 0 4px 20px rgba(255, 90, 95, 0.2);
    }

    .dashboard-card:hover {
        transform: translateY(-5px);
    }

    /* Expander personalizado */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 12px;
        padding: 15px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }

    /* Estados */
    .estado-pendiente {
        color: var(--warning-color);
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(255,180,0,0.1);
    }

    .estado-aprobada {
        color: var(--secondary-color);
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(0,166,153,0.1);
    }

    .estado-rechazada {
        color: var(--primary-color);
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(255,90,95,0.1);
    }

    /* Formulario */
    .stForm {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 20px;
    }

    /* Botón de submit */
    .stButton button {
        background-color: var(--secondary-color) !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }

    /* Info cards */
    .info-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid var(--secondary-color);
        width: 100%;
        display: block;
        float: none;
        clear: both;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    .info-card h4 {
        color: var(--text-color);
        font-size: 0.9rem;
        margin: 0 0 5px 0;
        font-weight: 600;
    }

    .info-card p {
        color: var(--text-color);
        font-size: 1rem;
        margin: 0 0 15px 0;
        line-height: 1.5;
    }

    .info-card p:last-child {
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns([2,1,1,1])

id_solicitud_param = st.query_params.get("id", [None])[0]

with col1:
    st.markdown("<h4>Buscar por ID de solicitud</h4>", unsafe_allow_html=True)
    id_filtro = st.text_input("", value=id_solicitud_param if id_solicitud_param else "", placeholder="Ingrese el número de solicitud...")

with col2:
    st.markdown("<h4>Estado</h4>", unsafe_allow_html=True)
    estado_filtro = st.selectbox(
        "",
        ["Todos", "Pendiente", "Aprobada", "Rechazada"]
    )

with col3:
    st.markdown("<h4>Programa</h4>", unsafe_allow_html=True)
    programa_filtro = st.selectbox(
        "",
        ["Todos", "Ingeniería", "Administración", "Medicina"]  # Ajustar según los programas reales
    )

with col4:
    st.markdown("<h4>Ordenar por</h4>", unsafe_allow_html=True)
    orden = st.selectbox(
        "",
        ["Más recientes", "Más antiguos"]
    )
    
if id_solicitud_param:
    st.markdown("""
    <a href="/admin/solicitudes" style="
        display: inline-block;
        padding: 5px 15px;
        background-color: #484848;
        color: white;
        text-decoration: none;
        border-radius: 15px;
        font-size: 0.8em;
        margin-bottom: 20px;
    ">← Volver a solicitudes</a>
    """, unsafe_allow_html=True)

try:
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT h.id_solicitud, h.id_asignatura, h.estado, h.justificacion, h.decision,
           a.nombre_asignatura, a.descripcion, o.programa,
           d.nombre, u.email
    FROM homologar h
    JOIN asignaturas a ON h.id_asignatura = a.id_asignatura
    JOIN formulario f ON h.id_solicitud = f.id_solicitud
    JOIN oferta o ON f.id_programa = o.id_programa
    JOIN datos d ON f.documento = d.documento
    JOIN usuario u ON d.id = u.id
    WHERE 1=1
    """ + (" AND CAST(h.id_solicitud AS TEXT) LIKE %s" if id_filtro else "") + \
    (" AND h.estado = %s" if estado_filtro != "Todos" else "") + \
    (" AND o.programa = %s" if programa_filtro != "Todos" else "") + \
    " ORDER BY h.id_solicitud " + ("DESC" if orden == "Más recientes" else "ASC")

    params = []
    if id_filtro:
        params.append(f"%{id_filtro}%")
    if estado_filtro != "Todos":
        params.append(estado_filtro)
    if programa_filtro != "Todos":
        params.append(programa_filtro)

    cur.execute(query, params)
    homologaciones = cur.fetchall()

    if homologaciones:
        pendientes = sum(1 for h in homologaciones if h[2] == 'Pendiente')
        aprobadas = sum(1 for h in homologaciones if h[2] == 'Aprobada')
        rechazadas = sum(1 for h in homologaciones if h[2] == 'Rechazada')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='dashboard-card card-pendientes'>
                <h3>Pendientes</h3>
                <p>{pendientes}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='dashboard-card card-aprobadas'>
                <h3>Aprobadas</h3>
                <p>{aprobadas}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='dashboard-card card-rechazadas'>
                <h3>Rechazadas</h3>
                <p>{rechazadas}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for solicitud in homologaciones:
            id_solicitud, id_asignatura, estado, justificacion, decision, nombre_asignatura, descripcion, programa, nombre_usuario, email_usuario = solicitud
            
            estado_clase = {
                'Pendiente': 'estado-pendiente',
                'Aprobada': 'estado-aprobada',
                'Rechazada': 'estado-rechazada'
            }.get(estado, 'estado-pendiente')

            with st.expander(f"Solicitud #{id_solicitud} - {nombre_asignatura}"):
                st.markdown(f"<p class='{estado_clase}'>Estado: {estado}</p>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""<div class='info-card'>
                    <h4>Estudiante</h4>
                    <p>{nombre_usuario}</p>
                    <h4>Email</h4>
                    <p>{email_usuario}</p>
                    <h4>Programa</h4>
                    <p>{programa}</p>
                    </div>""", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""<div class='info-card'>
                    <h4>Asignatura</h4>
                    <p>{nombre_asignatura}</p>
                    <h4>Descripción</h4>
                    <p>{descripcion}</p>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""<div class='info-card'>
                <h4>Justificación del estudiante</h4>
                <p>{justificacion}</p>
                </div>""", unsafe_allow_html=True)

                if decision:
                    st.markdown(f"""<div class='info-card'>
                    <h4>Decisión administrativa</h4>
                    <p>{decision}</p>
                    </div>""", unsafe_allow_html=True)

                with st.form(key=f"form_{id_solicitud}_{id_asignatura}"):
                    nuevo_estado = st.selectbox(
                        "Estado",
                        ["Pendiente", "Aprobada", "Rechazada"],
                        index=["Pendiente", "Aprobada", "Rechazada"].index(estado) if estado in ["Pendiente", "Aprobada", "Rechazada"] else 0,
                        key=f"estado_{id_solicitud}_{id_asignatura}"
                    )
                    nueva_decision = st.text_area("Decisión administrativa", value=decision or "", key=f"decision_{id_solicitud}_{id_asignatura}")
                    submit_button = st.form_submit_button("Guardar cambios")

                    if submit_button:
                        try:
                            cur.execute("""
                                UPDATE homologar 
                                SET estado = %s, decision = %s
                                WHERE id_solicitud = %s AND id_asignatura = %s
                            """, (nuevo_estado, nueva_decision, id_solicitud, id_asignatura))
                            conn.commit()
                            st.success("Homologación actualizada exitosamente")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error al actualizar: {e}")

    else:
        st.info("No se encontraron solicitudes de homologación")

except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
