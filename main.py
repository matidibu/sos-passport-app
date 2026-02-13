import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de conexión. Revisa tus Secrets.")
    st.stop()

# 2. INTERFAZ DE USUARIO
st.title("🆘 SOS Passport AI")
st.markdown("### Experiencia Integral de Asistencia al Viajero")

col_pref1, col_pref2 = st.columns(2)
with col_pref1:
    nacionalidad = st.text_input("🌎 Tu Nacionalidad", value="Argentina")
with col_pref2:
    idioma = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Français"])

st.markdown("---")

# 3. BUSCADOR PRINCIPAL
ciudad_input = st.text_input("📍 Ciudad de destino", placeholder="Ej: Río de Janeiro, Brasil")

if ciudad_input and nacionalidad:
    search_key = f"{ciudad_input.lower()}-{nacionalidad.lower()}-{idioma.lower()}".strip()
    
    if st.button("Generar Guía Integral"):
        guia_final = None
        
        # BUSCAR EN SUPABASE
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data and len(query.data) > 0:
                guia_final = query.data[0]['datos_jsonb']
        except: pass

        # GENERAR SI NO EXISTE
        if not guia_final:
            with st.spinner(f"Generando experiencia completa con fotos para {ciudad_input}..."):
                prompt = f"""
                Genera una guía EXHAUSTIVA para un ciudadano {nacionalidad} en {ciudad_input} en {idioma}.
                Incluye 10 puntos de interés.
                IMPORTANTE: Para cada lugar, inventa un término de búsqueda preciso para fotos.
                
                Estructura JSON:
                {{
                    "consulado": "Info consulado",
                    "hospital": "Info hospital",
                    "hospital_nombre": "Nombre hospital",
                    "puntos_interes": [
                        {{
                            "nombre": "Nombre lugar",
                            "ranking": "⭐ (1 a 5)",
                            "tipo_visita": "Categoría",
                            "reseña": "Descripción",
                            "precios": "Costos",
                            "ticket_link": "URL o 'none'",
                            "horarios": "Horas",
                            "como_llegar": "Transporte",
                            "termino_foto": "Termino para buscar en Google Images",
                            "tip_experiencia": "Consejo"
                        }}
                    ]
                }}
                """
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia_final = json.loads(completion.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia_final}).execute()

        # 4. MOSTRAR RESULTADOS
        if guia_final:
            st.divider()
            
            # Bloque Emergencia
            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.subheader("🏛️ Consulado")
                    st.write(guia_final.get('consulado'))
            with c2:
                with st.container(border=True):
                    st.subheader("🏥 Hospital")
                    st.write(guia_final.get('hospital'))

            st.divider()
            
            # --- NUEVA SECCIÓN: BUSCADOR INTERNO ---
            st.subheader(f"🌟 Imperdibles en {ciudad_input.title()}")
            search_interno = st.text_input("🔍 ¿Buscas algo específico? (ej: Playa, Museo, Gratis...)", key="interno")

            for lugar in guia_final.get('puntos_interes', []):
                # Lógica del buscador interno
                if search_interno.lower() in lugar['nombre'].lower() or \
                   search_interno.lower() in lugar['tipo_visita'].lower() or \
                   search_interno.lower() in lugar['reseña'].lower():
                    
                    with st.container(border=True):
                        col_txt, col_img = st.columns([2, 1])
                        
                        with col_txt:
                            st.markdown(f"### {lugar['nombre']} {lugar['ranking']}")
                            st.caption(f"📌 {lugar['tipo_visita']}")
                            st.write(lugar['reseña'])
                            st.info(f"💡 **Tip:** {lugar['tip_experiencia']}")
                        
                        with col_img:
                            # Generamos un link a Google Images o una imagen placeholder con el nombre
                            search_url = f"https://www.google.com/search?q={urllib.parse.quote(lugar['nombre'] + ' ' + ciudad_input)}&tbm=isch"
                            # Usamos una imagen de servicio gratuito para ilustrar (Unsplash)
                            st.image(f"https://source.unsplash.com/400x300/?{urllib.parse.quote(lugar['tipo_visita'])}", caption=lugar['nombre'])
                            st.link_button("🖼️ Ver más fotos", search_url, use_container_width=True)

                        # Detalles técnicos
                        inf1, inf2, inf3 = st.columns(3)
                        with inf1: st.write(f"💰 **Precios:**\n{lugar['precios']}")
                        with inf2: st.write(f"⏰ **Horarios:**\n{lugar['horarios']}")
                        with inf3: st.write(f"🚌 **Llegar:**\n{lugar['como_llegar']}")
                        
                        btn1, btn2 = st.columns(2)
                        with btn1:
                            q_map = urllib.parse.quote(f"{lugar['nombre']} {ciudad_input}")
                            st.link_button("🗺️ Mapa", f"https://www.google.com/maps/search/{q_map}", use_container_width=True)
                        with btn2:
                            if lugar['ticket_link'] != "none":
                                st.link_button("🎟️ Tickets", lugar['ticket_link'], use_container_width=True, type="primary")

st.divider()
st.caption("SOS Passport © 2026")