import streamlit as st
from groq import Groq
import json

# Configuración de página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

# Conexión con Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🆘 SOS Passport AI")
st.markdown("---")

# ==========================================
# SECCIÓN 1: BUSCADOR DE CIUDAD (Prioridad)
# ==========================================
st.subheader("🔍 Planificá tu viaje")
ciudad_buscada = st.text_input("Ingresá la ciudad de destino (Ej: Roma, Madrid, Londres)", "")

if ciudad_buscada:
    if st.button(f"Generar Guía para {ciudad_buscada}"):
        with st.spinner(f"Construyendo kit de emergencia para {ciudad_buscada}..."):
            try:
                # El Prompt solicita info y además el link de búsqueda de Google Maps
                prompt = f"""
                Genera una ficha de emergencia para {ciudad_buscada} en formato JSON.
                Incluye:
                "consulado": "Dirección y tel del consulado argentino",
                "hospital": "Nombre del mejor hospital cercano",
                "seguridad": "Consejo clave de seguridad",
                "puntos_interes": "3 lugares icónicos recomendados por viajeros"
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                res = json.loads(chat_completion.choices[0].message.content)
                
                # Diseño de la respuesta
                st.success(f"📍 Destino: {ciudad_buscada}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.info(f"🏛️ **Consulado**\n\n{res['consulado']}")
                    # Link directo a Google Maps para esa ciudad
                    url_maps = f"https://www.google.com/maps/search/consulado+argentino+en+{ciudad_buscada.replace(' ', '+')}"
                    st.link_button("🗺️ Ver en Mapa", url_maps)
                with c2:
                    st.error(f"🏥 **Hospital**\n\n{res['hospital']}")
                    url_hosp = f"https://www.google.com/maps/search/hospitales+en+{ciudad_buscada.replace(' ', '+')}"
                    st.link_button("🚑 Buscar Hospitales", url_hosp)
                with c3:
                    st.warning(f"🌟 **Imperdibles**\n\n{res['puntos_interes']}")
                    st.success(f"🛡️ **Seguridad**\n\n{res['seguridad']}")
            
            except Exception as e:
                st.error("Error al conectar con el cerebro de la IA.")

st.markdown("---")

# ==========================================
# SECCIÓN 2: UBICACIÓN ACTUAL (Auxilio)
# ==========================================
st.subheader("📍 Auxilio Inmediato")
st.write("¿Ya estás de viaje? Obtené ayuda basada en tu posición actual.")

if st.button("🆘 Detectar mi ubicación y buscar ayuda"):
    # Nota: Aquí usamos el link dinámico de Google Maps que abre el GPS del usuario
    st.info("Detectando GPS... Abrí los siguientes accesos directos para ayuda inmediata:")
    
    col_gps1, col_gps2 = st.columns(2)
    with col_gps1:
        # Este link busca hospitales cerca de donde esté el usuario parado
        st.link_button("🏥 Hospital más cercano (GPS)", "https://www.google.com/maps/search/hospital+near+me/")
    with col_gps2:
        # Este link busca el consulado argentino más cercano a su GPS
        st.link_button("🏛️ Consulado Argentino (GPS)", "https://www.google.com/maps/search/consulado+argentino+near+me/")
    
    st.caption("Al hacer clic, se abrirá Google Maps con tu ubicación en tiempo real.")

st.divider()
st.caption("SOS Passport © 2026 - Tu seguridad es nuestra prioridad.")