import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 2. Configuración de la IA (Con tu clave nueva)
API_KEY = "AIzaSyCwiTUy63Szy_eNB8l_Z9iIQyi8CVS4sEU"
genai.configure(api_key=API_KEY)

# 3. Base de Datos
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "telefono": "+55 48 3024-3035",
        "codigo": "FLORIPA2026"
    },
    "Madrid, España": {
        "consulado": "Calle de Fernando el Santo 15, 28010 Madrid.",
        "telefono": "+34 914 02 51 15",
        "codigo": "MADRID2026"
    }
}

# 4. Interfaz
st.title("🆘 SOS Passport AI")
st.markdown("### Asistencia al Viajero")

destino_sel = st.selectbox("📍 Seleccioná destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        st.info(f"🏛️ **Consulado:** {datos['consulado']}\n\n📞 **Teléfono:** {datos['telefono']}")
        
        st.divider()
        st.markdown("### 🤖 Consulta a la IA")
        user_question = st.text_input("¿En qué puedo ayudarte?")
        
        if user_question:
            with st.spinner("Obteniendo respuesta..."):
                try:
                    # Usamos el modelo 1.5-flash que es el más rápido
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(user_question)
                    
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error de Google: {e}")
    elif codigo_input != "":
        st.error("❌ Código incorrecto")

st.divider()
st.caption("SOS Passport © 2026")