import streamlit as st
from groq import Groq
import json

# Configuración de página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

# Conexión con Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🆘 SOS Passport AI")
st.markdown("---")

# SECCIÓN 1: BUSCADOR DE CIUDAD
st.subheader("🔍 Planificá tu viaje")
ciudad_input = st.text_input("Ingresá la ciudad de destino (Ej: Roma, Madrid, Londres)", key="buscador_principal")

if ciudad_input:
    if st.button(f"Generar Guía para {ciudad_input}"):
        with st.spinner(f"Construyendo kit para {ciudad_input}..."):
            try:
                # Prompt estricto para recibir SOLO info, sin etiquetas técnicas
                prompt = f"""
                Genera una ficha de emergencia para {ciudad_input} en JSON.
                IMPORTANTE: Los valores deben ser texto directo. No incluyas palabras como 'nombre:', 'dirección:' o 'teléfono:' dentro del texto.
                
                Estructura requerida:
                "consulado": "Dirección y teléfono del consulado argentino",
                "hospital": "Nombre y ubicación del hospital recomendado",
                "seguridad": "Consejo clave de seguridad (máximo 15 palabras)",
                "puntos_interes": "Los 3 lugares más importantes descritos brevemente"
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                res = json.loads(chat_completion.choices[0].message.content)
                
                st.success(f"📍 {ciudad_input.upper()}")
                
                # Diseño de columnas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### 🏛️ Consulado")
                    # Usamos .replace o simplemente mostramos el valor limpio
                    st.write(res['consulado'])
                    st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/consulado+argentino+{ciudad_input}")

                with col2:
                    st.markdown("#### 🏥 Hospital")
                    st.write(res['hospital'])
                    st.link_button("🚑 Emergencias", f"https://www.google.com/maps/search/hospital+{ciudad_input}")

                with col3:
                    st.markdown("#### 🌟 Imperdibles")
                    st.write(res['puntos_interes'])
                    st.info(f"🛡️ **Seguridad:** {res['seguridad']}")
            
            except Exception as e:
                st.error("Hubo un problema al procesar los datos. Reintentá en un momento.")

st.markdown("---")

# SECCIÓN 2: UBICACIÓN ACTUAL
st.subheader("📍 Auxilio Inmediato")
st.write("¿Ya estás de viaje? Accedé a ayuda basada en tu posición real.")

if st.button("🆘 Buscar ayuda cerca mío ahora"):
    st.info("Detectando GPS... Hacé clic abajo para abrir la ruta en tu celular:")
    
    gps_col1, gps_col2 = st.columns(2)
    with gps_col1:
        st.link_button("🏥 Hospital más cercano", "https://www.google.com/maps/search/hospital+near+me")
    with gps_col2:
        st.link_button("🏛️ Consulado Argentino", "https://www.google.com/maps/search/consulado+argentino+near+me")

st.divider()
st.caption("SOS Passport © 2026")