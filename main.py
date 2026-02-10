import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURACIÓN DE IA ---
# PEGA ACÁ TU API KEY de la foto que sacaste
os.environ["GOOGLE_API_KEY"] = "TU_API_KEY_AQUI"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# Estilos visuales
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #FF4B4B; color: white; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🆘 SOS Passport AI")
st.markdown("### Asistencia inteligente al viajero")
st.divider()

# --- BASE DE DATOS ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218.",
        "telefono": "+55 48 3024-3035",
        "mapa": "https://www.google.com/maps/search/?api=1&query=Consulado+Argentino+Florianopolis", 
        "codigo": "FLORIPA2026"
    },
    "Madrid, España": {
        "consulado": "Calle de Fernando el Santo 15, Chamberí, 28010 Madrid.",
        "telefono": "+34 914 02 51 15",
        "mapa": "https://www.google.com/maps/search/?api=1&query=Consulado+Argentino+Madrid",
        "codigo": "MADRID2026"
    }
}

# --- INTERFAZ ---
destino_sel = st.selectbox("📍 Seleccioná tu destino", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    codigo_input = st.text_input("🔑 Código de acceso", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO PREMIUM CONCEDIDO")
        
        # Información del destino
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Emergencias:**\n\n{datos['telefono']}")
        
        st.link_button("📍 Abrir GPS en Google Maps", datos["mapa"])
        
        # --- CHATBOT DE IA ---
        st.divider()
        st.markdown("### 🤖 Asistente IA SOS")
        st.write(f"Preguntame lo que necesites sobre {destino_sel} (seguridad, trámites, hospitales, etc.)")
        
        user_question = st.text_input("Escribí tu consulta:")
        if user_question:
            with st.spinner("Pensando..."):
                prompt = f"Eres un experto en asistencia al viajero. El usuario está en {destino_sel}. Responde de forma concisa y útil a: {user_question}"
                response = model.generate_content(prompt)
                st.write("---")
                st.write(response.text)

    elif codigo_input != "":
        st.error("❌ Código incorrecto")
        st.write("¿No tienes acceso? [Cómpralo aquí](https://mpago.la/tu-link)")

st.divider()
st.caption("SOS Passport © 2026 - Ahora con Inteligencia Artificial")