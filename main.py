import streamlit as st

# Configuración de la página
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; }
    .stSelectbox label { font-weight: bold; color: #1E1E1E; }
    </style>
    """, unsafe_allow_html=True)

st.title("🆘 SOS Passport")
st.markdown("### Tu seguridad no tiene fronteras.")
st.divider()

# --- 1. BASE DE DATOS MEJORADA (Destinos, Códigos y Maps) ---
# Aquí puedes agregar todos los destinos que quieras siguiendo el mismo formato
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Calle de la Amistad 123, Centro.",
        "telefono": "+55 48 1234-5678",
        "mapa": "https://maps.app.goo.gl/YpGkS1zP9fT9YpGkS", # <--- Poné el link real de Google Maps aquí
        "codigo": "FLORIPA2026"
    },
    "Madrid, España": {
        "consulado": "Calle de Serrano 90, 28006 Madrid.",
        "telefono": "+34 917 54 32 10",
        "mapa": "https://maps.app.goo.gl/XyZ123456789", # <--- Link real de Maps aquí
        "codigo": "MADRID2026"
    }
}

# --- INTERFAZ DE USUARIO ---
st.write("📍 **Paso 1:** Seleccioná tu destino para ver la guía estratégica.")
destino_sel = st.selectbox("Destino", ["Seleccionar..."] + list(destinos.keys()), label_visibility="collapsed")

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    
    st.write("🔑 **Paso 2:** Ingresá tu código de acceso para desbloquear la información.")
    codigo_input = st.text_input("Código de Acceso", type="password", placeholder="Escribí tu código aquí...")

    # --- 2. LÓGICA DE ACCESO Y BOTÓN DE PAGO ---
    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        
        st.markdown(f"### 📋 Guía para {destino_sel}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Emergencias:**\n\n{datos['telefono']}")
            
        # --- 3. BOTÓN DE MAPA REAL ---
        st.link_button("📍 Abrir ubicación en Google Maps", datos["mapa"])
        
    elif codigo_input != "":
        st.error("❌ Código inválido o expirado")
        st.info("💡 **¿Todavía no tenés tu código?**\n\nAl comprar la guía, recibís el código de acceso al instante en tu email para desbloquear toda la información de emergencia.")
        
        # LINK DE PAGO (Reemplazá por tu link de Mercado Pago, PayPal o Global66)
        st.link_button("💳 COMPRAR ACCESO AHORA ($15 USD)", "https://tu-link-de-pago-aqui.com")

st.divider()
st.caption("SOS Passport © 2026 - Asistencia al viajero 24/7")