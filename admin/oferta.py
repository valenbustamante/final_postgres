import streamlit as st
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv
from utils import get_connection
load_dotenv()

st.title('Gestión de oferta académica')

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
    .info-box {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .subject-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 4px solid #007bff;
    }
    .requirement-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 4px solid #ffc107;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .period-header {
        background-color: #007bff;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def get_academic_programs():
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
    SELECT id_programa, programa, periodo, semestres, titulo, inscripcion, matricula
    FROM uninorte_db.oferta
    ORDER BY programa, periodo DESC
    """
    
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def get_programs_by_period(period):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
    SELECT id_programa, programa, periodo, semestres, titulo, inscripcion, matricula
    FROM uninorte_db.oferta
    WHERE periodo = %s
    ORDER BY programa
    """
    
    cur.execute(query, (period,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def get_program_subjects(program_id):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
    SELECT id_asignatura, nombre, creditos, semestre, nombre_asignatura, descripcion
    FROM uninorte_db.asignaturas
    WHERE id_programa = %s
    ORDER BY semestre, nombre
    """
    
    cur.execute(query, (program_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def get_program_requirements(program_id):
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
    SELECT nombre_doc, tipo_req
    FROM uninorte_db.requisitos
    WHERE id_programa = %s
    ORDER BY nombre_doc
    """
    
    cur.execute(query, (program_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def add_academic_program(program, period, semesters, title, registration_fee, tuition_fee):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO uninorte_db.oferta (programa, periodo, semestres, titulo, inscripcion, matricula)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_programa
            """,
            (program, period, semesters, title, registration_fee, tuition_fee)
        )
        program_id = cur.fetchone()[0]
        conn.commit()
        return program_id
    except Exception as e:
        conn.rollback()
        st.error(f"Error al agregar el programa: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def add_subject(program_id, name, credits, semester, subject_code, description):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO uninorte_db.asignaturas (id_programa, nombre, creditos, semestre, nombre_asignatura, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_asignatura
            """,
            (program_id, name, credits, semester, subject_code, description)
        )
        subject_id = cur.fetchone()[0]
        conn.commit()
        return subject_id
    except Exception as e:
        conn.rollback()
        st.error(f"Error al agregar la asignatura: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def add_requirement(program_id, requirement_name, requirement_type):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO uninorte_db.requisitos (id_programa, nombre_doc, tipo_req)
            VALUES (%s, %s, %s)
            """,
            (program_id, requirement_name, requirement_type)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error al agregar el requisito: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def delete_program(program_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM uninorte_db.requisitos WHERE id_programa = %s", (program_id,))
        cur.execute("DELETE FROM uninorte_db.asignaturas WHERE id_programa = %s", (program_id,))
        cur.execute("DELETE FROM uninorte_db.oferta WHERE id_programa = %s", (program_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error al eliminar el programa: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def delete_subject(subject_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM uninorte_db.asignaturas WHERE id_asignatura = %s", (subject_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error al eliminar la asignatura: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def delete_requirement(program_id, requirement_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM uninorte_db.requisitos WHERE id_programa = %s AND nombre_doc = %s", 
                   (program_id, requirement_name))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error al eliminar el requisito: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def main():
    current_year = datetime.now().year
    
    period_input = st.text_input(
        "Ingrese el Periodo Académico (formato: AAAA10 o AAAA30)",
        placeholder=f"Ejemplo: {current_year}10"
    )
    
    # Validate and convert period format
    if period_input:
        try:
            if len(period_input) == 6 and period_input[:4].isdigit() and period_input[4:] in ['10', '30']:
                selected_period = period_input
            else:
                st.error("El periodo debe tener el formato AAAA10 o AAAA30 (donde AAAA es el año)")
                selected_period = None
        except ValueError:
            st.error("El periodo debe tener el formato AAAA10 o AAAA30 (donde AAAA es el año)")
            selected_period = None
    else:
        selected_period = None
    
    if selected_period:
        tab1, tab2, tab3 = st.tabs(["Programas Académicos", "Asignaturas", "Requisitos"])
        with tab1:
            st.header("Gestión de Programas Académicos")

            with st.expander("Agregar Nuevo Programa", expanded=True):
                with st.form("nuevo_programa_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        programa = st.text_input("Nombre del Programa")
                        semestres = st.number_input("Número de Semestres", min_value=1, max_value=20, step=1)
                    with col2:
                        titulo = st.text_input("Título a Otorgar")
                        inscripcion = st.number_input("Valor Inscripción", min_value=0, step=100000)
                        matricula = st.number_input("Valor Matrícula Base", min_value=0, step=100000)
                    
                    submit_button = st.form_submit_button("Agregar Programa")
                    
                    if submit_button:
                        if programa and titulo:
                            program_id = add_academic_program(programa, selected_period, semestres, 
                                                            titulo, inscripcion, matricula)
                            if program_id:
                                st.success("Programa agregado exitosamente")
                                st.rerun()
                        else:
                            st.error("Por favor complete todos los campos obligatorios")

            st.subheader(f"Programas Existentes - Periodo {selected_period[:4]}-{selected_period[4:]}")
            programas = get_programs_by_period(selected_period)
            
            if not programas:
                st.info(f"No hay programas registrados para el periodo {selected_period[:4]}-{selected_period[4:]}")
            else:
                for programa in programas:
                    with st.expander(f"{programa[1]}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="info-box">
                                <strong>ID:</strong> {programa[0]}<br>
                                <strong>Título:</strong> {programa[4]}<br>
                                <strong>Semestres:</strong> {programa[3]}<br>
                                <strong>Inscripción:</strong> ${programa[5]:,.2f}<br>
                                <strong>Matrícula Base:</strong> ${programa[6]:,.2f}
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("Eliminar Programa", key=f"del_prog_{programa[0]}"):
                                if delete_program(programa[0]):
                                    st.success("Programa eliminado exitosamente")
                                    st.rerun()
        
        with tab2:
            st.header("Gestión de Asignaturas")
            programas = get_programs_by_period(selected_period)
            if not programas:
                st.warning(f"No hay programas disponibles para el periodo {selected_period[:4]}-{selected_period[4:]}")
            else:
                programa_seleccionado = st.selectbox(
                    "Seleccione un Programa",
                    options=[(p[0], p[1]) for p in programas],
                    format_func=lambda x: x[1]
                )
                
                if programa_seleccionado:
                    with st.form("nueva_asignatura_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombre de la Asignatura")
                            creditos = st.number_input("Créditos", min_value=1, max_value=10, step=1)
                            semestre = st.number_input("Semestre", min_value=1, max_value=20, step=1)
                        with col2:
                            codigo = st.text_input("Código de la Asignatura")
                            descripcion = st.text_area("Descripción", height=100)
                        
                        submit_button = st.form_submit_button("Agregar Asignatura")
                        
                        if submit_button and nombre and codigo:
                            if add_subject(programa_seleccionado[0], nombre, creditos, semestre, codigo, descripcion):
                                st.success("Asignatura agregada exitosamente")
                                st.rerun()

                    st.subheader("Asignaturas del Programa")
                    asignaturas = get_program_subjects(programa_seleccionado[0])
                    
                    if not asignaturas:
                        st.info("No hay asignaturas registradas para este programa")
                    else:
                        for asig in asignaturas:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"""
                                <div class="subject-box">
                                    <strong>Semestre {asig[3]}</strong><br>
                                    <strong>{asig[1]}</strong> ({asig[4]})<br>
                                    Créditos: {asig[2]}<br>
                                    {asig[5]}
                                </div>
                                """, unsafe_allow_html=True)
                            with col2:
                                if st.button("Eliminar", key=f"del_asig_{asig[0]}"):
                                    if delete_subject(asig[0]):
                                        st.success("Asignatura eliminada exitosamente")
                                        st.rerun()
        
        with tab3:
            st.header("Gestión de Requisitos")
            programas = get_programs_by_period(selected_period)
            if not programas:
                st.warning(f"No hay programas disponibles para el periodo {selected_period[:4]}-{selected_period[4:]}")
            else:
                programa_seleccionado = st.selectbox(
                    "Seleccione un Programa",
                    options=[(p[0], p[1]) for p in programas],
                    format_func=lambda x: x[1],
                    key="programa_requisitos"
                )
                
                if programa_seleccionado:
                    with st.form("nuevo_requisito_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            requisito = st.text_input("Nombre del Requisito")
                        with col2:
                            tipo_requisito = st.selectbox(
                                "Tipo de Requisito",
                                options=["Obligatorio", "Opcional"],
                                key="tipo_requisito"
                            )
                        submit_button = st.form_submit_button("Agregar Requisito")
                        
                        if submit_button and requisito:
                            if add_requirement(programa_seleccionado[0], requisito, tipo_requisito):
                                st.success("Requisito agregado exitosamente")
                                st.rerun()

                    st.subheader("Requisitos del Programa")
                    requisitos = get_program_requirements(programa_seleccionado[0])
                    
                    if not requisitos:
                        st.info("No hay requisitos registrados para este programa")
                    else:
                        for req in requisitos:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"""
                                <div class="requirement-box">
                                    <strong>{req[0]}</strong><br>
                                    <span style="color: {'#28a745' if req[1] == 'Obligatorio' else '#ffc107'}">
                                        {req[1]}
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                            with col2:
                                if st.button("Eliminar", key=f"del_req_{req[0]}"):
                                    if delete_requirement(programa_seleccionado[0], req[0]):
                                        st.success("Requisito eliminado exitosamente")
                                        st.rerun()

if __name__ == "__main__":
    main()