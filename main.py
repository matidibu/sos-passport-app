import streamlit as st
from google import genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 2. Llamada a la clave secreta (Configurada en Streamlit Cloud)
try:
    # El código busca la clave que guardamos en el Paso 2
    api_key_secret = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key_secret)
except Exception as e:
    st.error("Error: No se encontró la clave en los Secrets de Streamlit.")
    st.stop()

# 3. Base de Datos
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "codigo": "FLORIPA2026"
    }
}

st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 Destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        
        user_question = st.text_input("🤖 Preguntame algo:")
        if user_question:
            with st.spinner("Pensando..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=user_question
                    )
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error de Google: {e}")