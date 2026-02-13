import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0faff 0%, #ffffff 100%); color: #2c3e50; }
    .main-title { color: #00838f; font-weight: 800; font-size: 3rem !important; }
    .punto-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 10px 30px rgba(0, 131, 143, 0.1);
        margin-bottom: 25px;
        border-top: 8px solid #00acc1;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES (Con manejo de errores)
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Faltan configurar los Secrets en Streamlit Cloud.")
    st.stop()

# 3. HOME
st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía de confianza para explorar y descansar.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Madrid")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR DESTINO!", use_container_width=True):
    if dest and nac:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Diseñando tu viaje..."):
                prompt = f"Genera una guía alegre para un {nac} en {dest} en {lang}. Incluye 8 puntos de interés. Responde JSON con campos 'emergencia' (texto) y 'puntos' (lista con nombre, resenia, ranking, horario, precio, link_ticket)."
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.divider()
            # Emergencias
            em = guia.get('emergencia', "Consultar en destino")
            st.info(f"🛡️ **Información de Seguridad:** {str(em)}")

            st.write("---")
            # Puntos de interés
            puntos = guia.get('puntos', [])
            for i, p in enumerate(puntos):
                nombre_lugar = str(p.get('nombre', 'Lugar Turístico')) # Forzamos a que sea texto
                
                st.markdown(f"""
                <div class="punto-card">
                    <h2 style="margin:0; color:#00838f;">{nombre_lugar} {p.get('ranking', '')}</h2>
                    <p style="margin-top:10px;">{p.get('resenia', '')}</p>
                    <p style="font-size:0.9rem; color:#666;"><b>⏰ Horario:</b> {p.get('horario')} | <b>💰 Precio:</b> {p.get('precio')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                c_map, c_tix = st.columns(2)
                with c_map:
                    # El 'str()' y el quote blindan el error dc301b
                    q_url = urllib.parse.quote(f"{nombre_lugar} {dest}")
                    st.link_button("🗺️ VER MAPA", f"https://www.google.com/maps/search/?api=1&query={q_url}", use_container_width=True, key=f"m_{i}")
                with c_tix:
                    link = p.get('link_ticket', 'No requiere')
                    if "http" in str(link):
                        st.link_button("🎟️ TICKETS", str(link), use_container_width=True, key=f"t_{i}")
                    else:
                        st.button(f"✨ {link}", disabled=True, use_container_width=True, key=f"i_{i}")