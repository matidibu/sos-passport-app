import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE Y LIMPIO (Sin fondos rojos)
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f0faff; }
    .main-title { color: #00838f; font-weight: 800; font-size: 3rem !important; margin-bottom: 0; }
    .punto-card {
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px; border-left: 8px solid #00acc1;
    }
    .info-tag { background: #e0f7fa; padding: 5px 10px; border-radius: 8px; font-size: 0.85rem; color: #006064; font-weight: bold; margin-right: 5px; }
    .custom-btn {
        display: inline-block; padding: 10px 20px; background-color: #00838f; color: white !important;
        text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 0.9rem;
        margin-top: 10px; margin-right: 10px; text-align: center; width: 45%;
    }
    .btn-tkt { background-color: #ff9800; }
    .header-box { 
        background: #00acc1; padding: 40px; border-radius: 20px; 
        color: white; text-align: center; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en Secrets.")
    st.stop()

# 3. INTERFAZ
with st.container():
    st.markdown('<div class="header-box"><h1>SOS Passport 🏖️</h1><p>Tu guía de confianza para explorar el mundo</p></div>', unsafe_allow_html=True)

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 ¿A dónde vas?", placeholder="Ej: París, Francia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR DESTINO!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Buscando información actualizada..."):
                prompt = f"Genera guía JSON para {nac} en {dest} en {lang}: consulado, hospital y puntos (nombre, resenia, horario, precio, url_ticket)."
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # 4. SEGURIDAD
            st.subheader("🛡️ Seguridad y Salud")
            s1, s2 = st.columns(2)
            s1.info(f"🏛️ **Consulado:**\n\n{guia.get('consulado')}")
            s2.success(f"🏥 **Hospital:**\n\n{guia.get('hospital')}")

            st.divider()
            st.subheader(f"📍 Imperdibles en {dest}")
            
            # 5. RENDERIZADO DE PUNTOS (SIN ERRORES)
            puntos = guia.get('puntos', [])
            for p in puntos:
                nombre = p.get('nombre', 'Lugar')
                t_url = p.get('url_ticket', '')
                if "http" not in str(t_url):
                    t_url = f"https://www.google.com/search?q=tickets+oficial+{urllib.parse.quote(nombre)}+{urllib.parse.quote(dest)}"
                
                q_map = urllib.parse.quote(f"{nombre} {dest}")
                
                # Renderizamos TODO en un solo bloque HTML para evitar que Streamlit se trabe
                st.markdown(f"""
                <div class="punto-card">
                    <h3 style="margin:0; color:#00838f;">{nombre}</h3>
                    <p style="margin:10px 0; color:#444;">{p.get('resenia', '')}</p>
                    <div style="margin-bottom:15px;">
                        <span class="info-tag">⏰ {p.get('horario')}</span>
                        <span class="info-tag">💰 {p.get('precio')}</span>
                    </div>
                    <a href="https://www.google.com/maps/search/?api=1&query={q_map}" target="_blank" class="custom-btn">🗺️ VER MAPA</a>
                    <a href="{t_url}" target="_blank" class="custom-btn btn-tkt">🎟️ TICKETS</a>
                </div>
                """, unsafe_allow_html=True)