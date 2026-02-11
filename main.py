import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

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

# 4. Interfaz de Usuario
st.title("🆘 SOS Passport AI")
st.markdown("### Asistencia Inteligente al Viajero")
st.divider()

destino_sel = st.selectbox("📍 ¿A dónde viajas?", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Ingresá tu código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Emergencias:**\n\n{datos['telefono']}")
        
        # --- SECCIÓN DE CHAT ---
        st.divider()
        st.markdown("### 🤖 Asistente Virtual")
        user_question = st.text_input("¿En qué puedo ayudarte?")
        
        if user_question:
            with st.spinner("Consultando..."):
                try:
                    # USAMOS EL NOMBRE TÉCNICO COMPLETO PARA EVITAR EL 404
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    response = model.generate_content(f"Usuario en {destino_sel}. Ayuda con: {user_question}")
                    
                    st.markdown("---")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error técnico: {e}")
                    st.info("Tip: Si dice 404, Google está actualizando sus servidores. Reintentá en un minuto.")

    elif codigo_input != "":
        st.error("❌ Código incorrecto")

st.divider()
st.caption("SOS Passport © 2026")