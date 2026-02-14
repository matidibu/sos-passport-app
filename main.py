import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json

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
    .info-tag { background: #e0f7fa; padding: 5px 10px; border-radius: 10px; font-size: 0.85rem; margin-right: 5px; color: #006064; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de configuración. Verificá tus Secrets.")
    st.stop()

st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía de confianza para explorar y descansar.")

# 3. INTERFAZ
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Londres, Reino Unido")
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
                Responde ÚNICAMENTE un JSON con esta estructura:
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
            st.subheader("🛡️ Seguridad y Salud")
            cs1, cs2 = st.columns(2)
            cs1.info(f"🏛️ **Consulado:** {guia.get('consulado', 'Consultar online')}")
            cs2.success(f"🏥 **Hospital:** {guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            puntos = guia.get('puntos', [])
            for i, p in enumerate(puntos):
                # Extraemos los datos de forma segura
                nombre_sitio = str(p.get('nombre', 'Lugar Turístico'))
                resenia_sitio = str(p.get('resenia', p.get('reseña', 'Sin descripción')))
                horario_sitio = str(p.get('horario', 'Consultar'))
                precio_sitio = str(p.get('precio', 'Variable'))
                
                # CREACIÓN DE LA TARJETA
                st.markdown(f"""
                <div class="punto-card">
                    <h2 style="margin:0; color:#00838f;">{nombre_sitio}</h2>
                    <p style="margin:15px 0; font-size:1.1rem; color:#444;">{resenia_sitio}</p>
                    <span class="info-tag">⏰ {horario_sitio}</span>
                    <span class="info-tag">💰 {precio_sitio}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # BOTONES (REDISEÑADOS PARA EVITAR TYPEERROR)
                bm, bt = st.columns(2)
                with bm:
                    # Usamos una búsqueda simple en Google Maps
                    link_google = f"https://www.google.com/maps/search/{nombre_sitio.replace(' ', '+')}+{dest.replace(' ', '+')}"
                    st.link_button("🗺️ VER EN MAPA", link_google, use_container_width=True, key=f"m_btn_{i}")
                with bt:
                    st.button("✨ RECOMENDADO", disabled=True, use_container_width=True, key=f"r_btn_{i}")