import datetime

# -----------------------------------------------------------------------------
# 2. CREAR NUEVO SORTEO
# -----------------------------------------------------------------------------
elif opcion == "➕ Crear Nuevo Sorteo":
    st.header("➕ Crear Nuevo Sorteo")
    
    with st.form("form_crear_sorteo"):
        title = st.text_input("Título del Sorteo", placeholder="Ej: GRAN SORTEO FIN DE AÑO")
        ticket_price = st.number_input("Precio por Boleto (Gs.)", min_value=1000, value=20000, step=5000)
        
        # Campo de Fecha de Sorteo (Recomendado por el Comité)
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
                    # Pausar sorteos anteriores para dejar solo uno activo
                    supabase.table("draws").update({"status": "PAUSED"}).eq("status", "ACTIVE").execute()
                    
                    # Insertar el nuevo sorteo completo
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
                    st.success("¡Sorteo creado y configurado como ACTIVO con éxito!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar en Supabase: {e}")
