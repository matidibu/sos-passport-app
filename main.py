import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime
import urllib.parse

# 1. ESTILO "CLARIDAD SOS"
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1e1e1e; }
    .main-title { color: #ff4b4b; font-weight: 900; font-size: 3rem !important; letter-spacing: -1px; }
    .punto-card {
        background: #fdfdfd;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #eee;
        border-left: 6px solid #ff4b4b;
        margin-bottom: 25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03);
    }
    .precio-tag { color: #2e7d32; font-weight: bold; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión.")
    st.stop()

# 3. INTERFAZ DE USUARIO
st.markdown('<h1 class="main-title">SOS PASSPORT</h1>', unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        nacionalidad = st.text_input("🌎 Nacionalidad", value="Argentina")
    with col2:
        ciudad_input = st.text_input("📍 Ciudad de destino", placeholder="Ej: Roma, Italia")
    with col3:
        # Reincorporamos el menú de idioma que pediste
        idioma = st.selectbox("🗣️ Idioma de la Guía", ["Español", "English", "Português", "Italiano", "Français"])

if st.button("GENERAR GUÍA INTEGRAL DE ASISTENCIA"):
    if ciudad_input and nacionalidad:
        search_key = f"{ciudad_input.lower().strip()}-{nacionalidad.lower().strip()}-{idioma.lower()}"
        guia_final = None
        
        # BUSCAR EN DB
        res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
        if res.data:
            guia_final = res.data[0]['datos_jsonb']
        
        # GENERAR CON IA (PIDIENDO TODA LA INFO DETALLADA)
        if not guia_final:
            with st.spinner(f"Generando protocolo en {idioma}..."):
                prompt = f"""
                Genera una guía de asistencia para un {nacionalidad} en {ciudad_input} en idioma {idioma}.
                Incluye 12 puntos de interés.
                Responde estrictamente en JSON con:
                {{
                    "emergencia": {{"consulado": "info", "hospital": "nombre y dir"}},
                    "puntos": [
                        {{
                            "nombre": "Nombre del lugar",
                            "resenia": "Reseña histórica y turística atractiva",
                            "ranking": "⭐⭐⭐⭐⭐",
                            "horario": "Horarios detallados",
                            "precio": "Costo de entrada aproximado en moneda local",
                            "link_entradas": "URL oficial o de ticketera (o 'No requiere')",
                            "ubicacion": "Dirección o referencia"
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

        # 4. DESPLIEGUE DE LA GUÍA
        if guia_final:
            st.divider()
            
            # Bloque de Emergencia
            st.subheader("🚨 Información de Seguridad")
            em = guia_final.get('emergencia', {})
            c1, c2 = st.columns(2)
            with c1: st.info(f"🏛️ **Consulado:** {em.get('consulado')}")
            with c2: st.error(f"🏥 **Hospital:** {em.get('hospital')}")

            st.write("---")
            st.subheader(f"📍 Explorando {ciudad_input.title()}")
            
            # Carrusel visual
            st.image([f"https://source.unsplash.com/1200x400/?{ciudad_input}", 
                      f"https://source.unsplash.com/1200x400/?{ciudad_input},monument"], use_container_width=True)

            # Listado Exhaustivo de Puntos
            for p in guia_final.get('puntos', []):
                with st.container():
                    st.markdown(f"""
                    <div class="punto-card">
                        <div style="display:flex; justify-content:space-between;">
                            <h3 style="margin:0; color:#ff4b4b;">{p.get('nombre')}</h3>
                            <span style="font-size:1.2rem;">{p.get('ranking')}</span>
                        </div>
                        <p style="margin-top:10px; font-size:1.1rem; line-height:1.6;">{p.get('resenia')}</p>
                        <hr style="border:0.5px solid #eee;">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <p><b>⏰ Horario:</b> {p.get('horario')}</p>
                            <p class="precio-tag"><b>💰 Precio:</b> {p.get('precio')}</p>
                        </div>
                        <p style="color:#666; font-size:0.9rem;">📍 {p.get('ubicacion')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botones de Acción: Mapa y Entradas
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        q_map = urllib.parse.quote(f"{p['nombre']} {ciudad_input}")
                        st.link_button(f"🗺️ VER MAPA", f"https://www.google.com/maps/search/{q_map}", use_container_width=True)
                    with btn_col2:
                        link = p.get('link_entradas', 'No requiere')
                        if "http" in link:
                            st.link_button(f"🎟️ COMPRAR ENTRADAS", link, use_container_width=True)
                        else:
                            st.button(f"🏷️ {link}", disabled=True, use_container_width=True)