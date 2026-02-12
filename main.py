import streamlit as st
from groq import Groq
import json

st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🆘 SOS Passport AI")
st.markdown("---")

st.subheader("🔍 Planificá tu viaje")
ciudad_input = st.text_input("Ingresá la ciudad de destino", key="buscador")

if ciudad_input:
    if st.button(f"Generar Guía Premium para {ciudad_input}"):
        with st.spinner(f"Investigando accesos y tickets en {ciudad_input}..."):
            try:
                prompt = f"""
                Genera una guía de ultra-detalle para {ciudad_input} en JSON.
                
                Estructura requerida:
                "consulado": "Info del consulado argentino",
                "hospital": "Info del hospital recomendado",
                "hospital_nombre": "Solo el nombre del hospital para el mapa",
                "seguridad": "Consejo de seguridad",
                "transporte_link": "Link a la web oficial de transporte público de la ciudad para comprar pases",
                "puntos_interes": [
                    {{
                        "nombre": "Nombre del lugar",
                        "reseña": "Breve descripción",
                        "ubicacion": "Dirección",
                        "precios": "Costo estimado",
                        "ticket_link": "Link directo a la web de venta de entradas (oficial o Civitatis/GetYourGuide). Si es gratis, poner 'none'",
                        "horarios": "Horarios",
                        "como_llegar": "Transporte"
                    }}
                ]
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                res = json.loads(chat_completion.choices[0].message.content)
                
                st.success(f"📍 {ciudad_input.upper()}")
                
                # Fila de Emergencia
                col1, col2 = st.columns(2)
                with col1:
                    with st.container(border=True):
                        st.markdown("#### 🏛️ Consulado Argentino")
                        st.write(res['consulado'])
                        st.link_button("🗺️ Ver Consulado en Mapa", f"https://www.google.com/maps/search/Consulado+Argentino+{ciudad_input}")

                with col2:
                    with st.container(border=True):
                        st.markdown("#### 🏥 Salud y Emergencias")
                        st.write(res['hospital'])
                        st.link_button("🚑 Ver Hospital en Mapa", f"https://www.google.com/maps/search/{res['hospital_nombre']}+{ciudad_input}")

                # Botón de Transporte Público
                if res.get('transporte_link'):
                    st.link_button("🎫 Comprar Pasajes de Transporte Público", res['transporte_link'], type="primary")

                st.divider()
                
                # SECCIÓN PUNTOS DE INTERÉS
                st.subheader("🌟 Puntos de Interés y Tickets")
                
                for lugar in res['puntos_interes']:
                    with st.expander(f"📍 {lugar['nombre']}"):
                        st.write(f"**📖 Reseña:** {lugar['reseña']}")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"📌 **Ubicación:** {lugar['ubicacion']}")
                            st.write(f"🎟️ **Precios:** {lugar['precios']}")
                            st.write(f"🕒 **Horarios:** {lugar['horarios']}")
                        with c2:
                            st.write(f"🚌 **Cómo llegar:** {lugar['como_llegar']}")
                            # Botón de tickets si no es gratis
                            if lugar['ticket_link'] and lugar['ticket_link'] != "none":
                                st.link_button(f"🛒 Comprar Entradas para {lugar['nombre']}", lugar['ticket_link'])
                        
                        st.link_button(f"🗺️ Ir a {lugar['nombre']}", f"https://www.google.com/maps/search/{lugar['nombre']}+{ciudad_input}")

            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.subheader("📍 Auxilio Inmediato")
if st.button("🆘 Buscar ayuda cerca mío ahora"):
    st.link_button("🏥 Hospital más cercano", "https://www.google.com/maps/search/hospital+near+me")
    st.link_button("🏛️ Consulado Argentino", "https://www.google.com/maps/search/consulado+argentino+near+me")