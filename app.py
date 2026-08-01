import streamlit as st
from supabase import create_client, Client
import random
import time

# Configuración de página
st.set_page_config(page_title="Panel de Sorteos Triples", page_icon="🎟️", layout="wide")

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

st.title("🎟️ Sistema de Gestión - Sorteos con Múltiples Premios")
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
col1.metric("🎟️ Boletos Registrados", f"{len(all_tickets):,}")
col2.metric("🎯 Sorteos Creados", f"{len(all_draws)}")
ganadores_count = len([t for t in all_tickets if t.get('status') == 'WINNER'])
col3.metric("🏆 Total Ganadores Proclamados", f"{ganadores_count}")

st.markdown("---")

# -----------------------------------------------------------------------------
# PESTAÑAS DEL DASHBOARD
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["➕ Crear Sorteo Triple", "📋 Listado de Boletos", "🎲 Bolillero Digital (3 Premios)"])

# -----------------------------------------------------------------------------
# TAB 1: CREAR SORTEO MULTI-PREMIO
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("➕ Registrar Nuevo Sorteo con 3 Premios")
    
    with st.form("form_nuevo_sorteo", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            titulo = st.text_input("Título del Sorteo", placeholder="Ej: Gran Sorteo Triple 2026")
            precio_ticket = st.number_input("Precio por Boleto (Gs.)", min_value=1000, value=10000, step=1000)
            url_imagen = st.text_input("URL de la Imagen de WhatsApp (Supabase Storage)", placeholder="https://.../afiche-triple.jpg")
            
        with col_f2:
            prize_1 = st.text_input("🥇 1er Premio", value="Toyota Hilux 0km")
            prize_2 = st.text_input("🥈 2do Premio", value="Moto Kenton GTR 150")
            prize_3 = st.text_input("🥉 3er Premio", value="Smart TV 65 pulgadas")
            
        submitted = st.form_submit_button("🚀 Guardar y Activar Sorteo", type="primary")
        
        if submitted:
            if not titulo:
                st.error("Por favor, ingresá un título para el sorteo.")
            else:
                try:
                    nuevo_sorteo = {
                        "title": titulo,
                        "ticket_price": precio_ticket,
                        "image_url": url_imagen if url_imagen else None,
                        "prize_1": prize_1,
                        "prize_2": prize_2,
                        "prize_3": prize_3,
                        "status": "ACTIVE"
                    }
                    supabase.table("draws").insert(nuevo_sorteo).execute()
                    st.success(f"🎉 ¡Sorteo '{titulo}' registrado con éxito!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar en Supabase: {e}")

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
                    st.write(f"🥇 **1er Premio:** {draw.get('prize_1', 'N/A')}")
                    st.write(f"🥈 **2do Premio:** {draw.get('prize_2', 'N/A')}")
                    st.write(f"🥉 **3er Premio:** {draw.get('prize_3', 'N/A')}")
                    if draw.get('status') == 'COMPLETED':
                        st.success(f"🏆 Ganadores asignados registrados en la base de datos.")
    else:
        st.info("No hay sorteos registrados.")

# -----------------------------------------------------------------------------
# TAB 2: LISTADO DE BOLETOS
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
# TAB 3: BOLILLERO DIGITAL MULTI-PREMIO
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("🎲 Ejecución del Sorteo Triple")
    
    draws_activos = [d for d in all_draws if d.get('status') != 'COMPLETED']
    
    if not draws_activos:
        st.warning("No hay sorteos activos para ejecutar.")
    else:
        opciones_sorteo = {f"Lote #{d['id']} - {d['title']}": d for d in draws_activos}
        lote_label = st.selectbox("Seleccionar el Sorteo a Sortear:", list(opciones_sorteo.keys()))
        sorteo_obj = opciones_sorteo[lote_label]
        lote_id = sorteo_obj['id']
        
        # Boletos elegibles
        boletos_elegibles = [t for t in all_tickets if t.get('draw_id') == lote_id and t.get('status') in ['PAID', 'WINNER']]
        
        st.info(f"📊 Boletos pagados participantes en este lote: **{len(boletos_elegibles)}**")
        
        if len(boletos_elegibles) < 3:
            st.warning("Se requieren al menos 3 boletos elegibles para realizar el sorteo triple.")
        else:
            if st.button("🚀 EJECUTAR SORTEO TRIPLE (3 GANADORES)", type="primary"):
                # Muestreo sin reemplazo (3 ganadores distintos)
                ganadores = random.sample(boletos_elegibles, 3)
                
                placeholder = st.empty()
                with st.spinner("GIRANDO BOLILLERO DIGITAL..."):
                    for _ in range(30):
                        temp = random.choice(boletos_elegibles)
                        placeholder.header(f"🎰 NÚMERO EN JUEGO: **{temp.get('ticket_number')}**")
                        time.sleep(0.1)
                
                placeholder.empty()
                
                g1, g2, g3 = ganadores[0], ganadores[1], ganadores[2]
                
                # Actualizar Supabase
                try:
                    # Actualizar boletos a WINNER
                    for g in [g1, g2, g3]:
                        supabase.table("tickets").update({"status": "WINNER"}).eq("id", g['id']).execute()
                    
                    # Actualizar sorteo como COMPLETED con los 3 IDs de ganadores
                    supabase.table("draws").update({
                        "winner_1_ticket_id": g1['id'],
                        "winner_2_ticket_id": g2['id'],
                        "winner_3_ticket_id": g3['id'],
                        "status": "COMPLETED"
                    }).eq("id", lote_id).execute()
                    
                except Exception as e:
                    st.warning(f"Nota sobre actualización de base de datos: {e}")

                st.balloons()
                st.markdown("# 🎉 ¡GANADORES DEL SORTEO TRIPLE!")
                
                col_g1, col_g2, col_g3 = st.columns(3)
                
                with col_g1:
                    st.success(f"🥇 **1er Premio:** {sorteo_obj.get('prize_1')}")
                    st.markdown(f"### Ticket: `{g1.get('ticket_number')}`")
                    st.write(f"📱 WhatsApp: `{g1.get('whatsapp')}`")
                    
                with col_g2:
                    st.info(f"🥈 **2do Premio:** {sorteo_obj.get('prize_2')}")
                    st.markdown(f"### Ticket: `{g2.get('ticket_number')}`")
                    st.write(f"📱 WhatsApp: `{g2.get('whatsapp')}`")
                    
                with col_g3:
                    st.warning(f"🥉 **3er Premio:** {sorteo_obj.get('prize_3')}")
                    st.markdown(f"### Ticket: `{g3.get('ticket_number')}`")
                    st.write(f"📱 WhatsApp: `{g3.get('whatsapp')}`")
