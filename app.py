import streamlit as st
import datetime
from supabase import create_client, Client
import pandas as pd
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Dashboard - Gestión de Sorteos",
    page_icon="🎟️",
    layout="wide"
)

# --- CONEXIÓN A SUPABASE ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "tu-anon-key")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("🎟️ Sistema de Gestión de Sorteos & Boletos")
st.markdown("---")

# --- MENÚ LATERAL ---
opcion = st.sidebar.radio(
    "Navegación",
    ["🏆 Sorteos Activos", "➕ Crear Nuevo Sorteo", "🎟️ Mapa de Boletos", "🎲 Realizar Sorteo"]
)

# -----------------------------------------------------------------------------
# 1. VER Y EDITAR SORTEOS
# -----------------------------------------------------------------------------
if opcion == "🏆 Sorteos Activos":
    st.header("🏆 Sorteos Registrados")
    try:
        response = supabase.table("draws").select("*").order("created_at", desc=True).execute()
        draws = response.data

        if not draws:
            st.info("No hay sorteos creados aún. Creá uno desde el menú lateral.")
        else:
            for draw in draws:
                with st.expander(f"📌 {draw.get('title', 'Sin Título')} - Estado: {draw.get('status')}", expanded=(draw.get('status') == 'ACTIVE')):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if draw.get("image_url"):
                            st.image(draw.get("image_url"), use_column_width=True)
                        else:
                            st.warning("Sin imagen asignada")
                    
                    with col2:
                        st.write(f"**Precio Ticket:** Gs. {draw.get('ticket_price', 0):,}")
                        st.write(f"🥇 **1er Premio:** {draw.get('prize_1', 'N/A')}")
                        st.write(f"🥈 **2do Premio:** {draw.get('prize_2', 'N/A')}")
                        st.write(f"🥉 **3er Premio:** {draw.get('prize_3', 'N/A')}")
                        st.write(f"🗓️ **Fecha Sorteo:** {draw.get('draw_date', 'N/A')}")
                        
                        nuevo_estado = st.selectbox(
                            "Cambiar Estado",
                            ["ACTIVE", "PAUSED", "CLOSED"],
                            index=["ACTIVE", "PAUSED", "CLOSED"].index(draw.get("status", "ACTIVE")),
                            key=f"status_{draw['id']}"
                        )
                        
                        if st.button("Guardar Cambio de Estado", key=f"btn_{draw['id']}"):
                            supabase.table("draws").update({"status": nuevo_estado}).eq("id", draw["id"]).execute()
                            st.success("¡Estado actualizado!")
                            st.rerun()
    except Exception as e:
        st.error(f"Error al consultar Supabase: {e}")

# -----------------------------------------------------------------------------
# 2. CREAR NUEVO SORTEO
# -----------------------------------------------------------------------------
elif opcion == "➕ Crear Nuevo Sorteo":
    st.header("➕ Crear Nuevo Sorteo")
    
    with st.form("form_crear_sorteo"):
        title = st.text_input("Título del Sorteo", placeholder="Ej: GRAN SORTEO FIN DE AÑO")
        ticket_price = st.number_input("Precio por Boleto (Gs.)", min_value=1000, value=20000, step=5000)
        draw_date = st.date_input("🗓️ Fecha del Sorteo", value=datetime.date.today() + datetime.timedelta(days=30))
        
        st.subheader("🎁 Premios")
        prize_1 = st.text_input("🥇 1er Premio", placeholder="Ej: Moto 0km")
        prize_2 = st.text_input("🥈 2do Premio", placeholder="Ej: Smart TV 55'")
        prize_3 = st.text_input("🥉 3er Premio", placeholder="Ej: Vale de Compra Gs. 1.000.000")
        
        image_url = st.text_input("URL de la Imagen (Supabase Storage o Web)", placeholder="https://...")
        
        submitted = st.form_submit_button("🚀 Crear y Activar Sorteo")
        
        if submitted:
            if not title or not prize_1:
                st.error("El título y el 1er premio son obligatorios.")
            else:
                try:
                    supabase.table("draws").update({"status": "PAUSED"}).eq("status", "ACTIVE").execute()
                    
                    nuevo_draw = {
                        "title": title,
                        "ticket_price": ticket_price,
                        "draw_date": str(draw_date),
                        "prize_1": prize_1,
                        "prize_2": prize_2,
                        "prize_3": prize_3,
                        "image_url": image_url,
                        "status": "ACTIVE"
                    }
                    supabase.table("draws").insert(nuevo_draw).execute()
                    st.success("¡Sorteo creado y configurado como ACTIVO!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar en Supabase: {e}")

# -----------------------------------------------------------------------------
# 3. MAPA DE BOLETOS
# -----------------------------------------------------------------------------
elif opcion == "🎟️ Mapa de Boletos":
    st.header("🎟️ Monitor de Boletos y Participantes")
    # ... (Resto del módulo de boletos)

# -----------------------------------------------------------------------------
# 4. SELECCIÓN DE GANADORES
# -----------------------------------------------------------------------------
elif opcion == "🎲 Realizar Sorteo":
    st.header("🎲 Extracción de Ganadores en Vivo")
    # ... (Resto del módulo de sorteo)
