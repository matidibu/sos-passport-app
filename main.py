import streamlit as st
from groq import Groq
import json
import urllib.parse

st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🆘 SOS Passport AI")

# ==========================================
# CONFIGURACIÓN ABIERTA (Nacionalidad libre)
# ==========================================
col_pref1, col_pref2 = st.columns(2)
with col_pref1:
    # Ahora es un campo de texto abierto
    nacionalidad = st.text_input("🌎 Tu Nacionalidad / Your Nationality", placeholder="Ej: Argentina, México, Italia...")
with col_pref2:
    idioma = st.selectbox("🗣️ Idioma / Language", 
                          ["Español", "English", "Português", "Français", "Italiano", "Deutsch"])

st.markdown("---")

# BUSCADOR
labels = {"Español": "Ciudad de destino", "English": "Destination city"}
ciudad_input = st.text_input(labels.get(idioma, "Ciudad / City"), key="buscador")

if ciudad_input and nacionalidad:
    if st.button("OK"):
        with st.spinner("Generando guía personalizada..."):
            try:
                # El Prompt ahora toma cualquier nacionalidad escrita
                prompt = f"""
                Act as a travel safety expert. User nationality: {nacionalidad}. Language: {idioma}. City: {ciudad_input}.
                Return JSON:
                "consulado_info": "Description of the {nacionalidad} consulate in {ciudad_input}",
                "consulado_google": "Exact name of {nacionalidad} consulate in {ciudad_input} for Google Maps",
                "hospital_info": "Best hospital in {ciudad_input}",
                "hospital_google": "Exact hospital name for Google Maps",
                "transporte_link": "Official transport ticket URL",
                "puntos_interes": [
                    {{
                        "nombre": "Name",
                        "nombre_google": "Exact name for Google Maps",
                        "reseña": "Description",
                        "precios": "Fees",
                        "ticket_link": "URL",
                        "horarios": "Hours",
                        "como_llegar": "Transport"
                    }}
                ]
                All text values in {idioma}.
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                res = json.loads(chat_completion.choices[0].message.content)
                
                # Función para link de Google Maps de alta precisión
                def get_map_url(place_name):
                    query = urllib.parse.quote(f"{place_name} {ciudad_input}")
                    return f"https://www.google.com/maps/search/?api=1&query={query}"

                st.success(f"📍 {ciudad_input.upper()} ({nacionalidad.upper()} PASSPORT)")

                # EMERGENCIAS
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown(f"#### 🏛️ Consulado de {nacionalidad}")
                        st.write(res['consulado_info'])
                        st.link_button("📍 Ver Mapa", get_map_url(res['consulado_google']))

                with c2:
                    with st.container(border=True):
                        st.markdown("#### 🏥 Salud")
                        st.write(res['hospital_info'])
                        st.link_button("🚑 Ver Mapa", get_map_url(res['hospital_google']))

                # PUNTOS DE INTERÉS
                st.subheader("🌟 Puntos de Interés")
                for lugar in res['puntos_interes']:
                    with st.expander(f"📍 {lugar['nombre']}"):
                        st.write(lugar['reseña'])
                        t1, t2 = st.columns(2)
                        with t1:
                            st.write(f"🎟️ **Costo:** {lugar['precios']}")
                            st.write(f"🕒 **Horario:** {lugar['horarios']}")
                        with t2:
                            st.write(f"🚌 **Cómo llegar:** {lugar['como_llegar']}")
                            if lugar['ticket_link'] and lugar['ticket_link'] != "none":
                                st.link_button("🛒 Comprar Entradas", lugar['ticket_link'])
                        
                        st.link_button("🗺️ Cómo llegar (Maps)", get_map_url(lugar['nombre_google']))

            except Exception as e:
                st.error(f"Error: {e}")

# GPS DE EMERGENCIA
st.divider()
if st.button("🆘 EMERGENCY GPS"):
    q_hosp = urllib.parse.quote("hospital near me")
    q_cons = urllib.parse.quote(f"consulate {nacionalidad} near me")
    st.link_button("🏥 Hospital Near Me", f"https://www.google.com/maps/search/?api=1&query={q_hosp}")
    st.link_button(f"🏛️ {nacionalidad} Consulate Near Me", f"https://www.google.com/maps/search/?api=1&query={q_cons}")