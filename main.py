import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 2. Configuración de la IA (Tu Key actual)
API_KEY = "AIzaSyCwiTUy63Szy_eNB8l_Z9iIQyi8CVS4sEU"
genai.configure(api_key=API_KEY)

# 3. Base de Datos
destinos = {
    "Florianópolis, Brasil": {"codigo": "FLORIPA2026", "consulado": "Rod. José Carlos Daux 5500"},
    "Madrid, España": {"codigo": "MADRID2026", "consulado": "Calle de Fernando el Santo 15"}
}

st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 Destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        st.info(f"🏛️ **Consulado:** {datos['consulado']}")
        
        st.divider()
        user_question = st.text_input("🤖 Consultá a la IA:")
        
        if user_question:
            with st.spinner("Buscando respuesta..."):
                # LISTA DE NOMBRES POSIBLES PARA EL MODELO
                nombres_modelos = [
                    'gemini-1.5-flash', 
                    'gemini-pro', 
                    'models/gemini-1.5-flash', 
                    'models/gemini-pro'
                ]
                
                respuesta_obtenida = False
                for nombre in nombres_modelos:
                    if not respuesta_obtenida:
                        try:
                            model = genai.GenerativeModel(nombre)
                            response = model.generate_content(user_question)
                            st.markdown("---")
                            st.write(response.text)
                            respuesta_obtenida = True
                        except:
                            continue # Si este nombre da 404, prueba el siguiente
                
                if not respuesta_obtenida:
                    st.error("Google no habilitó el modelo para tu región todavía. Reintentá en unos minutos.")

st.caption("SOS Passport © 2026")