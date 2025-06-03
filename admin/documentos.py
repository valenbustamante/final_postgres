import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
import base64
from utils import get_connection

load_dotenv()

st.title('Gestión de documentos')

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
    h1, h2, h3 {
        color: var(--text-color);
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, Helvetica Neue, sans-serif;
    }

    /* Contenedor de filtros */
    .filtros-container {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
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

    /* Botones */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        padding: 8px 16px;
        transition: all 0.2s;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 14px;
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .stButton.aprobar button {
        background-color: var(--secondary-color);
        color: white;
    }

    .stButton.rechazar button {
        background-color: var(--primary-color);
        color: white;
    }

    /* Cards para documentos */
    .doc-card {
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .doc-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Estados */
    .estado-pendiente {
        color: #FFA500;
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(255,165,0,0.1);
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
        display: inline-html;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(255,90,95,0.1);
    }
    .estado-sin-docs {
        color: #808080;
        font-weight: 600;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: rgba(128,128,128,0.1);
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

    .card-procesadas {
        background: linear-gradient(135deg, var(--secondary-color) 0%, #008B80 100%);
        box-shadow: 0 4px 20px rgba(0, 166, 153, 0.2);
    }

    .card-sin-documentos {
        background: linear-gradient(135deg, #607D8B 0%, #455A64 100%);
        box-shadow: 0 4px 20px rgba(96, 125, 139, 0.2);
    }

    .dashboard-card:hover {
        transform: translateY(-5px);
    }

    /* Mensajes de estado */
    .success-box, .info-box, .warning-box {
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }

    .success-box:hover, .info-box:hover, .warning-box:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


def display_pdf(pdf_data, file_name):
    """Función para mostrar PDF desde datos binarios"""
    if pdf_data:
        if isinstance(pdf_data, memoryview):
            pdf_data = pdf_data.tobytes()
        
        b64 = base64.b64encode(pdf_data).decode()
        pdf_display = f'''
        <iframe src="data:application/pdf;base64,{b64}" 
                width="100%" height="600" type="application/pdf">
        </iframe>
        '''
        st.markdown(pdf_display, unsafe_allow_html=True)
        
    else:
        st.warning("No se pudo cargar el documento")


col1, col2, col3 = st.columns([2,1,1])

id_solicitud_param = st.query_params.get("id", [None])[0]

with col1:
    st.markdown("<h4>Buscar por ID de solicitud</h4>", unsafe_allow_html=True)
    id_filtro = st.text_input("", value=id_solicitud_param if id_solicitud_param else "", placeholder="Ingrese el número de solicitud...")

with col2:
    st.markdown("<h4>Estado</h4>", unsafe_allow_html=True)
    estado_filtro = st.selectbox(
        "",
        ["Todos", "Pendientes", "Aprobados", "Sin documentos"]
    )

with col3:
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
    WITH solicitud_estado AS (
        SELECT 
            f.id_solicitud,
            f.periodo,
            o.programa,
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM anexos a 
                    WHERE a.id_solicitud = f.id_solicitud 
                    AND (a.aprobacion IS NULL OR a.aprobacion = 'pendiente')
                ) THEN 1
                WHEN EXISTS (
                    SELECT 1 FROM anexos a 
                    WHERE a.id_solicitud = f.id_solicitud
                ) THEN 2
                ELSE 3
            END as estado_orden
        FROM formulario f
        JOIN oferta o ON f.id_programa = o.id_programa
        LEFT JOIN aprobados ap ON f.id_solicitud = ap.id_solicitud
        WHERE 1=1
        """ + (" AND CAST(f.id_solicitud AS TEXT) LIKE %s" if id_filtro else "") + """
    )
    SELECT 
        id_solicitud,
        periodo,
        programa,
        estado_orden
    FROM solicitud_estado
    """ + ("""
    WHERE estado_orden = """ + {
        "Pendientes": "1",
        "Aprobados": "2",
        "Sin documentos": "3"
    }.get(estado_filtro, "estado_orden") if estado_filtro != "Todos" else "") + """
    ORDER BY estado_orden, id_solicitud """ + ("DESC" if orden == "Más recientes" else "ASC")

    params = []
    if id_filtro:
        params.append(f"%{id_filtro}%")

    cur.execute(query, params)
    todas_solicitudes = cur.fetchall()

    if todas_solicitudes:

        pendientes = sum(1 for s in todas_solicitudes if s[3] == 1)
        con_docs = sum(1 for s in todas_solicitudes if s[3] == 2)
        sin_docs = sum(1 for s in todas_solicitudes if s[3] == 3)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class='dashboard-card card-pendientes'>
                <h3>Pendientes de revisión</h3>
                <p>{pendientes}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='dashboard-card card-procesadas'>
                <h3>Documentos procesados</h3>
                <p>{con_docs}</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='dashboard-card card-sin-documentos'>
                <h3>Sin documentos</h3>
                <p>{sin_docs}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        for solicitud in todas_solicitudes:
            id_solicitud, periodo, programa, estado_orden = solicitud

            estado_texto = "PENDIENTE" if estado_orden == 1 else "APROBADA" if estado_orden == 2 else "SIN DOCUMENTOS"
            estado_clase = "estado-pendiente" if estado_orden == 1 else "estado-aprobado" if estado_orden == 2 else "estado-sin-docs"
            
            with st.expander(f"Solicitud #{id_solicitud} - {programa} - Periodo {periodo}"):
                st.markdown(f"<p class='{estado_clase}'>Estado: {estado_texto}</p>", unsafe_allow_html=True)
                
                cur.execute("""
                    SELECT id_documento, nombre_doc, archivo, aprobacion 
                    FROM anexos 
                    WHERE id_solicitud = %s
                    ORDER BY id_documento
                """, (id_solicitud,))
                documentos = cur.fetchall()

                if documentos:
                    st.markdown(f"<div class='info-box'>Total de documentos: {len(documentos)}</div>", unsafe_allow_html=True)
                    
                    for doc_id, nombre_doc, archivo, aprobacion in documentos:
                        st.markdown("<div class='doc-card'>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"<h3 style='margin:0'>{nombre_doc}</h3>", unsafe_allow_html=True)
                        with col2:
                            estado_doc = "APROBADO" if aprobacion == "aprobado" else "RECHAZADO" if aprobacion == "rechazado" else "PENDIENTE"
                            estado_clase_doc = "estado-aprobado" if aprobacion == "aprobado" else "estado-rechazado" if aprobacion == "rechazado" else "estado-pendiente"
                            st.markdown(f"<p class='{estado_clase_doc}' style='text-align:right'>{estado_doc}</p>", unsafe_allow_html=True)
                        
                        if archivo:
                            display_pdf(archivo, f"{nombre_doc}_{id_solicitud}.pdf")
                            
                            if estado_orden != 2:
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("<div class='stButton aprobar'>", unsafe_allow_html=True)
                                    if st.button("Aprobar", key=f"aprobar_{doc_id}"):
                                        cur.execute("""
                                            UPDATE anexos 
                                            SET aprobacion = 'aprobado'
                                            WHERE id_documento = %s
                                        """, (doc_id,))
                                        conn.commit()
                                        st.rerun()
                                    st.markdown("</div>", unsafe_allow_html=True)
                                with col2:
                                    st.markdown("<div class='stButton rechazar'>", unsafe_allow_html=True)
                                    if st.button("Rechazar", key=f"rechazar_{doc_id}"):
                                        cur.execute("""
                                            UPDATE anexos 
                                            SET aprobacion = 'rechazado'
                                            WHERE id_documento = %s
                                        """, (doc_id,))
                                        conn.commit()
                                        st.rerun()
                                    st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.warning("Documento sin contenido")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    if estado_orden != 2:
                        todos_aprobados = all(doc[3] == 'aprobado' for doc in documentos)
                        if todos_aprobados:
                            st.markdown("<div class='success-box'>Todos los documentos han sido aprobados</div>", unsafe_allow_html=True)
                            st.markdown("<div class='stButton aprobar'>", unsafe_allow_html=True)
                            if st.button("Aprobar Solicitud Completa", key=f"aprobar_solicitud_{id_solicitud}"):
                                cur.execute("""
                                    INSERT INTO aprobados (id_solicitud, aprobado_por)
                                    VALUES (%s, %s)
                                """, (id_solicitud, st.session_state.get('user_id', 'admin')))
                                conn.commit()
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='success-box'>Esta solicitud ya ha sido completamente aprobada</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='warning-box'>No se encontraron documentos para esta solicitud</div>", unsafe_allow_html=True)

    else:
        st.info("No se encontraron solicitudes")

except Exception as e:
    st.error(f"Error de conexión con la base de datos: {e}")
    st.exception(e)

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()