import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime, timedelta
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de conexión. Revisa los Secrets.")
    st.stop()

# 2. INTERFAZ
st.title("🆘 SOS Passport AI - Experiencia Integral")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    nacionalidad = st.text_input("🌎 Nacionalidad", value="Argentina")
with col2:
    ciudad_input = st.text_input("📍 Ciudad de destino", placeholder="Ej: Río de Janeiro")
with col3:
    tipo_experiencia = st.multiselect(
        "🎭 ¿Qué buscas?", 
        ["Educación", "Entretenimiento", "Relax", "Gastronomía", "Aventura"],
        default=["Educación", "Entretenimiento"]
    )

st.markdown("---")

if ciudad_input and nacionalidad:
    # La clave ahora incluye el tipo de experiencia para que la base de datos sea específica
    search_key = f"{ciudad_input.lower()}-{nacionalidad.lower()}"
    
    if st.button("Generar Guía Premium"):
        guia_final = None
        
        # A. BUSCAR EN BASE DE DATOS
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data:
                guia_final = query.data[0]['datos_jsonb']
                st.info("💡 Recuperando guía completa de la base de datos...")
        except:
            pass

        # B. SI NO EXISTE, GENERAR CON IA (MÁS POTENTE)
        if not guia_final:
            with st.spinner("Construyendo una experiencia integral..."):
                prompt = f"""
                Genera una guía turística y técnica EXHAUSTIVA para un {nacionalidad} en {ciudad_input}.
                Debes incluir al menos 10 puntos de interés variados.
                
                Responde ÚNICAMENTE con un objeto JSON:
                {{
                    "consulado": "Info detallada del consulado",
                    "hospital_nombre": "Nombre hospital principal",
                    "hospital_info": "Dirección y contacto",
                    "puntos_interes": [
                        {{
                            "nombre": "Nombre del lugar",
                            "categoria": "Educación, Entretenimiento, Relax, Gastronomía o Aventura",
                            "reseña": "Descripción atractiva",
                            "ranking": "⭐ (del 1 al 5)",
                            "horarios": "Info de apertura",
                            "tip_viajero": "Un consejo único para este lugar"
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
                
                # Guardar
                supabase.table("guias").upsert({
                    "clave_busqueda": search_key,
                    "datos_jsonb": guia_final,
                    "created_at": datetime.now().isoformat()
                }).execute()

        # 3. MOSTRAR RESULTADOS FILTRADOS
        if guia_final:
            # Sección Emergencias
            st.subheader("🚨 Información Esencial")
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"🏛️ **Consulado:** {guia_final['consulado']}")
            with c2:
                st.error(f"🏥 **Hospital:** {guia_final['hospital_nombre']}\n\n{guia_final['hospital_info']}")

            st.divider()
            st.subheader(f"📍 Lo mejor de {ciudad_input.title()}")

            # Filtrado por la elección del usuario
            puntos = guia_final.get('puntos_interes', [])
            
            # Mostramos los puntos según la categoría elegida
            for punto in puntos:
                if not tipo_experiencia or punto['categoria'] in tipo_experiencia:
                    with st.container(border=True):
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"### {punto['nombre']} {punto['ranking']}")
                            st.caption(f"Categoría: {punto['categoria']}")
                            st.write(punto['reseña'])
                            st.info(f"💡 **Tip:** {punto['tip_viajero']}")
                        with col_b:
                            st.write(f"⏰ {punto['horarios']}")
                            q = urllib.parse.quote(f"{punto['nombre']} {ciudad_input}")
                            st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/{q}")