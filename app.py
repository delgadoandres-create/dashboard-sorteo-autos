import streamlit as st
from supabase import create_client, Client
import random
import time

# Configuración de página
st.set_page_config(page_title="Panel de Control - Sorteo", page_icon="🎟️", layout="wide")

# Conexión a Supabase mediante Secrets
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

st.title("🎟️ Panel de Control - Sistema de Sorteos")
st.markdown("---")

# METRICAS
col1, col2 = st.columns(2)

try:
    # Traer todos los boletos
    res_tickets = supabase.table("tickets").select("*").execute()
    data_tickets = res_tickets.data if res_tickets.data else []
    
    total_tickets = len(data_tickets)
    col1.metric("🎟️ Total Boletos Registrados", f"{total_tickets:,}")
    col2.metric("🟢 Estado del Sistema", "Conectado y Listo")

except Exception as e:
    st.error(f"Error consultando la base de datos: {e}")
    data_tickets = []

st.markdown("---")

# PESTAÑAS OPERATIVAS
tab1, tab2 = st.tabs(["📋 Lista de Boletos", "🎲 Bolillero Digital"])

with tab1:
    st.subheader("Boletos Registrados")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
        
    if data_tickets:
        st.dataframe(data_tickets, use_container_width=True)
    else:
        st.info("No hay registros en la tabla de boletos.")

with tab2:
    st.subheader("🎲 Selección Aleatoria del Ganador")
    st.write("El sistema seleccionará de forma aleatoria e irrefutable un boleto directamente desde la base de datos.")
    
    if st.button("🚀 EJECUTAR SORTEO", type="primary"):
        if not data_tickets:
            st.warning("No hay boletos en la base de datos para realizar el sorteo.")
        else:
            placeholder = st.empty()
            
            # Animación de sorteo
            with st.spinner("Girando bolillero digital..."):
                for _ in range(25):
                    temp = random.choice(data_tickets)
                    # Muestra un valor representativo del registro
                    valor_mostrar = temp.get('ticket_number') or temp.get('number') or temp.get('id')
                    placeholder.header(f"🎰 NÚMERO / ID: **{valor_mostrar}**")
                    time.sleep(0.1)
            
            # Elección del ganador definitivo
            ganador = random.choice(data_tickets)
            placeholder.empty()
            
            st.balloons()
            st.success("🎉 ¡TENEMOS UN GANADOR!")
            st.json(ganador) # Muestra los datos completos del registro ganador
