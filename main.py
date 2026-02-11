import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# --- 1. CONFIGURACIÓN DE IA ---
# IMPORTANTE: Una sola comilla al principio y una sola al final.
API_KEY = 'AIzaSyBp_8YN50oicqeuBltOT-WHB2Fh2yW5uhg'

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Error de conexión con el servidor.")

# --- 2. BASE DE DATOS ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218, Saco Grande.",
        "telefono": "+55 48 3024-3035",
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

# --- 3. INTERFAZ ---
st.title("🆘 SOS Passport AI")
st.markdown("### Asistencia inteligente al viajero")
st.divider()

destino_sel = st.selectbox("📍 Seleccioná tu destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Teléfono:**\n\n{datos['telefono']}")
            
        st.link_button("📍 Abrir en Google Maps", datos["mapa"])
        
        # --- CHATBOT ---
        st.divider()
        st.markdown("### 🤖 Asistente IA")
        user_question = st.text_input("¿En qué puedo ayudarte?")
        
        if user_question:
            with st.spinner("Consultando..."):
                try:
                    # Usando la nueva librería google-genai
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=f"Responde corto: {user_question} (Contexto: el usuario está en {destino_sel})"
                    )
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    st.error("Error: Revisá que la API KEY no tenga comillas de más y que el requirements.txt sea correcto.")

    elif codigo_input != "":
        st.error("❌ Código incorrecto")

st.divider()
st.caption("SOS Passport © 2026")