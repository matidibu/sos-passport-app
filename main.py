import streamlit as st
import google.generativeai as genai

# Configuración básica
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 1. EL CÓDIGO BUSCA LA LLAVE EN LA CAJA FUERTE, NO ACÁ.
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Error: No se encontró la llave en los Secrets de Streamlit.")
except Exception as e:
    st.error(f"Error de configuración: {e}")

# 2. Base de Datos
destinos = {
    "Madrid, España": {"codigo": "MADRID2026", "info": "Calle de Fernando el Santo 15"}
}

st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 Destino", ["Seleccionar...", "Madrid, España"])

if destino_sel != "Seleccionar...":
    cod = st.text_input("🔑 Código", type="password")
    if cod == destinos[destino_sel]["codigo"]:
        st.success("ACCESO OK")
        pregunta = st.text_input("🤖 Consultá a la IA:")
        if pregunta:
            with st.spinner("Pensando..."):
                try:
                    # Usamos el modelo 1.0-pro que es el más estable en Santa Fe
                    model = genai.GenerativeModel('gemini-1.0-pro')
                    response = model.generate_content(pregunta)
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

st.caption("SOS Passport © 2026")