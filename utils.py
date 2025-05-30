import psycopg2
import streamlit as st

def get_connection():
    return psycopg2.connect(host='dpg-d0kvhcbuibrs739t0bb0-a.oregon-postgres.render.com',
                            database="cdd_db",
                            user="cdd_user",
                            password="gXmnbB3JuFU3IpHYiwiZUdxbwxgHZY26", port='5432',
                            options="-c search_path=uninorte_db")

def login_user(user_id, password):
    conn = get_connection()
    cur = conn.cursor()
    
    # Establecer el esquema correcto
    cur.execute("SET search_path TO uninorte_db")
    
    cur.execute(
        """
        SELECT id, tipo_usuario 
        FROM usuario 
        WHERE id = %s AND contraseña = %s
        """,
        (user_id, password)
    )

    result = cur.fetchone()
    
    if result:
        session_data = (str(result[0]).strip(), str(result[1]).strip())
    else:
        session_data = None
    
    cur.close()
    conn.close()
    return session_data

def register_user(user_id, email, password, user_type):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO "uninorte_db"."usuario" (id, email, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s)',
            (user_id, email, password, user_type)
        )
        conn.commit()
        st.success("Usuario registrado exitosamente.")
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        st.error("Ese ID o correo ya está registrado.")
    except Exception as e:
        conn.rollback()
        st.error(f"Error: {e}")
    finally:
        cur.close()
        conn.close() 