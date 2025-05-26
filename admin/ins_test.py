import streamlit as st
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="Aprobación de Solicitudes",
    layout="wide"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
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
    }
    .info-box {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def get_connection():
    return psycopg2.connect(
        host='localhost',
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        port='5432'
    )

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
 
    st.markdown("# Aprobación de Solicitudes")

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
 
    if not st.session_state.user_id:
        st.warning("Por favor inicie sesión para acceder a esta página.")
        return

    pending_approvals = get_pending_approvals()
    
    if not pending_approvals:
        st.info("ℹNo hay solicitudes pendientes de aprobación que cumplan con todos los requisitos.")
        return

    for request in pending_approvals:
        with st.expander(f"Solicitud #{request[0]} - {request[1]} {request[2]}", expanded=True):
            st.markdown("### 👤 Información del Estudiante")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="info-box">
                    <strong>Documento:</strong> {request[3]}<br>
                    <strong>Programa:</strong> {request[4]}<br>
                    <strong>Periodo:</strong> {request[5]}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="info-box">
                    <strong>Tipo de Estudiante:</strong> {request[6]}<br>
                    <strong>Semestre:</strong> {request[7]}<br>
                    <strong>Universidad:</strong> {request[8]}
                </div>
                """, unsafe_allow_html=True)
            
            # Documentos anexados
            st.markdown("### Documentos Anexados")
            documentos = get_attached_documents(request[0])
            for doc in documentos:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📄 {doc[0]}")
                with col2:
                    if doc[1]:  # Si hay archivo
                        file_data = bytes(doc[1])
                        st.download_button(
                            label="⬇️ Descargar",
                            data=file_data,
                            file_name=f"{doc[0]}.pdf",
                            mime="application/pdf",
                            key=f"doc_{request[0]}_{doc[0]}"
                        )
            st.markdown('</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Aprobar Solicitud", key=f"approve_{request[0]}"):
                    if approve_request(request[0], st.session_state.user_id):
                        st.success("Solicitud aprobada exitosamente")
                        st.rerun()
            
            with col2:
                if st.button("Rechazar Solicitud", key=f"reject_{request[0]}"):
                    if reject_request(request[0]):
                        st.success("Solicitud rechazada")
                        st.rerun()

if __name__ == "__main__":
    main()