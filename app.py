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
# CONSULTA DE DATOS
# -----------------------------------------------------------------------------
try:
    # Traer todos los boletos válidos o pagados
    res_tickets = supabase.table("tickets").select("*").execute()
    all_tickets = res_tickets.data if res_tickets.data else []
except Exception as e:
    st.error(f"Error consultando los boletos: {e}")
    all_tickets = []

# Filtrar boletos pagados
boletos_pagados = [t for t in all_tickets if t.get('status') in ['PAID', 'WINNER']]

# Obtener IDs de lotes con boletos participantes
lotes_disponibles = sorted(list(set([t['draw_id'] for t in boletos_pagados if 'draw_id' in t and t['draw_id'] is not None])))

# METRICAS
col1, col2, col3 = st.columns(3)
col1.metric("🎟️ Boletos Pagados Totales", f"{len(boletos_pagados):,}")
col2.metric("🎯 Lotes Registrados", f"{len(lotes_disponibles)}")

ganadores_actuales = [t for t in all_tickets if t.get('status') == 'WINNER']
col3.metric("🏆 Boletos Ganadores Registrados", f"{len(ganadores_actuales)}")

st.markdown("---")

# -----------------------------------------------------------------------------
# PESTAÑAS OPERATIVAS
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📋 Registros de Boletos", "🎲 Ejecutar y Registrar Sorteo"])

with tab1:
    st.subheader("Boletos Registrados en el Sistema")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
        
    if all_tickets:
        st.dataframe(all_tickets, use_container_width=True)
    else:
        st.info("No hay boletos en la base de datos.")

with tab2:
    st.subheader("🎲 Sorteo Oficial por Lote / Draw")
    
    if not lotes_disponibles:
        st.warning("No hay lotes con boletos válidos para sortear.")
    else:
        lote_seleccionado = st.selectbox("Seleccionar el Lote / Draw_ID a sortear:", lotes_disponibles)
        
        # Filtrar boletos de este lote que hayan sido pagados
        boletos_lote = [t for t in boletos_pagados if t.get('draw_id') == lote_seleccionado]
        
        st.info(f"📊 Boletos elegibles en el **Lote #{lote_seleccionado}**: **{len(boletos_lote)}**")
        
        if len(boletos_lote) == 0:
            st.warning("Este lote no tiene boletos válidos para sortear.")
        else:
            if st.button("🚀 EJECUTAR SORTEO Y GUARDAR GANADOR", type="primary"):
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
                
                # -------------------------------------------------------------
                # REGISTRO DEL GANADOR EN SUPABASE
                # -------------------------------------------------------------
                ticket_id = ganador.get('id')
                num_ticket = ganador.get('ticket_number')
                
                # 1. Intentar actualizar el boleto como 'WINNER'
                try:
                    supabase.table("tickets").update({"status": "WINNER"}).eq("id", ticket_id).execute()
                    st.success(f"✅ Boleto #{num_ticket} (ID: {ticket_id}) actualizado correctamente como WINNER.")
                except Exception as e:
                    st.warning(f"No se pudo cambiar el status del boleto a 'WINNER' ({e}). Se mantiene el registro sin alterar status.")

                # 2. Intentar actualizar la tabla de lotes 'draws' con el ticket ganador
                try:
                    supabase.table("draws").update({
                        "winning_ticket_id": ticket_id,
                        "status": "COMPLETED"
                    }).eq("id", lote_seleccionado).execute()
                    st.success(f"✅ Lote #{lote_seleccionado} actualizado en la tabla 'draws' con el ganador #{num_ticket}.")
                except Exception as e:
                    # En caso de que la tabla 'draws' no exista o varíe el nombre de la columna
                    st.info(f"Nota sobre la tabla de lotes: {e}")

                # -------------------------------------------------------------
                # PRESENTACIÓN DE RESULTADOS
                # -------------------------------------------------------------
                st.balloons()
                st.markdown(f"# 🎉 ¡GANADOR PROCLAMADO EN EL LOTE #{lote_seleccionado}!")
                
                col_g1, col_g2 = st.columns(2)
                col_g1.metric("🎟️ Número de Boleto Ganador", f"{num_ticket}")
                col_g2.metric("📱 WhatsApp del Ganador", f"{ganador.get('whatsapp')}")
                
                st.markdown("---")
                st.subheader("Registro Completo del Ganador:")
                st.json(ganador)
