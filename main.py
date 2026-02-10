import streamlit as st

# Configuración de la página
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        height: 3.5em; 
        background-color: #FF4B4B; 
        color: white; 
        font-weight: bold; 
        border: none;
    }
    .stButton>button:hover {
        background-color: #D43F3F;
        color: white;
    }
    .stSelectbox label { font-weight: bold; color: #1E1E1E; }
    </style>
    """, unsafe_allow_html=True)

st.title("🆘 SOS Passport")
st.markdown("### Tu seguridad no tiene fronteras.")
st.divider()

# --- 1. BASE DE DATOS REAL (Links de Maps actualizados y robustos) ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218, Saco Grande.",
        "telefono": "+55 48 3024-3035",
        # Link de búsqueda directa para evitar errores de Firebase
        "mapa": "https://www.google.com/maps/search/?api=1&query=Consulado+Argentino+Florianopolis", 
        "codigo": "FLORIPA2026"
    },
    "Madrid, España": {
        "consulado": "Calle de Fernando el Santo 15, Chamberí, 28010 Madrid.",
        "telefono": "+34 914 02 51 15",
        "mapa": "https://www.google.com/maps/search/?api=1&query=Consulado+Argentino+Madrid",
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
            
        # BOTÓN DE MAPA ACTUALIZADO (Formato Universal)
        st.link_button("📍 Abrir en Google Maps (GPS)", datos["mapa"])
        
    elif codigo_input != "":
        st.error("❌ Código inválido o expirado")
        st.info("💡 **¿Necesitás un código?**\n\nAl comprar tu guía estratégica, recibís el código de acceso al instante.")
        
        # --- 2. TU LINK DE PAGO REAL ---
        # Cambiá el link de abajo por tu link de Mercado Pago, PayPal o Stripe
        st.link_button("💳 COMPRAR ACCESO ($10 USD)", "https://mpago.la/tu-link-aqui")

st.divider()
st.caption("SOS Passport © 2026 - Asistencia al viajero")