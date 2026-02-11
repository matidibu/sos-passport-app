import streamlit as st
from google import genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# 2. Configuración de la IA con tu NUEVA KEY
API_KEY = 'AIzaSyACm5_6sLaiQOOQVsiv-NpZpcA0ffSHZFw' 

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Error de conexión.")

# 3. Base de Datos de Destinos
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218, Saco Grande.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://www.google.com/maps/search/Consulado+Argentina+Florianopolis", 
        "codigo": "FLORIPA2026"
    },
    "Madrid, España": {
        "consulado": "Calle de Fernando el Santo 15, Chamberí, 28010 Madrid.",
        "telefono": "+34 914 02 51 15",
        "mapa": "https://www.google.com/maps/search/Consulado+Argentina+Madrid",
        "codigo": "MADRID2026"
    }
}

# 4. Interfaz de Usuario
st.title("🆘 SOS Passport AI")
st.markdown("#### Asistencia inteligente para el viajero")
st.divider()

# Selector de destino
destino_sel = st.selectbox("📍 ¿A dónde viajas?", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    
    # Validación por código
    codigo_input = st.text_input("🔑 Ingresá tu código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        
        # Información del destino
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Emergencias:**\n\n{datos['telefono']}")
            
        st.link_button("🚀 Abrir ubicación en Google Maps", datos["mapa"])
        
        # --- SECCIÓN DE CHAT CON IA ---
        st.divider()
        st.markdown("### 🤖 Asistente Virtual SOS")
        user_question = st.text_input("¿En qué puedo ayudarte?")
        
        if user_question:
            with st.spinner("Consultando..."):
                try:
                    # El nombre exacto para que no dé error 404
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=f"Responde de forma corta y como un experto en asistencia al viajero. El usuario está en {destino_sel}. Pregunta: {user_question}"
                    )
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error de la IA: {e}")

    elif codigo_input != "":
        st.error("❌ Código incorrecto")

st.divider()
st.caption("SOS Passport © 2026")