import streamlit as st
import google.generativeai as genai

# Configuración de la página (esto debe ir primero)
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background-color: #FF4B4B; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #D43F3F; color: white; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIGURACIÓN DE INTELIGENCIA ARTIFICIAL ---
# Reemplaza lo que está entre comillas por tu clave real de la foto
API_KEY = "AIzaSyBp_8YN50oicqeuBltOT-WHB2Fh2yWSuhg" 

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error al conectar con la IA. Verifica tu API Key.")

# --- 2. BASE DE DATOS (Links de mapas oficiales y robustos) ---
destinos = {
    "Florianópolis, Brasil": {
        "consulado": "Rod. José Carlos Daux 5500, Torre Campeche, Sala 218, Saco Grande.",
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

# --- INTERFAZ DE USUARIO ---
st.title("🆘 SOS Passport AI")
st.markdown("#### Tu guía inteligente de emergencia en el bolsillo.")
st.divider()

# Paso 1: Selección de destino
destino_sel = st.selectbox("📍 ¿A dónde viajas?", ["Seleccionar..."] + list(destinos.keys()))

if destino_sel != "Seleccionar...":
    datos = destinos[destino_sel]
    
    # Paso 2: Validación de acceso
    codigo_input = st.text_input("🔑 Ingresá tu código de acceso para desbloquear", type="password")

    if codigo_input == datos["codigo"]:
        st.success("✅ ACCESO PREMIUM CONCEDIDO")
        
        # Bloque de Información Crítica
        st.markdown(f"### 📋 Información para {destino_sel}")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏛️ **Consulado:**\n\n{datos['consulado']}")
        with col2:
            st.warning(f"📞 **Emergencias:**\n\n{datos['telefono']}")
            
        # Botón de Mapa con formato universal
        st.link_button("🚀 Abrir GPS en Google Maps", datos["mapa"])
        
        # --- 3. ASISTENTE DE IA (Solo disponible con código correcto) ---
        st.divider()
        st.markdown("### 🤖 Chat de Asistencia Inteligente")
        st.write(f"Preguntame sobre hospitales, trámites o seguridad en {destino_sel}:")
        
        user_question = st.text_input("¿En qué puedo ayudarte hoy?", placeholder="Ej: ¿Qué hago si perdí mi pasaporte?")
        
        if user_question:
            with st.spinner("Consultando con la IA..."):
                try:
                    prompt = f"Eres un experto en asistencia al viajero. El usuario está en {destino_sel}. Responde de forma muy útil, empática y concisa a esta duda: {user_question}"
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(f"**Respuesta de SOS AI:**\n\n{response.text}")
                except Exception as e:
                    st.error("La IA está teniendo un momento de timidez. Por favor, intenta de nuevo en unos segundos.")

    elif codigo_input != "":
        st.error("❌ Código incorrecto o expirado")
        st.info("💡 **¿Todavía no tenés acceso?**")
        # Cambia este link por tu link real de cobro
        st.link_button("💳 COMPRAR GUÍA ESTRATÉGICA ($10 USD)", "https://mpago.la/tu-link-aqui")

st.divider()
st.caption("SOS Passport © 2026 - Tecnología de IA aplicada a tu seguridad.")