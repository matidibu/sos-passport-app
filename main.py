import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime, timedelta
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA (Limpia y profesional)
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de conexión. Verifica tus Secrets.")
    st.stop()

# 3. INTERFAZ CLARA
st.title("🆘 SOS Passport AI")
st.markdown("#### Asistencia Integral al Viajero")

col1, col2 = st.columns(2)
with col1:
    nacionalidad = st.text_input("🌎 Tu Nacionalidad", value="Argentina")
with col2:
    ciudad_input = st.text_input("📍 Ciudad de destino", placeholder="Ej: Río de Janeiro, Brasil")

# Selector de experiencias (la función que querías sumar)
tipo_experiencia = st.multiselect(
    "🎭 Filtrar por tipo de experiencia:", 
    ["Educación", "Entretenimiento", "Relax", "Gastronomía", "Aventura"],
    default=["Educación", "Entretenimiento", "Relax", "Gastronomía", "Aventura"]
)

st.markdown("---")

if ciudad_input and nacionalidad:
    # Clave única
    search_key = f"{ciudad_input.lower()}-{nacionalidad.lower()}"
    
    if st.button("Generar Guía Completa"):
        guia_final = None
        
        # --- BUSCAR EN SUPABASE ---
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data and len(query.data) > 0:
                guia_final = query.data[0]['datos_jsonb']
                st.info("⚡ Información recuperada para optimizar tiempo.")
        except:
            pass

        # --- GENERAR CON IA SI NO EXISTE ---
        if not guia_final:
            with st.spinner(f"Analizando {ciudad_input} para ofrecerte una experiencia integral..."):
                prompt = f"""
                Genera una guía EXHAUSTIVA para un ciudadano {nacionalidad} en {ciudad_input}.
                Debes incluir al menos 10 puntos de interés variados.
                
                Responde ÚNICAMENTE con un objeto JSON:
                {{
                    "consulado": "Dirección y contacto del consulado",
                    "hospital_nombre": "Nombre del hospital principal",
                    "hospital_info": "Dirección y contacto de emergencias",
                    "puntos_interes": [
                        {{
                            "nombre": "Nombre del lugar",
                            "categoria": "Educación, Entretenimiento, Relax, Gastronomía o Aventura",
                            "reseña": "Descripción detallada",
                            "ranking": "⭐ (de 1 a 5)",
                            "horarios": "Horas de apertura",
                            "tip": "Consejo para el viajero"
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
                
                # Guardar en DB
                supabase.table("guias").upsert({
                    "clave_busqueda": search_key,
                    "datos_jsonb": guia_final,
                    "created_at": datetime.now().isoformat()
                }).execute()

        # --- 4. MOSTRAR RESULTADOS ---
        if guia_final:
            st.header(f"📍 Guía SOS: {ciudad_input.title()}")
            
            # Bloque de Emergencias
            with st.expander("🚨 INFORMACIÓN CRÍTICA (Consulado y Salud)", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("🏛️ Consulado")
                    st.write(guia_final.get('consulado'))
                with c2:
                    st.subheader("🏥 Emergencias Médicas")
                    st.write(f"**{guia_final.get('hospital_nombre')}**")
                    st.write(guia_final.get('hospital_info'))

            st.divider()

            # Puntos de Interés Filtrados
            puntos = guia_final.get('puntos_interes', [])
            
            # Buscador interno por nombre (opcional)
            busqueda_interna = st.text_input("🔍 Buscar lugar específico dentro de la guía:")

            for p in puntos:
                # Aplicamos filtros de categoría y búsqueda de texto
                if (not tipo_experiencia or p['categoria'] in tipo_experiencia) and \
                   (busqueda_interna.lower() in p['nombre'].lower()):
                    
                    with st.container(border=True):
                        col_txt, col_map = st.columns([3, 1])
                        with col_txt:
                            st.subheader(f"{p['nombre']} {p.get('ranking', '')}")
                            st.caption(f"Categoría: {p['categoria']}")
                            st.write(p['reseña'])
                            st.info(f"💡 **Tip:** {p.get('tip', 'Recomendado.')}")
                        with col_map:
                            st.write(f"⏰ {p['horarios']}")
                            q = urllib.parse.quote(f"{p['nombre']} {ciudad_input}")
                            st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/{q}")

st.divider()
st.caption("SOS Passport © 2026")