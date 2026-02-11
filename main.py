import streamlit as st
from google import genai

st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 1. Tu Clave
API_KEY = 'AIzaSyBp_8YN50oicqeuBltOT-WHB2Fh2yW5uhg' 

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Error de cliente: {e}")

# 2. Base de Datos Simple
destinos = {
    "Florianópolis, Brasil": {"codigo": "FLORIPA2026", "consulado": "Saco Grande, Sala 218."},
    "Madrid, España": {"codigo": "MADRID2026", "consulado": "Chamberí, Madrid."}
}

st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 Destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    codigo = st.text_input("🔑 Código", type="password")
    if codigo == destinos[destino_sel]["codigo"]:
        st.success("ACCESO OK")
        st.write(f"🏛️ Consulado: {destinos[destino_sel]['consulado']}")
        
        pregunta = st.text_input("🤖 Chat:")
        if pregunta:
            # PRUEBA DE TRES NOMBRES DIFERENTES PARA EL MODELO
            modelos_a_probar = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-flash-001"]
            exito = False
            
            for m in modelos_a_probar:
                if not exito:
                    try:
                        response = client.models.generate_content(model=m, contents=pregunta)
                        st.write(response.text)
                        exito = True
                    except:
                        continue # Si falla uno, prueba el siguiente
            
            if not exito:
                st.error("Google no reconoce ningún nombre de modelo. Revisá AI Studio.")

st.caption("SOS Passport © 2026")