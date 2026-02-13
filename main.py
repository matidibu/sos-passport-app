import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime, timedelta
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

# 2. CONEXIONES (Asegurate de que estos nombres coincidan con tus Secrets)
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de conexión. Verifica tus Secrets en Streamlit.")
    st.stop()

# 3. INTERFAZ DE USUARIO
st.title("🆘 SOS Passport AI")
st.markdown("### Tu guía inteligente de asistencia al viajero")

col_pref1, col_pref2 = st.columns(2)
with col_pref1:
    nacionalidad = st.text_input("🌎 Tu Nacionalidad", placeholder="Ej: Argentina")
with col_pref2:
    idioma = st.selectbox("🗣️ Idioma de la guía", ["Español", "English", "Português", "Français"])

st.markdown("---")

# 4. BUSCADOR
ciudad_input = st.text_input("📍 Ciudad de destino", placeholder="Ej: Roma, Italia")

if ciudad_input and nacionalidad:
    # Clave única para la base de datos (todo en minúsculas para evitar duplicados)
    search_key = f"{ciudad_input.lower()}-{nacionalidad.lower()}-{idioma.lower()}".strip()
    
    if st.button("Generar Guía Integral"):
        guia_final = None
        
        # --- PASO A: BUSCAR EN SUPABASE ---
        try:
            # Buscamos si ya existe esta guía
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            
            if query.data and len(query.data) > 0:
                # Verificamos si la guía tiene menos de 30 días
                fecha_creacion = datetime.fromisoformat(query.data[0]['created_at'].replace('Z', '+00:00'))
                if datetime.now(fecha_creacion.tzinfo) - fecha_creacion < timedelta(days=30):
                    guia_final = query.data[0]['datos_jsonb'] # <--- USAMOS EL NOMBRE DE TU FOTO
                    st.info("⚡ Información recuperada de la base de datos (Ahorro de IA)")
        except Exception as e:
            st.warning(f"Aviso: No se pudo leer la base de datos, consultando a la IA directamente...")

        # --- PASO B: SI NO ESTÁ EN LA BASE, PEDIR A GROQ ---
        if not guia_final:
            with st.spinner(f"Investigando sobre {ciudad_input} para un ciudadano {nacionalidad}..."):
                try:
                    prompt = f"""
                    Genera una guía de asistencia técnica y turística para un ciudadano {nacionalidad} que se encuentra en {ciudad_input}.
                    La respuesta DEBE ser un objeto JSON estrictamente formateado con el idioma {idioma}.
                    
                    Estructura del JSON:
                    {{
                        "consulado": "Dirección y contacto del consulado o embajada",
                        "hospital": "Nombre y dirección del hospital principal",
                        "hospital_nombre": "Solo el nombre del hospital para buscar en mapa",
                        "transporte_link": "URL de la web oficial de transporte",
                        "puntos_interes": [
                            {{
                                "nombre": "Nombre del lugar",
                                "reseña": "Breve descripción",
                                "precios": "Costos estimados",
                                "ticket_link": "Link de compra o 'none'",
                                "horarios": "Horas de apertura",
                                "como_llegar": "Línea de metro o bus"
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
                    
                    # --- PASO C: GUARDAR EN SUPABASE PARA EL FUTURO ---
                    # Nota: Usamos datos_jsonb porque es como se llama en tu tabla
                    supabase.table("guias").upsert({
                        "clave_busqueda": search_key,
                        "datos_jsonb": guia_final,
                        "created_at": datetime.now().isoformat()
                    }).execute()
                    st.success("✅ Guía generada y guardada en la base de datos.")
                    
                except Exception as e:
                    st.error(f"Hubo un error con la IA: {e}")

        # --- 5. MOSTRAR RESULTADOS SI TENEMOS GUÍA ---
        if guia_final:
            st.divider()
            st.header(f"📍 Guía SOS: {ciudad_input.title()}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.container(border=True):
                    st.subheader(f"🏛️ Consulado de {nacionalidad}")
                    st.write(guia_final.get('consulado', 'No disponible'))
                    q_cons = urllib.parse.quote(f"consulado de {nacionalidad} en {ciudad_input}")
                    st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/?api=1&query={q_cons}")

            with col2:
                with st.container(border=True):
                    st.subheader("🏥 Hospital Recomendado")
                    st.write(guia_final.get('hospital', 'No disponible'))
                    q_hosp = urllib.parse.quote(f"{guia_final.get('hospital_nombre', 'Hospital')} {ciudad_input}")
                    st.link_button("🚑 Emergencias Mapa", f"https://www.google.com/maps/search/?api=1&query={q_hosp}")

            st.subheader("🌟 Imperdibles y Logística")
            for lugar in guia_final.get('puntos_interes', []):
                with st.expander(f"📍 {lugar['nombre']}"):
                    st.write(lugar['reseña'])
                    c_l1, c_l2 = st.columns(2)
                    with c_l1:
                        st.write(f"💰 **Precios:** {lugar['precios']}")
                        st.write(f"⏰ **Horarios:** {lugar['horarios']}")
                    with c_l2:
                        st.write(f"🚌 **Cómo llegar:** {lugar['como_llegar']}")
                        if lugar['ticket_link'] != "none":
                            st.link_button("🎟️ Comprar Entradas", lugar['ticket_link'])
                    
                    q_lugar = urllib.parse.quote(f"{lugar['nombre']} {ciudad_input}")
                    st.link_button("🗺️ Ir al Mapa", f"https://www.google.com/maps/search/?api=1&query={q_lugar}")

st.divider()
st.caption("SOS Passport © 2026 - Tu asistente de viaje con IA")