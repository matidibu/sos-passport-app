import streamlit as st
from google import genai

# 1. Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# 2. Configuración de la IA
# IMPORTANTE: Una sola comilla al principio y una al final.
API_KEY = 'AIzaSyACm5_6sLaiQOOQVsiv-NpZpcA0ffSHZFw' 

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Error de conexión inicial.")

# 3. Base de Datos
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://www.google.com/maps", 
        "codigo": "FLORIPA2026"
    },
    "Madrid, España": {
        "consulado": "Calle de Fernando el Santo 15, 28010 Madrid.",
        "telefono": "+34 914 02 51 15",
        "mapa": "https://www.google.com/maps",
        "codigo": "MADRID2026"
    }
}

# 4. Interfaz
st.title("🆘 SOS Passport AI")
destino_sel = st.selectbox("📍 ¿A dónde viajas?", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO CONCEDIDO")
        st.info(f"🏛️ **Consulado:** {datos['consulado']}\n\n📞 **Emergencias:** {datos['telefono']}")
        
        st.divider()
        st.markdown("### 🤖 Asistente Virtual")
        user_question = st.text_input("Escribí tu consulta aquí:")
        
        if user_question:
            with st.spinner("Buscando respuesta..."):
                # INTENTO 1: Nombre estándar
                try:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash", 
                        contents=user_question
                    )
                    st.write(response.text)
                except Exception as e:
                    # INTENTO 2: Si el 1 falla, prueba con este nombre
                    try:
                        response = client.models.generate_content(
                            model="gemini-1.5-flash-001", 
                            contents=user_question
                        )
                        st.write(response.text)
                    except Exception as e2:
                        st.error(f"Error de Google: El modelo no responde. Detalle: {e2}")

st.divider()
st.caption("SOS Passport © 2026")