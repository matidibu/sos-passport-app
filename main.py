import streamlit as st
from groq import Groq
import json

st.set_page_config(page_title="SOS Passport AI", page_icon="🆘")

# 1. Conexión con Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🆘 SOS Passport AI")
st.markdown("### Asistencia Global Dinámica")

# 2. Buscador en lugar de Selectbox
ciudad_destino = st.text_input("📍 ¿A qué ciudad vas? (Ej: Roma, Tokio, Medellín)", "")

if ciudad_destino:
    # Creamos un botón para "Generar Asistencia"
    if st.button(f"Generar guía para {ciudad_destino}"):
        with st.spinner(f"Investigando datos oficiales en {ciudad_destino}..."):
            try:
                # Instrucción estricta para la IA
                prompt_sistema = f"""
                Actúa como un experto en seguridad consular y viajes. 
                Genera una ficha de emergencia para la ciudad de {ciudad_destino}.
                Responde ÚNICAMENTE en formato JSON con estas llaves:
                "consulado": "dirección y teléfono del consulado argentino más cercano",
                "emergencias": "número de policía y ambulancia local",
                "hospital": "nombre y dirección del mejor hospital público/privado",
                "consejo": "un consejo de seguridad clave para esta ciudad"
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_sistema}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"} # Esto asegura que no tire texto de más
                )
                
                # Procesamos la respuesta
                datos = json.loads(chat_completion.choices[0].message.content)
                
                # Mostramos los resultados en cards lindas
                st.success(f"✅ Guía de emergencia: {ciudad_destino}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"🏛️ **Consulado Argentino:**\n\n{datos['consulado']}")
                    st.warning(f"📞 **Números Locales:**\n\n{datos['emergencias']}")
                with col2:
                    st.error(f"🏥 **Salud:**\n\n{datos['hospital']}")
                    st.success(f"💡 **Tip de Seguridad:**\n\n{datos['consejo']}")
                
                # Botón de descarga (Modo Offline inicial)
                texto_pdf = f"SOS PASSPORT - {ciudad_destino}\n\nConsulado: {datos['consulado']}\nEmergencias: {datos['emergencias']}\nSalud: {datos['hospital']}"
                st.download_button("📥 Descargar Guía Offline (TXT)", texto_pdf, file_name=f"SOS_{ciudad_destino}.txt")

            except Exception as e:
                st.error(f"No pudimos obtener datos para esa ciudad. Error: {e}")

st.divider()
st.caption("SOS Passport © 2026 - Información generada por IA en tiempo real.")