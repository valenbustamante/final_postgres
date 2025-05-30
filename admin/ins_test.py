import streamlit as st
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv
from utils import get_connection
load_dotenv()

st.title('Aprobación de solicitudes')


st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .approve-button {
        background-color: #28a745;
        color: white;
    }
    .reject-button {
        background-color: #dc3545;
        color: white;
    }
    .document-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .info-box {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
    .estado-pendiente {
        color: #FFA500;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(255, 165, 0, 0.1);
        display: inline-block;
        border: 1px solid rgba(255, 165, 0, 0.2);
        font-weight: 500;
    }
    .estado-aprobada {
        color: #28a745;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(40, 167, 69, 0.1);
        display: inline-block;
        border: 1px solid rgba(40, 167, 69, 0.2);
        font-weight: 500;
    }
    .estado-rechazada {
        color: #dc3545;
        padding: 5px 10px;
        border-radius: 5px;
        background-color: rgba(220, 53, 69, 0.1);
        display: inline-block;
        border: 1px solid rgba(220, 53, 69, 0.2);
        font-weight: 500;
    }
    .info-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .info-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .info-card h4 {
        color: #2c3e50;
        margin-bottom: 12px;
        font-size: 1.1em;
        font-weight: 600;
        border-bottom: 2px solid #f1f1f1;
        padding-bottom: 8px;
    }
    .info-card p {
        margin-bottom: 8px;
        color: #444;
    }
    .info-card strong {
        color: #2c3e50;
    }
    .nav-section {
        margin-top: 20px;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .nav-section h4 {
        color: #2c3e50;
        margin-bottom: 15px;
        font-weight: 600;
        border-bottom: 2px solid #f1f1f1;
        padding-bottom: 8px;
    }
    .nav-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        background-color: #007bff;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        text-align: center;
        width: 100%;
        transition: all 0.3s ease;
        border: none;
        font-weight: 500;
    }
    .nav-button:hover {
        background-color: #0056b3;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .document-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .document-item:hover {
        background-color: #f1f3f5;
        transform: translateX(5px);
    }
    .document-item span {
        font-size: 1em;
        font-weight: 500;
    }
    /* Style for download button in document section */
    .stDownloadButton>button {
        width: 100%;
        background-color: #6c757d;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stDownloadButton>button:hover {
        background-color: #5a6268;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

def get_pending_approvals():
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
    SELECT 
        f.id_solicitud,d.nombre,d.apellido,d.documento,o.programa,o.periodo,f.tipo_estudiante,f.semestre,f.universidad
    FROM formulario f
    JOIN datos d ON f.documento = d.documento
    JOIN oferta o ON f.id_programa = o.id_programa
    WHERE f.id_solicitud NOT IN (SELECT id_solicitud FROM aprobados)
    AND f.id_solicitud IN (
        SELECT id_solicitud 
        FROM anexos 
        GROUP BY id_solicitud 
        HAVING COUNT(*) = (SELECT COUNT(*) FROM requisitos WHERE id_programa = f.id_programa)
    )
    AND f.id_solicitud IN (
        SELECT id_solicitud 
        FROM homologar 
        WHERE estado = 'Aprobada'
    )
    AND f.id_solicitud IN (
        SELECT id_solicitud 
        FROM pagos 
        WHERE estado = 'Aprobada'
    )
    """
    
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def get_attached_documents(request_id):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
    SELECT nombre_doc, archivo
    FROM anexos
    WHERE id_solicitud = %s
    """
    
    cur.execute(query, (request_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def approve_request(request_id, admin_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO aprobados (id_solicitud, aprobado_por) VALUES (%s, %s)",
            (request_id, admin_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error al aprobar la solicitud: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def reject_request(request_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM aprobados WHERE id_solicitud = %s", (request_id,))
        cur.execute("DELETE FROM homologar WHERE id_solicitud = %s", (request_id,))
        cur.execute("DELETE FROM pagos WHERE id_solicitud = %s", (request_id,))
        cur.execute("DELETE FROM anexos WHERE id_solicitud = %s", (request_id,))
        cur.execute("DELETE FROM formulario WHERE id_solicitud = %s", (request_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error al rechazar la solicitud: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def main():

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
 
    if not st.session_state.user_id:
        st.warning("Por favor inicie sesión para acceder a esta página.")
        return

    col1, col2, col3, col4 = st.columns([2,1,1,1])

    id_solicitud_param = st.query_params.get("id", [None])[0]

    with col1:
        st.markdown("<h4>Buscar por ID de solicitud</h4>", unsafe_allow_html=True)
        id_filtro = st.text_input("", value=id_solicitud_param if id_solicitud_param else "", placeholder="Ingrese el número de solicitud...")

    with col2:
        st.markdown("<h4>Tipo de Estudiante</h4>", unsafe_allow_html=True)
        tipo_filtro = st.selectbox(
            "",
            ["Todos", "Nuevo", "Transferencia externa"]
        )

    with col3:
        st.markdown("<h4>Programa</h4>", unsafe_allow_html=True)
        programa_filtro = st.selectbox(
            "",
            ["Todos", "Ingeniería", "Administración", "Psicología", "Derecho"]
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
        query = """
        SELECT 
            f.id_solicitud,
            d.nombre,
            d.apellido,
            d.documento,
            o.programa,
            o.periodo,
            f.tipo_estudiante,
            f.semestre,
            f.universidad,
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
            END as tiene_homologaciones_pendientes
        FROM formulario f
        JOIN oferta o ON f.id_programa = o.id_programa
        JOIN datos d ON f.documento = d.documento
        JOIN usuario u ON d.id = u.id
        WHERE f.id_solicitud NOT IN (SELECT id_solicitud FROM aprobados)
        """ + (" AND CAST(f.id_solicitud AS TEXT) LIKE %s" if id_filtro else "") + \
        (" AND f.tipo_estudiante = %s" if tipo_filtro != "Todos" else "") + \
        (" AND o.programa = %s" if programa_filtro != "Todos" else "") + \
        " ORDER BY f.id_solicitud " + ("DESC" if orden == "Más recientes" else "ASC")

        params = []
        if id_filtro:
            params.append(f"%{id_filtro}%")
        if tipo_filtro != "Todos":
            params.append(tipo_filtro)
        if programa_filtro != "Todos":
            params.append(programa_filtro)

        cur.execute(query, params)
        solicitudes = cur.fetchall()

        if solicitudes:
            st.write(f"Se encontraron {len(solicitudes)} solicitudes pendientes de aprobación")

            for solicitud in solicitudes:
                id_solicitud, nombre, apellido, documento, programa, periodo, tipo_estudiante, semestre, universidad, email, estado_docs, pago_realizado, tiene_homologaciones = solicitud
                
                estado_clase = {
                    'Pendiente': 'estado-pendiente',
                    'Aprobado': 'estado-aprobada',
                    'Sin documentos': 'estado-rechazada'
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
                        </div>""", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""<div class='info-card'>
                        <h4>Información académica</h4>
                        <p><strong>Tipo de estudiante:</strong> {tipo_estudiante}</p>
                        <p><strong>Programa:</strong> {programa}</p>
                        <p><strong>Periodo:</strong> {periodo}</p>
                        <p><strong>Semestre:</strong> {semestre}</p>
                        <p><strong>Universidad de origen:</strong> {universidad if tipo_estudiante == "Transferencia externa" else "N/A"}</p>
                        </div>""", unsafe_allow_html=True)

                    st.markdown(f"""<div class='info-card'>
                    <h4>Estado de la solicitud</h4>
                    <p><strong>Documentos:</strong> {estado_docs}</p>
                    <p><strong>Pago:</strong> {"Realizado" if pago_realizado else "Pendiente"}</p>
                    <p><strong>Homologaciones pendientes:</strong> {"Sí" if tiene_homologaciones else "No"}</p>
                    </div>""", unsafe_allow_html=True)

                    st.markdown("""<div class='info-card'>
                    <h4>Documentos Anexados</h4>
                    </div>""", unsafe_allow_html=True)
                    
                    documentos = get_attached_documents(id_solicitud)
                    if documentos:
                        for doc in documentos:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"""<div class='document-item'>
                                    <span style='color: #2c3e50;'>📄 {doc[0]}</span>
                                </div>""", unsafe_allow_html=True)
                            with col2:
                                if doc[1]:  # Si hay archivo
                                    file_data = bytes(doc[1])
                                    st.download_button(
                                        label="⬇️ Descargar",
                                        data=file_data,
                                        file_name=f"{doc[0]}.pdf",
                                        mime="application/pdf",
                                        key=f"doc_{id_solicitud}_{doc[0]}"
                                    )
                    else:
                        st.info("No hay documentos adjuntos para esta solicitud.")

                    st.markdown("""<div class='nav-section'>
                    <h4>Acciones disponibles</h4>
                    </div>""", unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✓ Aprobar solicitud", key=f"aprobar_{id_solicitud}"):
                            try:
                                cur.execute(
                                    "INSERT INTO aprobados (id_solicitud, aprobado_por) VALUES (%s, %s)",
                                    (id_solicitud, st.session_state.user_id)
                                )
                                conn.commit()
                                st.success("Solicitud aprobada exitosamente")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error al aprobar la solicitud: {e}")

                    with col2:
                        if st.button("✗ Rechazar solicitud", key=f"rechazar_{id_solicitud}"):
                            try:
                                cur.execute("DELETE FROM aprobados WHERE id_solicitud = %s", (id_solicitud,))
                                cur.execute("DELETE FROM homologar WHERE id_solicitud = %s", (id_solicitud,))
                                cur.execute("DELETE FROM pagos WHERE id_solicitud = %s", (id_solicitud,))
                                cur.execute("DELETE FROM anexos WHERE id_solicitud = %s", (id_solicitud,))
                                cur.execute("DELETE FROM formulario WHERE id_solicitud = %s", (id_solicitud,))
                                conn.commit()
                                st.success("Solicitud rechazada exitosamente")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Error al rechazar la solicitud: {e}")

        else:
            st.info("No se encontraron solicitudes pendientes de aprobación")

    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()