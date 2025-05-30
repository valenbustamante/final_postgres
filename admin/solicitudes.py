import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
from utils import get_connection

load_dotenv()

st.title('Gestión de solicitudes')

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

    .card-prospectos {
        background: linear-gradient(135deg, var(--secondary-color) 0%, #008B80 100%);
        box-shadow: 0 4px 20px rgba(0, 166, 153, 0.2);
    }

    .card-transferencia {
        background: linear-gradient(135deg, var(--warning-color) 0%, #FF9800 100%);
        box-shadow: 0 4px 20px rgba(255, 180, 0, 0.2);
    }

    .card-total {
        background: linear-gradient(135deg, var(--primary-color) 0%, #E31C3D 100%);
        box-shadow: 0 4px 20px rgba(255, 90, 95, 0.2);
    }

    .dashboard-card:hover {
        transform: translateY(-5px);
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

    /* Estados */
    .estado-pendiente {
        color: var(--warning-color);
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(255,180,0,0.1);
    }

    .estado-aprobado {
        color: var(--secondary-color);
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(0,166,153,0.1);
    }

    .estado-rechazado {
        color: var(--primary-color);
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(255,90,95,0.1);
    }

    /* Botones de navegación */
    .nav-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 10px 10px 10px 0;
        border-radius: 8px;
        font-weight: 500;
        text-decoration: none;
        transition: all 0.2s;
        cursor: pointer;
    }

    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .nav-button.documentos {
        background-color: var(--secondary-color);
        color: white !important;
    }

    .nav-button.homologaciones {
        background-color: var(--warning-color);
        color: white !important;
    }

    .nav-section {
        margin-top: 20px;
        padding: 15px;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .nav-section h4 {
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# Filtros
col1, col2, col3, col4 = st.columns([2,1,1,1])

with col1:
    st.markdown("<h4>Buscar por ID de solicitud</h4>", unsafe_allow_html=True)
    id_filtro = st.text_input("", placeholder="Ingrese el número de solicitud...")

with col2:
    st.markdown("<h4>Tipo de inscripción</h4>", unsafe_allow_html=True)
    tipo_filtro = st.selectbox(
        "",
        ["Todos", "Prospecto", "Transferencia Externa"]
    )

with col3:
    st.markdown("<h4>Estado de documentos</h4>", unsafe_allow_html=True)
    estado_docs_filtro = st.selectbox(
        "",
        ["Todos", "Pendientes", "Aprobados", "Sin documentos"]
    )

with col4:
    st.markdown("<h4>Ordenar por</h4>", unsafe_allow_html=True)
    orden = st.selectbox(
        "",
        ["Más recientes", "Más antiguos"]
    )

try:
    conn = get_connection()
    cur = conn.cursor()

    # Query base para obtener solicitudes
    query = """
    SELECT 
        f.id_solicitud,
        f.tipo_estudiante,
        f.periodo,
        f.semestre,
        f.universidad,
        o.programa,
        d.nombre,
        d.apellido,
        d.documento,
        d.país,
        d.ciudad,
        d.direccion,
        d.telefono,
        d.fecha_nacimiento,
        u.email,
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM anexos a 
                WHERE a.id_solicitud = f.id_solicitud 
                AND a.aprobacion = 'pendiente'
            ) THEN 'Pendiente'
            WHEN EXISTS (
                SELECT 1 FROM anexos a 
                WHERE a.id_solicitud = f.id_solicitud
            ) THEN 'Aprobado'
            ELSE 'Sin documentos'
        END as estado_docs,
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM pagos p 
                WHERE p.id_solicitud = f.id_solicitud 
                AND p.estado = 'pagado'
            ) THEN true
            ELSE false
        END as pago_realizado,
        CASE 
            WHEN EXISTS (
                SELECT 1 FROM homologar h 
                WHERE h.id_solicitud = f.id_solicitud 
                AND h.estado = 'Pendiente'
            ) THEN true
            ELSE false
        END as tiene_homologaciones_pendientes,
        CASE
            WHEN f.semestre = 1 THEN 'Prospecto'
            ELSE 'Transferencia Externa'
        END as tipo_real
    FROM formulario f
    JOIN oferta o ON f.id_programa = o.id_programa
    JOIN datos d ON f.documento = d.documento
    JOIN usuario u ON d.id = u.id
    WHERE 1=1
    """ + (" AND CAST(f.id_solicitud AS TEXT) LIKE %s" if id_filtro else "") + \
    (" AND CASE WHEN %s = 'Prospecto' THEN f.semestre = 1 ELSE f.semestre > 1 END" if tipo_filtro != "Todos" else "") + \
    (" AND CASE " + \
     "WHEN %s = 'Pendientes' THEN EXISTS (SELECT 1 FROM anexos a WHERE a.id_solicitud = f.id_solicitud AND a.aprobacion = 'pendiente') " + \
     "WHEN %s = 'Aprobados' THEN EXISTS (SELECT 1 FROM anexos a WHERE a.id_solicitud = f.id_solicitud AND a.aprobacion = 'aprobado') " + \
     "WHEN %s = 'Sin documentos' THEN NOT EXISTS (SELECT 1 FROM anexos a WHERE a.id_solicitud = f.id_solicitud) " + \
     "ELSE true END" if estado_docs_filtro != "Todos" else "") + \
    " ORDER BY f.id_solicitud " + ("DESC" if orden == "Más recientes" else "ASC")

    # Preparar parámetros
    params = []
    if id_filtro:
        params.append(f"%{id_filtro}%")
    if tipo_filtro != "Todos":
        params.append(tipo_filtro)
    if estado_docs_filtro != "Todos":
        params.extend([estado_docs_filtro] * 3)  # Necesitamos el valor tres veces para el CASE

    cur.execute(query, params)
    solicitudes = cur.fetchall()

    if solicitudes:
        # Contadores para el dashboard
        total = len(solicitudes)
        prospectos = sum(1 for s in solicitudes if s[-1] == "Prospecto")  # Usando el tipo_real calculado
        transferencias = sum(1 for s in solicitudes if s[-1] == "Transferencia Externa")  # Usando el tipo_real calculado

        # Dashboard de resumen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='dashboard-card card-prospectos'>
                <h3>Prospectos</h3>
                <p>{prospectos}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='dashboard-card card-transferencia'>
                <h3>Transferencias</h3>
                <p>{transferencias}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='dashboard-card card-total'>
                <h3>Total Solicitudes</h3>
                <p>{total}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Mostrar solicitudes
        for solicitud in solicitudes:
            id_solicitud, tipo_estudiante, periodo, semestre, universidad, programa, nombre, apellido, documento, pais, ciudad, direccion, telefono, fecha_nacimiento, email, estado_docs, pago_realizado, tiene_homologaciones, tipo_real = solicitud
            
            estado_clase = {
                'Pendiente': 'estado-pendiente',
                'Aprobado': 'estado-aprobado',
                'Sin documentos': 'estado-rechazado'
            }.get(estado_docs, 'estado-pendiente')

            with st.expander(f"Solicitud #{id_solicitud} - {nombre} {apellido} - {programa}"):
                st.markdown(f"<p class='{estado_clase}'>Estado documentos: {estado_docs}</p>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""<div class='info-card'>
                    <h4>Información del estudiante</h4>
                    <p><strong>Nombre completo:</strong> {nombre} {apellido}</p>
                    <p><strong>Documento:</strong> {documento}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Teléfono:</strong> {telefono}</p>
                    <p><strong>Fecha de nacimiento:</strong> {fecha_nacimiento}</p>
                    </div>""", unsafe_allow_html=True)

                    st.markdown(f"""<div class='info-card'>
                    <h4>Ubicación</h4>
                    <p><strong>País:</strong> {pais}</p>
                    <p><strong>Ciudad:</strong> {ciudad}</p>
                    <p><strong>Dirección:</strong> {direccion}</p>
                    </div>""", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""<div class='info-card'>
                    <h4>Información académica</h4>
                    <p><strong>Tipo de estudiante:</strong> {tipo_real}</p>
                    <p><strong>Programa:</strong> {programa}</p>
                    <p><strong>Periodo:</strong> {periodo}</p>
                    <p><strong>Semestre:</strong> {semestre}</p>
                    <p><strong>Universidad de origen:</strong> {universidad if tipo_real == "Transferencia Externa" else "N/A"}</p>
                    </div>""", unsafe_allow_html=True)

                    st.markdown(f"""<div class='info-card'>
                    <h4>Estado de la solicitud</h4>
                    <p><strong>Documentos:</strong> {estado_docs}</p>
                    <p><strong>Pago:</strong> {"Realizado" if pago_realizado else "Pendiente"}</p>
                    <p><strong>Homologaciones pendientes:</strong> {"Sí" if tiene_homologaciones else "No"}</p>
                    </div>""", unsafe_allow_html=True)

                # Sección de navegación
                st.markdown("""<div class='nav-section'>
                <h4>Acciones disponibles</h4>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                
                with col1:
                    if estado_docs != "Sin documentos":
                        st.markdown(f"""
                        <a href="/admin/documentos?id={id_solicitud}" target="_self" class="nav-button documentos">
                            {"✓ Revisar" if estado_docs == "Pendiente" else "👁 Ver"} documentos
                        </a>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No hay documentos para revisar")

                with col2:
                    if tipo_real == "Transferencia Externa":
                        st.markdown(f"""
                        <a href="/admin/homologaciones?id={id_solicitud}" target="_self" class="nav-button homologaciones">
                            {"✓ Revisar" if tiene_homologaciones else "👁 Ver"} homologaciones
                        </a>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No aplican homologaciones")

                st.markdown("</div>", unsafe_allow_html=True)

                # TODO: Agregar detalles del formulario de inscripción

    else:
        st.info("No se encontraron solicitudes que coincidan con los filtros seleccionados")

except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()