import streamlit as st
import google.generativeai as genai

# 1. Configuración básica
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 2. Tu Nueva Clave
API_KEY = "AIzaSyCwiTUy63Szy_eNB8l_Z9iIQyi8CVS4sEU"
genai.configure(api_key=API_KEY)

# 3. Base de Datos
destinos = {
    "Madrid, España": {"codigo": "MADRID2026", "info": "Calle de Fernando el Santo 15"}
}

st.title("🆘 SOS Passport AI")
destino = st.selectbox("📍 Destino", ["Seleccionar...", "Madrid, España"])

if destino != "Seleccionar...":
    cod = st.text_input("🔑 Código", type="password")
    if cod == destinos[destino]["codigo"]:
        st.success("ACCESO OK")
        
        pregunta = st.text_input("🤖 Consultá a la IA:")
        if pregunta:
            with st.spinner("Pensando..."):
                try:
                    # FORZAMOS EL MODELO 1.0 PRO (El más compatible en Argentina)
                    model = genai.GenerativeModel('gemini-1.0-pro')
                    response = model.generate_content(pregunta)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
                    st.info("Intentá usar los datos del celular (Hotspot) un segundo, a veces el Wi-Fi local bloquea a Google.")

st.caption("SOS Passport © 2026")