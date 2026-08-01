import streamlit as st
from supabase import create_client, Client
import random
import time

# Configuración de página
st.set_page_config(page_title="Dashboard Sorteo CarShow", page_icon="🚘", layout="wide")

# Inicializar conexión Supabase usando Secrets
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

st.title("🚘 Gran Sorteo CarShow 2026 - Panel de Control")
st.markdown("---")

# METRICAS GENERALES
col1, col2, col3 = st.columns(3)

try:
    # Obtener total de boletos vendidos
    res_tickets = supabase.table("tickets").select("id", count="exact").execute()
    total_tickets = res_tickets.count if res_tickets.count is not None else 0
    
    # Obtener recaudación total
    res_purchases = supabase.table("purchases").select("amount").execute()
    total_recaudado = sum([p['amount'] for p in res_purchases.data]) if res_purchases.data else 0

    col1.metric("🎟️ Boletos Vendidos", f"{total_tickets:,}")
    col2.metric("💰 Recaudación Total", f"Gs. {total_recaudado:,.0f}")
    col3.metric("🎯 Sorteo Activo", "Sorteo #1")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")

st.markdown("---")

# PESTAÑAS DEL DASHBOARD
tab1, tab2 = st.tabs(["🎟️ Lista de Boletos", "🎉 Ejecutar Sorteo"])

with tab1:
    st.subheader("Boletos Asignados")
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
        
    try:
        data = supabase.table("tickets").select("ticket_number, customer_phone, created_at").order("created_at", desc=True).execute()
        if data.data:
            st.dataframe(data.data, use_container_width=True)
        else:
            st.info("Aún no hay boletos registrados.")
    except Exception as e:
        st.error(f"Error cargando boletos: {e}")

with tab2:
    st.subheader("🎲 Extracción del Boleto Ganador")
    st.write("Presioná el botón para realizar la selección aleatoria de forma transparente sobre la base de datos.")
    
    if st.button("🚀 REALIZAR SORTEO AHORA", type="primary"):
        try:
            todos_boletos = supabase.table("tickets").select("ticket_number, customer_phone").execute().data
            
            if not todos_boletos:
                st.warning("No hay boletos en la base de datos para sortear.")
            else:
                placeholder = st.empty()
                
                # Efecto de ruleta aleatoria
                with st.spinner("Girando bolillero digital..."):
                    for _ in range(25):
                        temp = random.choice(todos_boletos)
                        placeholder.header(f"🎰 NÚMERO: **{temp['ticket_number']}**")
                        time.sleep(0.1)
                
                # Ganador definitivo
                ganador = random.choice(todos_boletos)
                placeholder.empty()
                
                st.balloons()
                st.success(f"🎉 ¡BOLETO GANADOR DEFINITIVO: **{ganador['ticket_number']}**!")
                st.info(f"📱 **Teléfono del Ganador:** {ganador['customer_phone']}")
                
        except Exception as e:
            st.error(f"Error ejecutando el sorteo: {e}")
