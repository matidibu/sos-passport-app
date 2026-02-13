import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE Y LIMPIO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0faff 0%, #ffffff 100%); }
    .main-title { color: #00838f; font-weight: 800; font-size: 3rem !important; margin-bottom: 0; }
    .punto-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0px 10px 30px rgba(0, 131, 143, 0.1);
        margin-bottom: 25px; border-top: 8px solid #00acc1;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de configuración. Revisá tus Secrets.")
    st.stop()

# 3. INTERFAZ
st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía de confianza para explorar y descansar.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Rio de Janeiro")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest:
        # Usamos una clave de búsqueda que incluya nacionalidad para que la info sea específica
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Buscando los mejores rincones..."):
                # Prompt reforzado para que no falle el JSON
                prompt = f"""Genera una guía de viaje vibrante para un {nac} en {dest} en {lang}. 
                IMPORTANTE: Responde ÚNICAMENTE un objeto JSON con esta estructura exacta:
                {{
                    "consulado": "Info del consulado o embajada",
                    "hospital": "Nombre y dirección de hospital recomendado",
                    "puntos": [
                        {{"nombre": "Lugar", "resenia": "Reseña corta", "ranking": "⭐⭐⭐⭐⭐", "horario": "Info", "precio": "Info", "link": "No requiere"}}
                    ]
                }}
                Crea entre 7 y 9 puntos de interés."""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.divider()
            # SECCIÓN SEGURIDAD
            st.subheader("🛡️ Seguridad y Salud")
            col_s1, col_s2 = st.columns(2)
            col_s1.info(f"🏛️ **Consulado:** {guia.get('consulado', 'Consultar online')}")
            col_s2.success(f"🏥 **Hospital:** {guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            # Lógica inteligente para encontrar la lista de puntos
            puntos = guia.get('puntos', [])
            
            if not puntos:
                st.warning("Hacé clic de nuevo en el botón para refrescar la búsqueda.")
            
            for i, p in enumerate(puntos):
                nombre_lugar = str(p.get('nombre', 'Lugar Turístico'))
                st.markdown(f"""
                <div class="punto-card">
                    <h2 style="margin:0; color:#00838f;">{nombre_lugar}</h2>
                    <p style="font-size:1.1rem; margin-top:10px;">{p.get('resenia', p.get('reseña', ''))}</p>
                    <p><b>⏰ Horario:</b> {p.get('horario')} | <b>💰 Precio:</b> {p.get('precio')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # BOTONES (Blindados contra el TypeError)
                bm, bt = st.columns(2)
                with bm:
                    q_safe = urllib.parse.quote(f"{nombre_lugar} {dest}")
                    st.link_button("🗺️ VER MAPA", f"https://www.google.com/maps/search/?api=1&query={q_safe}", use_container_width=True, key=f"map_{i}")
                with bt:
                    link = p.get('link', p.get('link_ticket', 'No requiere'))
                    if "http" in str(link):
                        st.link_button("🎟️ TICKETS", link, use_container_width=True, key=f"tix_{i}")
                    else:
                        st.button(f"✨ {link}", disabled=True, use_container_width=True, key=f"info_{i}")