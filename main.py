import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# --- CONFIGURACIÓN DE IA ---
# Usamos tu clave nueva recién generada
API_KEY = "AIzaSyCvXXh2cLlMUgvhQmi2A67EyYw3yG0KCdI" 

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Error de conexión.")

# --- BASE DE DATOS ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://maps.app.goo.gl/floripa", 
        "codigo": "FLORIPA2026"
    }
}

st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 Seleccioná destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        st.info(f"🏛️ **Consulado:** {datos['consulado']}")
        
        st.divider()
        st.markdown("### 🤖 Asistente IA")
        user_question = st.text_input("Preguntame lo que necesites:")
        
        if user_question:
            with st.spinner("Consultando a la IA..."):
                try:
                    # Llamada limpia a la IA
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=user_question
                    )
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    # Este mensaje nos dirá si el problema es la región o la clave
                    st.error(f"Aviso técnico: {e}")