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

# --- 1. BASE DE DATOS REAL (Actualizada con links oficiales) ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218, Saco Grande.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://maps.app.goo.gl/35bYofm1HqR2N4kM6", 
        "codigo": "FLORIPA2026"
    },
    "Madrid, España": {
        "consulado": "Calle de Fernando el Santo 15, Chamberí, 28010 Madrid.",
        "telefono": "+34 914 02 51 15",
        "mapa": "https://maps.app.goo.gl/K8P2G9mXmX6xYxYx9",
        "codigo": "MADRID2026"
    }
}

# --- INTERFAZ DE USUARIO ---
st.write("📍 **Paso 1:** Seleccioná tu destino.")
destino_sel = st.selectbox("Destino", ["Seleccionar..."] + list(destinos.keys()), label_visibility="collapsed")

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    
    st.write("🔑 **Paso 2:** Ingresá tu código de acceso.")
    codigo_input = st.text_input("Código de Acceso", type="password", placeholder="Escribí tu código aquí...")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        st.markdown(f"### 📋 Guía para {destino_sel}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Teléfono:**\n\n{datos['telefono']}")
            
        # BOTÓN DE MAPA ACTUALIZADO
        st.link_button("📍 Abrir en Google Maps (GPS)", datos["mapa"])
        
    elif codigo_input != "":
        st.error("❌ Código inválido o expirado")
        st.info("💡 **¿Necesitás un código?**\n\nComprá tu guía y recibí el código al instante.")
        
        # Link de pago (Reemplazalo por el tuyo real de Mercado Pago)
        st.link_button("💳 COMPRAR ACCESO ($10 USD)", "https://tu-link-de-pago-aqui.com")

st.divider()
st.caption("SOS Passport © 2026")