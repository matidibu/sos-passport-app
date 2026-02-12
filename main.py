import streamlit as st
from groq import Groq
import json

st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==========================================
# CONFIGURACIÓN INICIAL (Nacionalidad e Idioma)
# ==========================================
st.title("🆘 SOS Passport AI")

col_pref1, col_pref2 = st.columns(2)
with col_pref1:
    nacionalidad = st.selectbox("🌎 Tu Nacionalidad / Your Nationality", 
                                ["Argentina", "Uruguay", "Chile", "México", "España", "Colombia", "USA", "Brasil"])
with col_pref2:
    idioma = st.selectbox("🗣️ Idioma de la App / Language", 
                          ["Español", "English", "Português", "Français", "Italiano"])

st.markdown("---")

# ==========================================
# SECCIÓN 1: BUSCADOR DINÁMICO
# ==========================================
# Traducimos el label del buscador según el idioma elegido
labels = {
    "Español": "Ingresá la ciudad de destino",
    "English": "Enter your destination city",
    "Português": "Digite a cidade de destino",
    "Français": "Entrez la ville de destination",
    "Italiano": "Inserisci la città de destinazione"
}

ciudad_input = st.text_input(labels[idioma], key="buscador")

if ciudad_input:
    if st.button("OK"):
        with st.spinner("..."):
            try:
                # El Prompt ahora es dinámico según nacionalidad e idioma
                prompt = f"""
                Act as a global travel safety expert.
                The user is {nacionalidad} and wants the information in {idioma}.
                City: {ciudad_input}.
                
                Return a JSON with:
                "consulado": "Address and phone of the {nacionalidad} consulate in {ciudad_input}",
                "hospital": "Best hospital nearby with address",
                "hospital_nombre": "Just the hospital name for Google Maps",
                "transporte_link": "Official link to buy public transport passes in {ciudad_input}",
                "seguridad": "One critical safety tip for this city",
                "puntos_interes": [
                    {{
                        "nombre": "Place name",
                        "reseña": "Short description",
                        "precios": "Entry fees",
                        "ticket_link": "Official ticket website or 'none'",
                        "horarios": "Opening hours",
                        "como_llegar": "How to get there"
                    }}
                ]
                All text values must be in {idioma}.
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                res = json.loads(chat_completion.choices[0].message.content)
                
                # Renderizado de la información
                st.success(f"📍 {ciudad_input.upper()}")
                
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown(f"#### 🏛️ {res.get('consulado_titulo', 'Consulado')}")
                        st.write(res['consulado'])
                        st.link_button("Maps", f"https://maps.google.com/?cid=15516772469038778077&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQ{nacionalidad}+consulate+{ciudad_input}")

                with c2:
                    with st.container(border=True):
                        st.markdown("#### 🏥 Salud / Health")
                        st.write(res['hospital'])
                        st.link_button("🚑 Maps", f"https://maps.google.com/maps/contrib/100984570847078626087{res['hospital_nombre']}+{ciudad_input}")

                if res.get('transporte_link'):
                    st.link_button("🎫 Tickets & Transport", res['transporte_link'], type="primary")

                st.divider()
                st.subheader("🌟 Points of Interest")
                
                for lugar in res['puntos_interes']:
                    with st.expander(f"📍 {lugar['nombre']}"):
                        st.write(f"**📖:** {lugar['reseña']}")
                        t1, t2 = st.columns(2)
                        with t1:
                            st.write(f"🎟️: {lugar['precios']}")
                            st.write(f"🕒: {lugar['horarios']}")
                        with t2:
                            st.write(f"🚌: {lugar['como_llegar']}")
                            if lugar['ticket_link'] and lugar['ticket_link'] != "none":
                                st.link_button("🛒 Buy Tickets", lugar['ticket_link'])
                        
                        st.link_button("🗺️ Maps", f"https://www.google.com/maps/dir/?api=1&destination=-31.6485,-60.71890{lugar['nombre']}+{ciudad_input}")

            except Exception as e:
                st.error(f"Error: {e}")

# SECCIÓN GPS (Simplificada)
st.divider()
if st.button("🆘 EMERGENCY GPS"):
    st.link_button("🏥 Hospital Near Me", "https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgID4_5GsQA!2e10!4m2!3m1!1s0x95b5a9b284214497:0xd756a659659e06dd")
    st.link_button(f"🏛️ {nacionalidad} Consulate Near Me", f"https://maps.google.com/maps/contrib/105314273679854713821{nacionalidad}+consulate")