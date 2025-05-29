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

st.title('Gestión de Pagos')


id_filtro = st.text_input("Filtrar por ID de Solicitud")

try:
    conn = get_connection()
    cur = conn.cursor()

    
    query = """
    SELECT p.id_solicitud, p.fecha, p.estado,
           d.nombre, u.email, o.programa
    FROM pagos p
    JOIN formulario f ON p.id_solicitud = f.id_solicitud
    JOIN datos d ON f.documento = d.documento
    JOIN usuario u ON d.id = u.id
    JOIN oferta o ON f.id_programa = o.id_programa
    WHERE (%s = '' OR CAST(p.id_solicitud AS TEXT) = %s)
    ORDER BY p.fecha DESC
    """
    cur.execute(query, (id_filtro, id_filtro))
    pagos = cur.fetchall()

    if pagos:
        for pago in pagos:
            id_solicitud, fecha_pago, estado, nombre_usuario, email_usuario, programa = pago

            with st.expander(f"Pago - Solicitud #{id_solicitud}"):
                st.markdown(f"**Nombre del estudiante:** {nombre_usuario}")
                st.markdown(f"**Email:** {email_usuario}")
                st.markdown(f"**Programa:** {programa}")
                st.markdown(f"**Fecha del pago:** {fecha_pago}")
                st.markdown(f"**Estado del pago:** {estado}")
    else:
        st.info("No se encontraron pagos.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")

finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
