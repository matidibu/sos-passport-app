import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime
import urllib.parse

# 1. ESTILO "MINIMAL SOS" (CSS)
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #ffffff; }
    
    /* Título con identidad única */
    .main-title { 
        color: #ff4b4b; 
        font-family: 'Inter', sans-serif; 
        font-weight: 900; 
        font-size: 4rem !important;
        letter-spacing: -2px;
        margin-bottom: 0px;
    }
    
    /* Tarjetas de información */
    .info-card {
        background: #111418;
        border-radius: 12px;
        padding: 25px;
        border-left: 6px solid #ff4b4b;
        margin-bottom: 20px;
    }
    
    /* Botón de acción masivo */
    .stButton>button {
        width: 100%;
        background: #ff4b4b;
        color: white;
        border: none;
        padding: 20px;
        font-size: 1.2rem;
        font-weight: bold;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #d43f3f; box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de sistema.")
    st.stop()

# 3. INTERFAZ DIRECTA
st.markdown('<h1 class="main-title">SOS PASSPORT</h1>', unsafe_allow_html=True)
st.write("### ASISTENCIA GLOBAL DE EMERGENCIA")

st.markdown("---")

col_in1, col_in2 = st.columns(2)
with col_in1:
    ciudad_input = st.text_input("📍 DESTINO", placeholder="Ej: Río de Janeiro")
with col_in2:
    nacionalidad = st.text_input("🌎 NACIONALIDAD", value="Argentina")

# Botón central único
if st.button("GENERAR PROTOCOLO DE ASISTENCIA"):
    if ciudad_input:
        search_key = f"{ciudad_input.lower().strip()}-{nacionalidad.lower().strip()}"
        guia_final = None
        
        # BUSCAR EN DB
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data:
                guia_final = query.data[0]['datos_jsonb']
        except: pass
        
        # GENERAR CON IA SI NO EXISTE (PIDIENDO 10 PUNTOS POR DEFECTO)
        if not guia_final:
            with st.spinner("CONECTANDO CON RED DE EMERGENCIA..."):
                prompt = f"""
                Genera una guía de seguridad y turismo para un {nacionalidad} en {ciudad_input}.
                Idioma: Español.
                Incluye: consulado, hospital de referencia y 10 puntos de interés con ranking (1-5 estrellas).
                Responde solo JSON. Campos: 'consulado', 'hospital', 'puntos' (nombre, descripcion, ranking, tip).
                """
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia_final = json.loads(completion.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia_final}).execute()

        # 4. DESPLIEGUE DE LA INFORMACIÓN
        if guia_final:
            st.divider()
            
            # Cabecera de Emergencia
            st.error(f"🚨 PROTOCOLO ACTIVO: {ciudad_input.upper()}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**🏛️ CONSULADO {nacionalidad.upper()}**\n\n{guia_final.get('consulado')}")
            with c2:
                st.markdown(f"**🏥 HOSPITAL RECOMENDADO**\n\n{guia_final.get('hospital')}")

            st.write("---")
            st.subheader("📍 PUNTOS ESTRATÉGICOS Y RANKING")

            # Carrusel de fotos (ahora arriba de los puntos para que sea visualmente impactante)
            st.image([f"https://source.unsplash.com/1200x500/?{ciudad_input}", 
                      f"https://source.unsplash.com/1200x500/?{ciudad_input},landmark"], 
                     use_container_width=True)

            # Listado de los 10 puntos sin filtros, directo
            for p in guia_final.get('puntos', []):
                nombre = p.get('nombre', 'Lugar')
                # Arreglo de seguridad para evitar el error de la 'ñ'
                desc = p.get('descripcion', p.get('reseña', p.get('resenia', 'Info no disponible')))
                ranking = p.get('ranking', '⭐⭐⭐⭐')
                tip = p.get('tip', 'Recomendado.')

                st.markdown(f"""
                <div class="info-card">
                    <div style="display:flex; justify-content:space-between;">
                        <h3 style="margin:0; color:#ff4b4b;">{nombre}</h3>
                        <span>{ranking}</span>
                    </div>
                    <p style="margin-top:10px; font-size:1.1rem;">{desc}</p>
                    <p style="color:#888; font-size:0.9rem;"><b>💡 TIP SOS:</b> {tip}</p>
                </div>
                """, unsafe_allow_html=True)
                
                q_map = urllib.parse.quote(f"{nombre} {ciudad_input}")
                st.link_button(f"🗺️ MAPA: {nombre.upper()}", f"https://www.google.com/maps/search/{q_map}")