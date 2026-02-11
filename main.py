import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# --- CONFIGURACIÓN DE IA ---
# ASEGURATE DE QUE TU CLAVE ESTÉ ENTRE COMILLAS SIMPLES
API_KEY = 'AIzaSyBp_8YN50oicqeuBltOT-WHB2Fh2yW5uhg' 

try:
    client = genai.Client(api_key=API_KEY)
    # No usamos variable model aquí para evitar errores
except Exception as e:
    st.error("Error de conexión.")

# --- BASE DE DATOS ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://www.google.com/maps/search/Consulado+Argentino+Florianopolis", 
        "codigo": "FLORIPA2026"
    }
}

st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 Seleccioná destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        st.info(f"🏛️ **Consulado:** {datos['consulado']}")
        st.link_button("🚀 Abrir Mapa", datos["mapa"])
        
        st.divider()
        user_question = st.text_input("🤖 Preguntame algo:")
        if user_question:
            # Nueva forma de llamar a la IA para evitar errores de modelo
            response = client.models.generate_content(model="gemini-1.5-flash", contents=user_question)
            st.write(response.text)