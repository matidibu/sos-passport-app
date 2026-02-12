import streamlit as st
from google import genai

# Configuración de página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 1. Conexión usando la nueva librería
try:
    if "GOOGLE_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Falta la clave en Secrets")
except Exception as e:
    st.error(f"Error de cliente: {e}")

# 2. Datos
destinos = {"Madrid, España": {"codigo": "MADRID2026"}}

st.title("🆘 SOS Passport AI")
destino = st.selectbox("📍 Seleccioná destino", ["Seleccionar...", "Madrid, España"])

if destino != "Seleccionar...":
    cod = st.text_input("🔑 Código", type="password")
    if cod == destinos[destino]["codigo"]:
        st.success("ACCESO OK")
        pregunta = st.text_input("🤖 Chat con IA:")
        
        if pregunta:
            with st.spinner("Conectando con Google..."):
                try:
                    # Usamos el modelo Flash que es el más moderno y rápido
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=pregunta
                    )
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Google dice: {e}")
                    st.info("Aviso: Si el error persiste, puede ser un bloqueo de región temporal en el servidor.")

st.caption("SOS Passport © 2026")