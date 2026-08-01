import streamlit as st
from supabase import create_client, Client
import random
import time

# Configuración de página
st.set_page_config(page_title="Panel de Control - Sorteos por Lote", page_icon="🎟️", layout="wide")

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

st.title("🎟️ Gestión y Ejecución de Sorteos por Lote")
st.markdown("---")

# -----------------------------------------------------------------------------
# CONSULTA DE DATOS Y FILTRO DE LOTES
# -----------------------------------------------------------------------------
try:
    # Traer todos los boletos
    res_tickets = supabase.table("tickets").select("*").execute()
    all_tickets = res_tickets.data if res_tickets.data else []
except Exception as e:
    st.error(f"Error consultando la base de datos: {e}")
    all_tickets = []

# Identificar lotes disponibles si existe columna 'draw_id' o 'status'
# Si no existe la columna 'status', asumiremos 'active' para todos
lotes_disponibles = list(set([t.get('draw_id', 'Lote Único') for t in all_tickets if t.get('status', 'active') != 'closed']))
lotes_cerrados = list(set([t.get('draw_id', 'Lote Único') for t in all_tickets if t.get('status') == 'closed']))

# METRICAS PRINCIPALES
col1, col2, col3 = st.columns(3)
col1.metric("🎟️ Total Boletos Registrados", f"{len(all_tickets):,}")
col2.metric("🟢 Lotes Activos", f"{len(lotes_disponibles)}")
col3.metric("🔴 Lotes Cerrados", f"{len(lotes_cerrados)}")

st.markdown("---")

# -----------------------------------------------------------------------------
# PESTAÑAS OPERATIVAS
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📋 Todos los Boletos", "🎲 Ejecutar y Cerrar Sorteo"])

with tab1:
    st.subheader("Registros Globales")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
        
    if all_tickets:
        st.dataframe(all_tickets, use_container_width=True)
    else:
        st.info("No hay registros en la base de datos.")

with tab2:
    st.subheader("🎲 Sorteo Oficial de Lote / Draw")
    
    if not lotes_disponibles:
        st.success("✅ No hay lotes pendientes por sortear. Todos los lotes actuales están cerrados.")
    else:
        # Selector de lote a sortear
        lote_seleccionado = st.selectbox("Seleccionar el Lote / Draw a sortear:", lotes_disponibles)
        
        # Filtrar boletos pertenecientes al lote seleccionado y que estén 'active'
        boletos_lote = [
            t for t in all_tickets 
            if t.get('draw_id', 'Lote Único') == lote_seleccionado and t.get('status', 'active') != 'closed'
        ]
        
        st.info(f"📊 Boletos elegibles en **{lote_seleccionado}**: **{len(boletos_lote)}**")
        
        if len(boletos_lote) == 0:
            st.warning("Este lote no tiene boletos activos elegibles.")
        else:
            st.warning("⚠️ **Atención:** Al ejecutar el sorteo, se proclamará el ganador y este lote quedará **CERRADO** automáticamente.")
            
            if st.button("🚀 EJECUTAR Y CERRAR SORTEO", type="primary"):
                placeholder = st.empty()
                
                # Animación de sorteo
                with st.spinner("Girando bolillero digital..."):
                    for _ in range(30):
                        temp = random.choice(boletos_lote)
                        valor_mostrar = temp.get('ticket_number') or temp.get('number') or temp.get('id')
                        placeholder.header(f"🎰 NÚMERO EN JUEGO: **{valor_mostrar}**")
                        time.sleep(0.1)
                
                # Seleccionar Ganador
                ganador = random.choice(boletos_lote)
                placeholder.empty()
                
                # Proceso de Cierre de Lote en Supabase
                try:
                    # Marcar boletos del lote como 'closed'
                    # Si existe 'draw_id', actualizamos por 'draw_id', si no, actualizamos los IDs seleccionados
                    if 'draw_id' in ganador:
                        supabase.table("tickets").update({"status": "closed"}).eq("draw_id", lote_seleccionado).execute()
                    else:
                        # Si no hay columna draw_id, marcamos status='closed' globalmente
                        supabase.table("tickets").update({"status": "closed"}).execute()
                    
                    st.balloons()
                    st.success(f"🎉 ¡SORTEO FINALIZADO! El lote **{lote_seleccionado}** ha sido oficialmente CERRADO.")
                    
                    st.markdown("### 🏆 DATOS DEL GANADOR PROCLAMADO")
                    st.json(ganador)
                    
                except Exception as e:
                    st.error(f"El ganador fue seleccionado ({ganador}), pero hubo un error al cerrar el lote en Supabase: {e}")
