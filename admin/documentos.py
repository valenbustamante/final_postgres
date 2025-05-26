import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv
import base64

load_dotenv()

st.write('workss')

def get_connection():
    return psycopg2.connect(
        host='localhost',
        database=os.getenv('DATABASE'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        port='5432'
    )

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
        
        st.download_button(
            label=f"Descargar {file_name}",
            data=pdf_data,
            file_name=file_name,
            mime="application/pdf"
        )
    else:
        st.warning("No se pudo cargar el documento")

st.title('Revisión de Documentos')
st.markdown("---")

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
                ) THEN 1  -- Prioridad 1: Tiene documentos pendientes de aprobación
                WHEN EXISTS (
                    SELECT 1 FROM anexos a 
                    WHERE a.id_solicitud = f.id_solicitud
                ) THEN 2  -- Prioridad 2: Tiene documentos (todos aprobados o rechazados)
                ELSE 3    -- Prioridad 3: No tiene documentos
            END as estado_orden
        FROM formulario f
        JOIN oferta o ON f.id_programa = o.id_programa
        LEFT JOIN aprobados ap ON f.id_solicitud = ap.id_solicitud
    )
    SELECT 
        id_solicitud,
        periodo,
        programa,
        estado_orden
    FROM solicitud_estado
    ORDER BY estado_orden, id_solicitud DESC
    """
    
    cur.execute(query)
    todas_solicitudes = cur.fetchall()

    if todas_solicitudes:
        st.success(f"Se encontraron {len(todas_solicitudes)} solicitudes en total")
        
        for solicitud in todas_solicitudes:
            id_solicitud, periodo, programa, estado_orden = solicitud

            estado_texto = "PENDIENTE" if estado_orden == 1 else "APROBADA" if estado_orden == 2 else "SIN DOCUMENTOS"
            
            with st.expander(f"Solicitud #{id_solicitud} - Programa: {programa} - Periodo: {periodo} [{estado_texto}]"):
                cur.execute("""
                    SELECT id_documento, nombre_doc, archivo, aprobacion 
                    FROM anexos 
                    WHERE id_solicitud = %s
                    ORDER BY id_documento
                """, (id_solicitud,))
                documentos = cur.fetchall()

                if documentos:
                    st.info(f"Total de documentos: {len(documentos)}")
                    
                    if len(documentos) == 1:
                        doc_id, nombre_doc, archivo, aprobacion = documentos[0]
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{nombre_doc}**")
                        with col2:
                            estado_actual = "APROBADO" if aprobacion == "aprobado" else "RECHAZADO" if aprobacion == "rechazado" else "PENDIENTE"
                            st.markdown(f"**Estado:** {estado_actual}")
                        
                        if archivo:
                            display_pdf(archivo, f"{nombre_doc}_{id_solicitud}.pdf")
                            
                            if estado_orden != 2:
                                col1, col2, col3 = st.columns([1, 1, 2])
                                with col1:
                                    if st.button("Aprobar", key=f"aprobar_{doc_id}"):
                                        cur.execute("""
                                            UPDATE anexos 
                                            SET aprobacion = 'aprobado'
                                            WHERE id_documento = %s
                                        """, (doc_id,))
                                        conn.commit()
                                        st.rerun()
                                with col2:
                                    if st.button("Rechazar", key=f"rechazar_{doc_id}"):
                                        cur.execute("""
                                            UPDATE anexos 
                                            SET aprobacion = 'rechazado'
                                            WHERE id_documento = %s
                                        """, (doc_id,))
                                        conn.commit()
                                        st.rerun()
                        else:
                            st.warning("Documento sin contenido")
                    else:
                        tab_names = [f"{doc[1]}" for doc in documentos]
                        tabs = st.tabs(tab_names)
                        
                        for i, (doc_id, nombre_doc, archivo, aprobacion) in enumerate(documentos):
                            with tabs[i]:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"**Nombre del documento:** {nombre_doc}")
                                with col2:
                                    estado_actual = "APROBADO" if aprobacion == "aprobado" else "RECHAZADO" if aprobacion == "rechazado" else "PENDIENTE"
                                    st.markdown(f"**Estado:** {estado_actual}")
                                
                                if archivo:
                                    display_pdf(archivo, f"{nombre_doc}_{id_solicitud}.pdf")
                                    if estado_orden != 2:
                                        col1, col2, col3 = st.columns([1, 1, 2])
                                        with col1:
                                            if st.button("Aprobar", key=f"aprobar_{doc_id}"):
                                                cur.execute("""
                                                    UPDATE anexos 
                                                    SET aprobacion = 'aprobado'
                                                    WHERE id_documento = %s
                                                """, (doc_id,))
                                                conn.commit()
                                                st.rerun()
                                        with col2:
                                            if st.button("Rechazar", key=f"rechazar_{doc_id}"):
                                                cur.execute("""
                                                    UPDATE anexos 
                                                    SET aprobacion = 'rechazado'
                                                    WHERE id_documento = %s
                                                """, (doc_id,))
                                                conn.commit()
                                                st.rerun()
                                else:
                                    st.warning("Documento sin contenido")
                                    
                    if estado_orden != 2:
                        todos_aprobados = all(doc[3] == 'aprobado' for doc in documentos)
                        if todos_aprobados:
                            st.success("Todos los documentos han sido aprobados")
                            if st.button("Aprobar Solicitud Completa", key=f"aprobar_solicitud_{id_solicitud}"):
                                cur.execute("""
                                    INSERT INTO aprobados (id_solicitud, aprobado_por)
                                    VALUES (%s, %s)
                                """, (id_solicitud, st.session_state.get('user_id', 'admin')))
                                conn.commit()
                                st.rerun()
                    else:
                        st.success("Esta solicitud ya ha sido completamente aprobada")
                else:
                    st.warning("No se encontraron documentos para esta solicitud")

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