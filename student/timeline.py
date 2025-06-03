import streamlit as st
import psycopg2
from utils import get_connection
import datetime

def show_timeline():
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

        /* Estilo general y tipografía */
        @import url('https://fonts.googleapis.com/css2?family=Circular:wght@400;500;700&display=swap');
        
        .timeline-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, Helvetica Neue, sans-serif;
            background-color: var(--background-color);
        }
        
        .timeline-header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        }
        
        .timeline-header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: var(--text-color);
            font-weight: 700;
        }
        
        .timeline-item {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            border-left: 4px solid var(--primary-color);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            width: 100%;
            box-sizing: border-box;
        }
        
        .timeline-item:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        
        .timeline-date {
            color: var(--text-color);
            font-size: 1.1em;
            margin-bottom: 20px;
            font-weight: 500;
            opacity: 0.8;
        }
        
        .timeline-content {
            margin-top: 20px;
        }
        
        .timeline-content h3 {
            color: var(--text-color);
            margin-bottom: 20px;
            font-size: 1.5em;
            font-weight: 600;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
            margin: 5px;
            transition: all 0.2s ease;
        }
        
        .status-pending {
            background-color: var(--warning-color);
            color: white;
        }
        
        .status-approved {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .status-rejected {
            background-color: var(--primary-color);
            color: white;
        }
        
        .document-list {
            margin: 25px 0;
            padding: 25px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            width: 100%;
            box-sizing: border-box;
        }
        
        .document-item {
            margin: 15px 0;
            padding: 15px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.2s ease;
        }
        
        .document-item:hover {
            background-color: var(--background-color);
        }
        
        .document-item:last-child {
            border-bottom: none;
        }
        
        .homologation-section {
            margin-top: 30px;
            padding: 25px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            width: 100%;
            box-sizing: border-box;
        }
        
        .section-title {
            font-size: 1.3em;
            color: var(--text-color);
            margin-bottom: 25px;
            font-weight: 600;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--primary-color);
        }
        
        .no-requests {
            text-align: center;
            padding: 50px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
            margin-top: 30px;
        }
        
        .no-requests h3 {
            color: var(--text-color);
            font-size: 1.5em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .no-requests p {
            color: var(--text-color);
            opacity: 0.8;
            font-size: 1.1em;
        }
        
        .status-container {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 15px 0;
        }
        
        .homologation-item {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }
        
        .homologation-item:hover {
            transform: translateY(-2px);
        }
        
        .homologation-details {
            margin-top: 10px;
            font-size: 1em;
            color: var(--text-color);
            opacity: 0.8;
        }

        /* Fix container display issues */
        .stApp {
            background-color: var(--background-color);
        }

        .element-container {
            width: 100% !important;
            max-width: none !important;
            padding-right: 0 !important;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .timeline-item {
                padding: 20px;
            }
            
            .document-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            
            .status-container {
                justify-content: flex-start;
            }

            .timeline-header {
                padding: 20px;
            }

            .timeline-header h1 {
                font-size: 2em;
            }
        }

        .document-group {
            margin: 20px 0;
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        .document-group h4 {
            color: var(--text-color);
            margin-bottom: 15px;
            font-size: 1.1em;
            font-weight: 600;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }

        .document-info {
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
        }

        .document-name {
            font-weight: 500;
            color: var(--text-color);
        }

        .document-required {
            color: var(--primary-color);
            font-size: 0.8em;
            font-weight: 500;
            padding: 4px 8px;
            border-radius: 12px;
            background-color: rgba(255,90,95,0.1);
        }

        .document-optional {
            color: var(--text-color);
            font-size: 0.8em;
            font-weight: 500;
            opacity: 0.7;
            padding: 4px 8px;
            border-radius: 12px;
            background-color: rgba(72,72,72,0.1);
        }

        .document-status {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .document-icon {
            font-size: 1.2em;
            color: var(--text-color);
            opacity: 0.7;
        }

        .document-item {
            margin: 12px 0;
            padding: 15px;
            border-radius: 12px;
            background: var(--background-color);
            transition: all 0.2s ease;
        }

        .document-item:hover {
            transform: translateX(4px);
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)
    st.markdown('<div class="timeline-header"><h1>Estado de solicitudes</h1></div>', unsafe_allow_html=True)

    # Get user_id from session state
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.markdown("""
            <div class="no-requests">
                <h3>Acceso no autorizado</h3>
                <p>Por favor inicie sesión para ver su línea de tiempo.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET search_path TO uninorte_db;")

    try:
        # Get user's documento from their id
        cursor.execute("SELECT documento FROM datos WHERE id = %s", (user_id,))
        user_documento = cursor.fetchone()
        
        if not user_documento:
            st.markdown("""
                <div class="no-requests">
                    <h3>Información no encontrada</h3>
                    <p>No se encontró información del usuario en el sistema.</p>
                </div>
            """, unsafe_allow_html=True)
            return
            
        # Get all requests for the student
        cursor.execute("""
            SELECT 
                f.id_solicitud,
                f.documento,
                f.tipo_estudiante,
                f.id_programa,
                p.programa as nombre_programa,
                pg.estado as estado_pago,
                pg.fecha as fecha_pago,
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
                END as estado_docs
            FROM formulario f
            LEFT JOIN oferta p ON f.id_programa = p.id_programa
            LEFT JOIN pagos pg ON f.id_solicitud = pg.id_solicitud
            WHERE f.documento = %s
            ORDER BY f.id_solicitud DESC
        """, (user_documento[0],))
        
        solicitudes = cursor.fetchall()

        if not solicitudes:
            st.markdown("""
                <div class="no-requests">
                    <h3>No se encontraron solicitudes</h3>
                    <p>Aún no has realizado ninguna solicitud en el sistema.</p>
                </div>
            """, unsafe_allow_html=True)
            return

        for solicitud in solicitudes:
            id_solicitud, documento, tipo_estudiante, id_programa, nombre_programa, estado_pago, fecha_solicitud, estado_docs = solicitud
            
            doc_status_class = {
                'Pendiente': 'status-pending',
                'Aprobado': 'status-approved',
                'Sin documentos': 'status-rejected'
            }.get(estado_docs, 'status-pending')

            pago_status_class = {
                'pagado': 'status-approved',
                'pendiente': 'status-pending',
                None: 'status-rejected'
            }.get(estado_pago, 'status-rejected')

            st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-date">
                        Solicitud #{id_solicitud} - {fecha_solicitud.strftime('%d/%m/%Y') if fecha_solicitud else 'Fecha no disponible'}
                    </div>
                    <div class="timeline-content">
                        <h3>{tipo_estudiante}</h3>
                        <p><strong>Programa:</strong> {nombre_programa}</p>
                        <div class="status-container">
                            <span class="status-badge {doc_status_class}">
                                Documentos: {estado_docs}
                            </span>
                            <span class="status-badge {pago_status_class}">
                                Pago: {estado_pago.capitalize() if estado_pago else 'No registrado'}
                            </span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Documentos
            cursor.execute("""
                SELECT 
                    a.nombre_doc,
                    a.aprobacion,
                    a.archivo,
                    r.tipo_req
                FROM anexos a
                LEFT JOIN requisitos r ON r.nombre_doc = a.nombre_doc 
                    AND r.id_programa = %s
                WHERE a.id_solicitud = %s
                ORDER BY r.tipo_req DESC, a.nombre_doc
            """, (id_programa, id_solicitud))
            documentos = cursor.fetchall()

            if documentos:
                st.markdown('<div class="section-title">Documentos Presentados</div>', unsafe_allow_html=True)

                estado_general = 'Pendiente'
                if all(doc[1] == 'Aprobado' for doc in documentos if doc[1]):
                    estado_general = 'Aprobado'
                elif any(doc[1] == 'Rechazado' for doc in documentos if doc[1]):
                    estado_general = 'Rechazado'

                estado_class = {
                    'Pendiente': 'status-pending',
                    'Aprobado': 'status-approved',
                    'Rechazado': 'status-rejected'
                }[estado_general]

                obligatorios = []
                opcionales = []
                otros = []
                
                for doc in documentos:
                    nombre_doc, estado_doc, archivo, tipo_req = doc
                    if tipo_req == 'Obligatorio':
                        obligatorios.append(doc)
                    elif tipo_req == 'Opcional':
                        opcionales.append(doc)
                    else:
                        otros.append(doc)

                if obligatorios:
                    st.markdown('<div class="document-group"><h4>Documentos Obligatorios</h4>', unsafe_allow_html=True)
                    for doc in obligatorios:
                        nombre_doc, estado_doc, archivo, _ = doc
                        doc_estado_class = {
                            'Aprobado': 'status-approved',
                            'Rechazado': 'status-rejected',
                            'Pendiente': 'status-pending'
                        }.get(estado_doc if estado_doc else 'Pendiente', 'status-pending')
                        
                        estado_doc = estado_doc if estado_doc else 'Pendiente'
                        
                        st.markdown(f"""
                            <div class="document-item">
                                <div class="document-info">
                                    <span class="document-name">{nombre_doc}</span>
                                    <span class="document-required">Obligatorio</span>
                                </div>
                                <div class="document-status">
                                    <span class="status-badge {doc_estado_class}">{estado_doc}</span>
                                    {f'<span class="document-icon">📎</span>' if archivo else ''}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if opcionales:
                    st.markdown('<div class="document-group"><h4>Documentos Opcionales</h4>', unsafe_allow_html=True)
                    for doc in opcionales:
                        nombre_doc, estado_doc, archivo, _ = doc
                        doc_estado_class = {
                            'Aprobado': 'status-approved',
                            'Rechazado': 'status-rejected',
                            'Pendiente': 'status-pending'
                        }.get(estado_doc if estado_doc else 'Pendiente', 'status-pending')
                        
                        estado_doc = estado_doc if estado_doc else 'Pendiente'
                        
                        st.markdown(f"""
                            <div class="document-item">
                                <div class="document-info">
                                    <span class="document-name">{nombre_doc}</span>
                                    <span class="document-optional">Opcional</span>
                                </div>
                                <div class="document-status">
                                    <span class="status-badge {doc_estado_class}">{estado_doc}</span>
                                    {f'<span class="document-icon">📎</span>' if archivo else ''}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                if otros:
                    st.markdown('<div class="document-group"><h4>Otros Documentos</h4>', unsafe_allow_html=True)
                    for doc in otros:
                        nombre_doc, estado_doc, archivo, _ = doc
                        doc_estado_class = {
                            'Aprobado': 'status-approved',
                            'Rechazado': 'status-rejected',
                            'Pendiente': 'status-pending'
                        }.get(estado_doc if estado_doc else 'Pendiente', 'status-pending')
                        
                        estado_doc = estado_doc if estado_doc else 'Pendiente'
                        
                        st.markdown(f"""
                            <div class="document-item">
                                <div class="document-info">
                                    <span class="document-name">{nombre_doc}</span>
                                </div>
                                <div class="document-status">
                                    <span class="status-badge {doc_estado_class}">{estado_doc}</span>
                                    {f'<span class="document-icon">📎</span>' if archivo else ''}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            if tipo_estudiante == 'Transferencia Externa':
                cursor.execute("""
                    SELECT 
                        h.estado,
                        h.decision,
                        a.nombre as materia_destino,
                        a.creditos,
                        a.semestre
                    FROM homologar h
                    JOIN asignaturas a ON h.id_asignatura = a.id_asignatura
                    WHERE h.id_solicitud = %s
                """, (id_solicitud,))
                homologaciones = cursor.fetchall()

                if homologaciones:
                    st.markdown('<div class="section-title">Estado de homologaciones</div>', unsafe_allow_html=True)
                    
                    for hom in homologaciones:
                        estado_hom, decision, materia_destino, creditos, semestre = hom
                        hom_estado_class = {
                            'Aprobada': 'status-approved',
                            'Rechazada': 'status-rejected',
                            'Pendiente': 'status-pending'
                        }.get(estado_hom, 'status-pending')
                        
                        st.markdown(f"""
                            <div class="homologation-item">
                                <strong>{materia_destino}</strong>
                                <div class="homologation-details">
                                    {creditos} créditos - Semestre {semestre}
                                </div>
                                <div class="status-container">
                                    <span class="status-badge {hom_estado_class}">
                                        {estado_hom if estado_hom else 'Pendiente'}
                                    </span>
                                    <small>Decisión: {decision if decision and decision != 'Por definir' else 'Pendiente'}</small>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
            <div class="no-requests">
                <h3>Error en el sistema</h3>
                <p>Ocurrió un error al cargar las solicitudes: {str(e)}</p>
            </div>
        """, unsafe_allow_html=True)

    finally:
        cursor.close()
        conn.close()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    show_timeline() 