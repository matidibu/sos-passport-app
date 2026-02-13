import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0faff 0%, #ffffff 100%); }
    .main-title { color: #00838f; font-weight: 800; font-size: 3rem !important; }
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
    st.error("Error de conexión. Revisá tus Secrets.")
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
        # Clave única por destino y nacionalidad
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Buscando los mejores lugares para vos..."):
                prompt = f"""Genera una guía de viaje para un {nac} en {dest} en {lang}. 
                Responde ÚNICAMENTE un JSON con:
                'consulado': 'info',
                'hospital': 'info',
                'lista_lugares': [{{'nombre': '..', 'resenia': '..', 'horario': '..', 'precio': '..'}}]"""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.divider()
            # SEGURIDAD (Lo que ya te funcionaba en la foto e7fa81)
            st.subheader("🛡️ Seguridad y Salud")
            col_s1, col_s2 = st.columns(2)
            col_s1.info(f"🏛️ **Consulado:** {guia.get('consulado', guia.get('consulado_info', 'Consultar online'))}")
            col_s2.success(f"🏥 **Hospital:** {guia.get('hospital', guia.get('hospital_info', 'Consultar online'))}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            # --- BUSCADOR INTELIGENTE DE PUNTOS ---
            # Buscamos cualquier lista que tenga el JSON de la IA
            puntos = []
            for clave in ['lista_lugares', 'puntos', 'lugares', 'atracciones', 'items']:
                if clave in guia and isinstance(guia[clave], list):
                    puntos = guia[clave]
                    break
            
            # Si no encontró ninguna de las anteriores, agarra la primera lista que vea
            if not puntos:
                for v in guia.values():
                    if isinstance(v, list):
                        puntos = v
                        break

            if puntos:
                for i, p in enumerate(puntos):
                    nombre = str(p.get('nombre', 'Lugar Turístico'))
                    st.markdown(f"""
                    <div class="punto-card">
                        <h2 style="margin:0; color:#00838f;">{nombre}</h2>
                        <p style="font-size:1.1rem; margin-top:10px;">{p.get('resenia', p.get('reseña', 'Sin descripción'))}</p>
                        <p><b>⏰ Horario:</b> {p.get('horario', 'No info')} | <b>💰 Precio:</b> {p.get('precio', 'No info')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    bm, bt = st.columns(2)
                    with bm:
                        q_url = urllib.parse.quote(f"{nombre} {dest}")
                        st.link_button("🗺️ VER MAPA", f"https://www.google.com/maps/search/{q_url}", use_container_width=True, key=f"m_{i}")
                    with bt:
                        st.button("✨ Sugerido", disabled=True, use_container_width=True, key=f"s_{i}")
            else:
                st.warning("No se encontraron puntos. Probá escribiendo el destino de nuevo.")