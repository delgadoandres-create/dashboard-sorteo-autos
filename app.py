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

st.title("🎟️ Sistema de Gestión y Sorteos por Lote")
st.markdown("---")

# -----------------------------------------------------------------------------
# CONSULTA DE DATOS Y FILTRO DE LOTES
# -----------------------------------------------------------------------------
try:
    # Solo traemos los boletos que estén pagados (PAID)
    res_tickets = supabase.table("tickets").select("*").eq("status", "PAID").execute()
    all_tickets = res_tickets.data if res_tickets.data else []
except Exception as e:
    st.error(f"Error consultando la base de datos: {e}")
    all_tickets = []

# Obtener los IDs de lotes (draw_id) presentes en los boletos pagados
lotes_disponibles = sorted(list(set([t['draw_id'] for t in all_tickets if 'draw_id' in t and t['draw_id'] is not None])))

# METRICAS PRINCIPALES
col1, col2 = st.columns(2)
col1.metric("🎟️ Boletos Pagados Totales", f"{len(all_tickets):,}")
col2.metric("🎯 Lotes con Boletos Pagados", f"{len(lotes_disponibles)}")

st.markdown("---")

# -----------------------------------------------------------------------------
# PESTAÑAS OPERATIVAS
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📋 Boletos Registrados (PAID)", "🎲 Executar Sorteo de Lote"])

with tab1:
    st.subheader("Boletos Validados (Pago Confirmado)")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
        
    if all_tickets:
        st.dataframe(all_tickets, use_container_width=True)
    else:
        st.info("No hay boletos pagados en la base de datos.")

with tab2:
    st.subheader("🎲 Sorteo Oficial por Lote (Draw)")
    
    if not lotes_disponibles:
        st.warning("No hay lotes con boletos pagados para sortear.")
    else:
        # Selector de lote
        lote_seleccionado = st.selectbox("Seleccionar el Lote / Draw_ID a sortear:", lotes_disponibles)
        
        # Filtrar boletos pertenecientes al lote seleccionado
        boletos_lote = [t for t in all_tickets if t.get('draw_id') == lote_seleccionado]
        
        st.info(f"📊 Boletos participantes en el **Lote #{lote_seleccionado}**: **{len(boletos_lote)}**")
        
        if len(boletos_lote) == 0:
            st.warning("Este lote no tiene boletos válidos para sortear.")
        else:
            if st.button("🚀 EJECUTAR SORTEO DE LOTE", type="primary"):
                placeholder = st.empty()
                
                # Animación de sorteo
                with st.spinner("Girando bolillero digital..."):
                    for _ in range(30):
                        temp = random.choice(boletos_lote)
                        placeholder.header(f"🎰 BOLETO EN JUEGO: **{temp.get('ticket_number')}**")
                        time.sleep(0.1)
                
                # Seleccionar Ganador
                ganador = random.choice(boletos_lote)
                placeholder.empty()
                
                st.balloons()
                st.success(f"🎉 ¡TENEMOS UN BOLETO GANADOR PARA EL LOTE #{lote_seleccionado}!")
                
                # Mostrar resultado destacado
                st.markdown(f"### 🏆 Boleto Ganador: `{ganador.get('ticket_number')}`")
                st.markdown(f"📱 **WhatsApp:** `{ganador.get('whatsapp')}`")
                st.markdown(f"🆔 **ID de Boleto:** `{ganador.get('id')}`")
                
                st.markdown("---")
                st.subheader("Detalles del Registro Ganador:")
                st.json(ganador)
