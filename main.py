import streamlit as st
from google import genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# 2. Conexión usando la librería moderna y la clave de los Secrets
try:
    if "GOOGLE_API_KEY" in st.secrets:
        # Usamos el cliente oficial de 2026
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("⚠️ Falta la clave en los Secrets de Streamlit.")
except Exception as e:
    st.error(f"Error de conexión inicial: {e}")

# 3. Base de Datos de Destinos
destinos = {
    "Madrid, España": {
        "consulado": "Calle de Fernando el Santo 15, 28010 Madrid.",
        "telefono": "+34 914 02 51 15",
        "codigo": "MADRID2026"
    },
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche.",
        "telefono": "+55 48 3024-3035",
        "codigo": "FLORIPA2026"
    }
}

# 4. Interfaz de Usuario
st.title("🆘 SOS Passport AI")
st.markdown("### Asistencia Inteligente al Viajero")
st.divider()

destino_sel = st.selectbox("📍 ¿A dónde viajás?", ["Seleccionar..."] + list(destinos.keys()))

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
        
        # --- SECCIÓN DEL CHAT ---
        st.divider()
        st.markdown("### 🤖 Asistente Virtual")
        user_question = st.text_input("¿En qué puedo ayudarte?")
        
        if user_question:
            with st.spinner("Consultando a la IA..."):
                exito = False
                # Intentamos con los dos modelos más estables
                for modelo_nombre in ["gemini-1.5-flash", "gemini-1.5-pro"]:
                    if not exito:
                        try:
                            response = client.models.generate_content(
                                model=modelo_nombre, 
                                contents=f"Usuario en {destino_sel}. Pregunta: {user_question}"
                            )
                            st.markdown("---")
                            st.write(response.text)
                            exito = True
                        except:
                            continue # Si el modelo falla, intenta el siguiente
                
                if not exito:
                    st.error("Lo siento, Google no pudo procesar la consulta. Intentá de nuevo en un minuto.")

    elif codigo_input != "":
        st.error("❌ Código incorrecto")

st.divider()
st.caption("SOS Passport © 2026")