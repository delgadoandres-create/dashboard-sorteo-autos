import streamlit as st
from supabase import create_client, Client
import random
import time

# Configuración de página
st.set_page_config(page_title="Panel de Sorteos - CarShow", page_icon="🎟️", layout="wide")

# Conexión a Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("⚠️ Error conectando a Supabase. Verifica los Secrets.")
    st.stop()

st.title("🎟️ Sistema de Gestión y Sorteos")
st.markdown("---")

# -----------------------------------------------------------------------------
# CONSULTA GLOBAL DE DATOS
# -----------------------------------------------------------------------------
try:
    res_tickets = supabase.table("tickets").select("*").execute()
    all_tickets = res_tickets.data if res_tickets.data else []
except Exception as e:
    all_tickets = []

try:
    res_draws = supabase.table("draws").select("*").order("created_at", desc=True).execute()
    all_draws = res_draws.data if res_draws.data else []
except Exception as e:
    all_draws = []

# METRICAS
col1, col2, col3 = st.columns(3)
col1.metric("🎟️ Boletos Totales Emitidos", f"{len(all_tickets):,}")
col2.metric("🎯 Sorteos Creados", f"{len(all_draws)}")
ganadores_count = len([t for t in all_tickets if t.get('status') == 'WINNER'])
col3.metric("🏆 Ganadores Proclamados", f"{ganadores_count}")

st.markdown("---")

# -----------------------------------------------------------------------------
# PESTAÑAS DEL DASHBOARD
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["➕ Crear / Administrar Sorteos", "📋 Listado de Boletos", "🎲 Bolillero Digital"])

# -----------------------------------------------------------------------------
# TAB 1: CREAR Y ADMINISTRAR SORTEOS
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("➕ Registrar Nuevo Sorteo o Premio")
    
    with st.form("form_nuevo_sorteo", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            titulo = st.text_input("Título del Sorteo / Premio", placeholder="Ej: Gran Sorteo Toyota Hilux 2026")
            precio_ticket = st.number_input("Precio por Boleto (Gs.)", min_value=1000, value=10000, step=1000)
            
        with col_f2:
            total_tickets = st.number_input("Cantidad de Boletos Disponibles", min_value=100, value=1000000, step=1000)
            url_imagen = st.text_input("URL de la Imagen del Premio (Opcional)", placeholder="https://ejemplo.com/foto-auto.jpg")
            
        submitted = st.form_submit_button("🚀 Guardar y Activar Sorteo", type="primary")
        
        if submitted:
            if not titulo:
                st.error("Por favor, ingresá un título para el sorteo.")
            else:
                try:
                    nuevo_sorteo = {
                        "title": titulo,
                        "ticket_price": precio_precio if 'precio_precio' in locals() else precio_ticket,
                        "total_tickets": total_tickets,
                        "image_url": url_imagen if url_imagen else None,
                        "status": "ACTIVE"
                    }
                    supabase.table("draws").insert(nuevo_sorteo).execute()
                    st.success(f"🎉 ¡Sorteo '{titulo}' creado exitosamente!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar el sorteo en Supabase: {e}")

    st.markdown("---")
    st.subheader("📌 Catálogo de Sorteos Registrados")
    
    if all_draws:
        for draw in all_draws:
            with st.expander(f"🎯 Lote #{draw['id']} - {draw['title']} ({draw.get('status', 'ACTIVE')})", expanded=True):
                col_d1, col_d2 = st.columns([1, 2])
                with col_d1:
                    if draw.get('image_url'):
                        st.image(draw['image_url'], use_column_width=True)
                    else:
                        st.info("Sin imagen asignada")
                with col_d2:
                    st.write(f"💰 **Precio del Boleto:** Gs. {draw.get('ticket_price', 0):,}")
                    st.write(f"🎟️ **Boletos Disponibles:** {draw.get('total_tickets', 0):,}")
                    st.write(f"📅 **Fecha de Creación:** {draw.get('created_at', 'N/A')}")
                    if draw.get('status') == 'COMPLETED':
                        st.success(f"🏆 Ticket Ganador ID: {draw.get('winning_ticket_id')}")
    else:
        st.info("No hay sorteos registrados todavía. ¡Creá el primero arriba!")

# -----------------------------------------------------------------------------
# TAB 2: VER BOLETOS
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Boletos Registrados en el Sistema")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
        
    if all_tickets:
        st.dataframe(all_tickets, use_container_width=True)
    else:
        st.info("No hay boletos cargados.")

# -----------------------------------------------------------------------------
# TAB 3: BOLILLERO DIGITAL
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🎲 Ejecución del Sorteo")
    
    # Filtrar solo sorteos activos
    draws_activos = [d for d in all_draws if d.get('status') != 'COMPLETED']
    
    if not draws_activos:
        st.warning("No hay sorteos activos para ejecutar.")
    else:
        opciones_sorteo = {f"Lote #{d['id']} - {d['title']}": d['id'] for d in draws_activos}
        lote_label = st.selectbox("Seleccionar el Sorteo a Ejecutar:", list(opciones_sorteo.keys()))
        lote_id = opciones_sorteo[lote_label]
        
        # Boletos elegibles para este lote
        boletos_elegibles = [t for t in all_tickets if t.get('draw_id') == lote_id and t.get('status') in ['PAID', 'WINNER']]
        
        st.info(f"📊 Boletos pagados participantes en este sorteo: **{len(boletos_elegibles)}**")
        
        if len(boletos_elegibles) == 0:
            st.warning("Este sorteo aún no tiene boletos válidos o pagados asignados.")
        else:
            if st.button("🚀 EJECUTAR SORTEO Y PROCLAMAR GANADOR", type="primary"):
                placeholder = st.empty()
                
                with st.spinner("Girando bolillero digital..."):
                    for _ in range(30):
                        temp = random.choice(boletos_elegibles)
                        placeholder.header(f"🎰 BOLETO EN JUEGO: **{temp.get('ticket_number')}**")
                        time.sleep(0.1)
                
                ganador = random.choice(boletos_elegibles)
                placeholder.empty()
                
                ticket_id = ganador.get('id')
                num_ticket = ganador.get('ticket_number')
                
                # Actualizar Supabase
                try:
                    supabase.table("tickets").update({"status": "WINNER"}).eq("id", ticket_id).execute()
                    supabase.table("draws").update({"winning_ticket_id": ticket_id, "status": "COMPLETED"}).eq("id", lote_id).execute()
                except Exception as e:
                    st.warning(f"Nota sobre actualización: {e}")

                st.balloons()
                st.markdown(f"# 🎉 ¡GANADOR PROCLAMADO!")
                st.metric("🎟️ Boleto Ganador", f"{num_ticket}")
                st.metric("📱 WhatsApp", f"{ganador.get('whatsapp')}")
                st.json(ganador)
