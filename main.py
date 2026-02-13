import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime, timedelta
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de conexión. Verifica tus Secrets.")
    st.stop()

# 3. INTERFAZ DE USUARIO
st.title("🆘 SOS Passport AI")
st.markdown("### Experiencia Integral de Asistencia al Viajero")

col_pref1, col_pref2 = st.columns(2)
with col_pref1:
    nacionalidad = st.text_input("🌎 Tu Nacionalidad", value="Argentina")
with col_pref2:
    idioma = st.selectbox("🗣️ Idioma de la guía", ["Español", "English", "Português", "Français"])

st.markdown("---")

# 4. BUSCADOR
ciudad_input = st.text_input("📍 Ciudad de destino", placeholder="Ej: Río de Janeiro, Brasil")

if ciudad_input and nacionalidad:
    search_key = f"{ciudad_input.lower()}-{nacionalidad.lower()}-{idioma.lower()}".strip()
    
    if st.button("Generar Guía Integral"):
        guia_final = None
        
        # --- PASO A: BUSCAR EN SUPABASE ---
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data and len(query.data) > 0:
                guia_final = query.data[0]['datos_jsonb']
                st.info("⚡ Información recuperada de la base de datos.")
        except:
            pass

        # --- PASO B: GENERAR CON IA SI NO EXISTE ---
        if not guia_final:
            with st.spinner(f"Generando experiencia completa para {ciudad_input}..."):
                try:
                    prompt = f"""
                    Genera una guía EXHAUSTIVA para un ciudadano {nacionalidad} en {ciudad_input} en idioma {idioma}.
                    Incluye al menos 10 puntos de interés variados (educación, relax, entretenimiento, etc.).
                    
                    Estructura JSON obligatoria:
                    {{
                        "consulado": "Dirección y contacto del consulado",
                        "hospital": "Dirección y contacto del hospital",
                        "hospital_nombre": "Nombre para mapa",
                        "puntos_interes": [
                            {{
                                "nombre": "Nombre del lugar",
                                "ranking": "⭐ (1 a 5)",
                                "tipo_visita": "Relax / Educación / Entretenimiento / etc",
                                "reseña": "Descripción detallada",
                                "precios": "Costos estimados",
                                "ticket_link": "URL de compra o 'none'",
                                "horarios": "Horas de apertura",
                                "como_llegar": "Transporte recomendado",
                                "tip_experiencia": "Consejo para el viajero"
                            }}
                        ]
                    }}
                    """
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    
                    guia_final = json.loads(chat_completion.choices[0].message.content)
                    
                    # GUARDAR EN SUPABASE
                    supabase.table("guias").upsert({
                        "clave_busqueda": search_key,
                        "datos_jsonb": guia_final,
                        "created_at": datetime.now().isoformat()
                    }).execute()
                    
                except Exception as e:
                    st.error(f"Error: {e}")

        # --- 5. MOSTRAR RESULTADOS ---
        if guia_final:
            st.divider()
            st.header(f"📍 Guía Integral: {ciudad_input.title()}")
            
            # Bloque de Emergencia
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.subheader(f"🏛️ Consulado de {nacionalidad}")
                    st.write(guia_final.get('consulado'))
                    q_cons = urllib.parse.quote(f"consulado de {nacionalidad} en {ciudad_input}")
                    st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/{q_cons}")

            with col2:
                with st.container(border=True):
                    st.subheader("🏥 Hospital Recomendado")
                    st.write(guia_final.get('hospital'))
                    q_hosp = urllib.parse.quote(f"{guia_final.get('hospital_nombre')} {ciudad_input}")
                    st.link_button("🚑 Emergencias Mapa", f"https://www.google.com/maps/search/{q_hosp}")

            # Bloque de Puntos de Interés (Los 10+ lugares)
            st.subheader("🌟 Imperdibles y Experiencias")
            for lugar in guia_final.get('puntos_interes', []):
                with st.container(border=True):
                    c_tit, c_rank = st.columns([3, 1])
                    with c_tit:
                        st.markdown(f"### {lugar['nombre']}")
                        st.caption(f"📌 Tipo de visita: {lugar['tipo_visita']}")
                    with c_rank:
                        st.subheader(lugar['ranking'])
                    
                    st.write(lugar['reseña'])
                    st.info(f"💡 **Tip:** {lugar.get('tip_experiencia', 'Disfruta el recorrido')}")
                    
                    col_inf1, col_inf2, col_inf3 = st.columns(3)
                    with col_inf1:
                        st.write(f"💰 **Precios:**\n{lugar['precios']}")
                    with col_inf2:
                        st.write(f"⏰ **Horarios:**\n{lugar['horarios']}")
                    with col_inf3:
                        st.write(f"🚌 **Cómo llegar:**\n{lugar['como_llegar']}")
                    
                    # Botonera de acción
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        q_map = urllib.parse.quote(f"{lugar['nombre']} {ciudad_input}")
                        st.link_button("🗺️ Cómo llegar (Mapa)", f"https://www.google.com/maps/search/{q_map}", use_container_width=True)
                    with c_btn2:
                        if lugar['ticket_link'] != "none":
                            st.link_button("🎟️ Comprar Entradas", lugar['ticket_link'], use_container_width=True, type="primary")

st.divider()
st.caption("SOS Passport © 2026")