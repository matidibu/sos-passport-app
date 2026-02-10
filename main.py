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
        "mapa": "https://www.google.com/maps",
        "codigo": "FLORIPA2026"
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
        st.error("❌ Código inválido")
        st.write("¿Aún no tenés tu acceso? Obtenelo al instante:")
        # Aquí es donde pondrás tu link final de cobro
        st.link_button("💳 Comprar acceso por $10 USD", "https://tu-link-de-pago.com")