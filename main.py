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
    .info-tag { background: #e0f7fa; padding: 5px 10px; border-radius: 10px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Revisá la configuración de tus Secrets.")
    st.stop()

st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía de confianza para explorar y descansar.")

# 3. INTERFAZ DE BÚSQUEDA
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Rio de Janeiro")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Buscando los mejores lugares..."):
                prompt = f"""Genera una guía de viaje para un {nac} en {dest} en {lang}. 
                Responde EXCLUSIVAMENTE un JSON con esta estructura:
                {{
                    "consulado": "info",
                    "hospital": "info",
                    "puntos": [{{ "nombre": "Lugar", "resenia": "Breve descripción", "horario": "Info", "precio": "Info" }}]
                }}"""
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.divider()
            # SECCIÓN SEGURIDAD (Foto e7fa81 - OK)
            st.subheader("🛡️ Seguridad y Salud")
            cs1, cs2 = st.columns(2)
            cs1.info(f"🏛️ **Consulado:** {guia.get('consulado', 'Consultar online')}")
            cs2.success(f"🏥 **Hospital:** {guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            # Buscador de puntos (Flexible)
            puntos = guia.get('puntos', [])
            if not puntos:
                for v in guia.values():
                    if isinstance(v, list):
                        puntos = v
                        break

            for i, p in enumerate(puntos):
                nombre_lugar = str(p.get('nombre', 'Lugar Turístico'))
                st.markdown(f"""
                <div class="punto-card">
                    <h2 style="margin:0; color:#00838f;">{nombre_lugar}</h2>
                    <p style="font-size:1.1rem; margin:10px 0;">{p.get('resenia', p.get('reseña', ''))}</p>
                    <span class="info-tag">⏰ {p.get('horario', 'N/A')}</span>
                    <span class="info-tag">💰 {p.get('precio', 'N/A')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # BOTONES (Aquí corregimos el error de la foto e8025f)
                b_map, b_extra = st.columns(2)
                with b_map:
                    # Usamos quote para asegurar que el link sea válido
                    query = urllib.parse.quote(f"{nombre_lugar} {dest}")
                    st.link_button("🗺️ VER EN MAPA", f"https://www.google.com/maps/search/?api=1&query={query}", use_container_width=True, key=f"m_{i}")
                with b_extra:
                    st.button("✨ RECOMENDADO", disabled=True, use_container_width=True, key=f"r_{i}")