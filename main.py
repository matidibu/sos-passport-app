import streamlit as st
from groq import Groq

st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 1. Conexión con Groq (La nueva llave en Secrets)
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("Falta la llave GROQ_API_KEY en Secrets")
except Exception as e:
    st.error(f"Error: {e}")

destinos = {"Madrid, España": {"codigo": "MADRID2026"}}

st.title("🆘 SOS Passport AI")
destino = st.selectbox("📍 Seleccioná destino", ["Seleccionar...", "Madrid, España"])

if destino != "Seleccionar...":
    cod = st.text_input("🔑 Código", type="password")
    if cod == destinos[destino]["codigo"]:
        st.success("ACCESO OK")
        pregunta = st.text_input("🤖 Chat con IA (Llama 3):")
        
        if pregunta:
            with st.spinner("Groq está pensando..."):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": pregunta}],
                        model="llama-3.3-70b-versatile",
                    )
                    st.write(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error de Groq: {e}")