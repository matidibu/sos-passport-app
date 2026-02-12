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
    if st.button(f"Generar Guía Completa para {ciudad_input}"):
        with st.spinner(f"Investigando a fondo {ciudad_input}..."):
            try:
                # Prompt avanzado para obtener detalles de puntos de interés
                prompt = f"""
                Genera una guía detallada para {ciudad_input} en JSON.
                No uses etiquetas técnicas dentro de los valores.
                
                Estructura:
                "consulado": "Info del consulado argentino",
                "hospital": "Info del hospital recomendado",
                "seguridad": "Consejo de seguridad",
                "puntos_interes": [
                    {{
                        "nombre": "Nombre del lugar",
                        "reseña": "Breve descripción atractiva",
                        "ubicacion": "Dirección exacta",
                        "precios": "Costos de entrada o si es gratis",
                        "horarios": "Días y horas de apertura",
                        "como_llegar": "Transporte recomendado (metro, bus, a pie)",
                        "tip_extra": "Dato curioso o mejor hora para ir"
                    }},
                    {{ "... otro lugar ..." }},
                    {{ "... otro lugar ..." }}
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
                with col2:
                    with st.container(border=True):
                        st.markdown("#### 🏥 Salud y Emergencias")
                        st.write(res['hospital'])

                st.divider()
                
                # SECCIÓN PUNTOS DE INTERÉS (Desplegables)
                st.subheader("🌟 Puntos de Interés Recomendados")
                
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
                            st.write(f"💡 **Tip SOS:** {lugar['tip_extra']}")
                        
                        # Botón para ir al mapa directo del lugar
                        st.link_button(f"🗺️ Ir a {lugar['nombre']}", f"https://www.google.com/maps/search/{lugar['nombre']}+{ciudad_input}")

            except Exception as e:
                st.error(f"Error al procesar la guía: {e}")

st.divider()
# Sección de GPS (Se mantiene igual abajo)
st.subheader("📍 Auxilio Inmediato")
if st.button("🆘 Buscar ayuda cerca mío ahora"):
    st.info("Detectando GPS...")
    st.link_button("🏥 Hospital más cercano", "https://www.google.com/maps/search/hospital+near+me")
    st.link_button("🏛️ Consulado Argentino", "https://www.google.com/maps/search/consulado+argentino+near+me")