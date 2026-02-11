import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# 2. Conexión segura con la IA (vía Secrets)
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Configuración incompleta: No se encontró la clave en 'Secrets'.")
except Exception as e:
    st.error(f"Error de configuración: {e}")

# 3. Base de Datos de Destinos
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
st.markdown("#### Asistencia inteligente para el viajero")
st.divider()

destino_sel = st.selectbox("📍 Seleccioná tu destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Emergencias:**\n\n{datos['telefono']}")
            
        # --- SECCIÓN DE CHAT CON IA ---
        st.divider()
        st.markdown("### 🤖 Asistente Virtual")
        user_question = st.text_input("¿En qué puedo ayudarte hoy?")
        
        if user_question:
            with st.spinner("Consultando con la IA..."):
                # Probamos nombres de modelos estables para evitar el error 404
                modelos_a_probar = ['gemini-pro', 'models/gemini-1.0-pro']
                exito = False
                
                for nombre_modelo in modelos_a_probar:
                    if not exito:
                        try:
                            model = genai.GenerativeModel(nombre_modelo)
                            response = model.generate_content(user_question)
                            st.markdown("---")
                            st.write(response.text)
                            exito = True
                        except:
                            continue # Si uno falla, intenta el siguiente
                
                if not exito:
                    st.error("Lo siento, el servicio de Google no está respondiendo en este momento. Reintentá en unos segundos.")

    elif codigo_input != "":
        st.error("❌ Código incorrecto")

st.divider()
st.caption("SOS Passport © 2026 - Protección y Asistencia")