import streamlit as st
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host='localhost',
        database=os.getenv('DATABASE'),
        user=os.getenv('USER'),
        password=os.getenv('PASSWORD'),
        port='5432'
    )

st.title('Gestión de Homologaciones')

# Filtro id solicitud
id_filtro = st.text_input("Filtrar por ID de Solicitud")

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
    WHERE (%s = '' OR CAST(h.id_solicitud AS TEXT) = %s)
    ORDER BY 
        CASE h.estado 
            WHEN 'Pendiente' THEN 1
            WHEN 'Rechazada' THEN 2
            WHEN 'Aprobada' THEN 3
            ELSE 4 
        END,
        h.id_solicitud
    """
    cur.execute(query, (id_filtro, id_filtro))
    homologaciones = cur.fetchall()

    if homologaciones:
        for solicitud in homologaciones:
            id_solicitud, id_asignatura, estado, justificacion, decision, nombre_asignatura, descripcion, programa, nombre_usuario, email_usuario = solicitud

            with st.expander(f"Solicitud #{id_solicitud} - {nombre_asignatura} [{estado}]"):
                st.markdown(f"**Nombre del estudiante:** {nombre_usuario}")
                st.markdown(f"**Email:** {email_usuario}")
                st.markdown(f"**Programa Académico:** {programa}")
                st.markdown(f"**Asignatura a homologar:** {nombre_asignatura}")
                st.markdown(f"**Descripción:** {descripcion}")
                st.markdown(f"**Justificación del estudiante:** {justificacion}")
                st.markdown(f"**Decisión actual:** {decision or 'Sin decisión'}")

                # Formulario para actualizar resolución
                with st.form(key=f"form_{id_solicitud}_{id_asignatura}"):
                    nuevo_estado = st.selectbox(
                        "Estado",
                        ["Pendiente", "Aprobada", "Rechazada"],
                        index=["Pendiente", "Aprobada", "Rechazada"].index(estado) if estado in ["Pendiente", "Aprobada", "Rechazada"] else 0,
                        key=f"estado_{id_solicitud}_{id_asignatura}"
                    )
                    nueva_decision = st.text_input("Decisión administrativa", value=decision or "Por definir", key=f"decision_{id_solicitud}_{id_asignatura}")
                    submit_button = st.form_submit_button("Guardar")

                    if submit_button:
                        try:
                            cur.execute("""
                                UPDATE homologar 
                                SET estado = %s,  decision = %s
                                WHERE id_solicitud = %s AND id_asignatura = %s
                            """, (nuevo_estado, nueva_decision, id_solicitud, id_asignatura))
                            conn.commit()
                            st.success(f"Homologación {id_solicitud}-{id_asignatura} actualizada.")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error al actualizar: {e}")
    else:
        st.info("No se encontraron solicitudes de homologación.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
