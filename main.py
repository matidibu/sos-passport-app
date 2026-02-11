import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# --- 1. CONFIGURACIÓN DE IA ---
# Pegá tu clave ACÁ ADENTRO (asegurandote que no haya espacios)
llave = "AIzaSyCvXXh2cLIMUgvhQmi2A67EyYw3yGOKCdl"

try:
    client = genai.Client(api_key=llave)
except:
    st.error("Error de conexión.")

# --- 2. BASE DE DATOS ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://www.google.com/maps/search/Consulado+Argentina+Florianopolis", 
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
        st.link_button("🚀 Abrir Mapa", datos["mapa"])
        
        st.divider()
        user_question = st.text_input("🤖 Chat de Ayuda:")
        if user_question:
            try:
                # Usamos una forma más directa de respuesta
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=user_question
                )
                st.write(response.text)
            except Exception as e:
                # Esto nos va a decir el error REAL en la pantalla
                st.error(f"Error técnico: {e}")

    elif codigo_input != "":
        st.error("❌ Código incorrecto")