import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime
import urllib.parse

# 1. CONFIGURACIÓN LIMPIA
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de conexión. Revisa tus Secrets.")
    st.stop()

# 2. INTERFAZ DIRECTA
st.title("🆘 SOS Passport AI")
st.write("Tu asistente integral de viaje. Sin vueltas.")

col1, col2 = st.columns(2)
with col1:
    nacionalidad = st.text_input("🌎 Tu Nacionalidad", value="Argentina")
with col2:
    ciudad_input = st.text_input("📍 Ciudad de destino", placeholder="Ej: Río de Janeiro, Brasil")

st.markdown("---")

if ciudad_input and nacionalidad:
    search_key = f"{ciudad_input.lower()}-{nacionalidad.lower()}"
    
    if st.button("GENERAR MI GUÍA"):
        guia_final = None
        
        # BUSCAR EN BASE DE DATOS
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data:
                guia_final = query.data[0]['datos_jsonb']
                st.info("⚡ Cargando datos guardados...")
        except:
            pass

        # GENERAR SI NO EXISTE
        if not guia_final:
            with st.spinner("Construyendo tu guía estratégica..."):
                prompt = f"""
                Genera una guía de asistencia y turismo para un {nacionalidad} en {ciudad_input}.
                Debes incluir obligatoriamente 10 puntos de interés destacados.
                
                Responde en JSON:
                {{
                    "consulado": "Info del consulado",
                    "emergencia_salud": "Hospital recomendado y contacto",
                    "puntos_interes": [
                        {{
                            "nombre": "Nombre del lugar",
                            "resenia": "Descripción breve y atractiva",
                            "ranking": "⭐ (1 al 5)",
                            "horarios": "Horas de apertura",
                            "tip": "Consejo clave"
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

        # 3. VISUALIZACIÓN
        if guia_final:
            st.header(f"📍 Destino: {ciudad_input.title()}")
            
            # Bloque de Seguridad (Consulado y Salud)
            c1, c2 = st.columns(2)
            with c1:
                with st.container(border=True):
                    st.subheader("🏛️ Consulado")
                    st.write(guia_final.get('consulado'))
            with c2:
                with st.container(border=True):
                    st.subheader("🏥 Salud y Emergencias")
                    st.write(guia_final.get('emergencia_salud'))

            st.divider()
            st.subheader("🌟 Top 10 Lugares Imperdibles")

            # Lista de puntos de interés
            for p in guia_final.get('puntos_interes', []):
                with st.container(border=True):
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"### {p['nombre']} {p.get('ranking', '')}")
                        st.write(p['resenia'])
                        st.caption(f"💡 **Tip:** {p.get('tip')}")
                    with col_btn:
                        st.write(f"⏰ {p['horarios']}")
                        q = urllib.parse.quote(f"{p['nombre']} {ciudad_input}")
                        st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/{q}")

st.divider()
st.caption("SOS Passport © 2026")