import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# --- CONFIGURACIÓN DE IA ---
# LA CLAVE VA ACÁ ABAJO (Línea 9). Borrá todo lo que hay entre las comillas y pegá.
API_KEY = 'AIzaSyBp_8YN50oicqeuBltOT-WHB2Fh2yWSuhg'

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Error al conectar con el servidor de IA.")

# --- BASE DE DATOS ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://www.google.com/maps/search/?api=1&query=Consulado+Argentino+Florianopolis", 
        "codigo": "FLORIPA2026"
    }
}

st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 Seleccioná destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        st.info(f"🏛️ **Consulado:** {datos['consulado']}")
        st.link_button("🚀 Abrir Mapa", datos["mapa"])
        
        st.divider()
        st.markdown("### 🤖 Asistente IA")
        user_question = st.text_input("Preguntame algo (ej: ¿Dónde hay un hospital?):")
        
        if user_question:
            with st.spinner("Pensando..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=f"Usuario en {destino_sel}. Ayuda con: {user_question}"
                    )
                    st.write("---")
                    st.write(response.text)
                except Exception as e:
                    st.error("La clave de IA sigue dando error. Verificá que sea la correcta en AI Studio.")