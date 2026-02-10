import streamlit as st

st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="centered")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🆘 SOS Passport")
st.caption("Tu seguridad no tiene fronteras.")

# --- BASE DE DATOS ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Calle de la Amistad 123",
        "telefono": "+55 48 1234-5678",
        "mapa": "https://maps.app.goo.gl/N422pe89Qo484cZT9",
        "codigo": "FLORIPA_SAFE" # <--- Cambialo acá
    },
    "Madrid, España": {
        "consulado": "Calle Serrano 90",
        "telefono": "+34 91 123 4567",
        "mapa": "https://maps.app.goo.gl/MadridUbicacion",
        "codigo": "MADRID_SAFE"
    }
}

# --- INTERFAZ ---
destino_sel = st.selectbox("📍 Seleccioná tu destino:", ["Seleccionar...", "Florianópolis, Brasil"])

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    
    codigo_input = st.text_input("🔑 Ingresá tu código de acceso:", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ Acceso Concedido")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Teléfono:**\n{datos['telefono']}")
            
        st.link_button("📍 Ver ubicación en el Mapa", datos["mapa"])
        
    elif codigo_input != "":
        st.error("❌ Código inválido o expirado")
        st.write("Obtené tu código de acceso al instante aquí:")
        
        # Reemplaza el link entre comillas por tu link de Mercado Pago o PayPal
        st.link_button("💳 Pagar Guía de Emergencia ($10 USD)", "https://mpago.la/TuLinkDePago")
        
        st.caption("Una vez realizado el pago, recibirás el código en tu email.")