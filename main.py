import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO DINÁMICO SEGÚN DESTINO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

# Inicializar destino en sesión para el color
if "last_dest" not in st.session_state:
    st.session_state.last_dest = ""

bg_color = "#f0faff"
d = st.session_state.last_dest.lower()
if any(x in d for x in ["cabo", "africa", "safari", "egipto"]): bg_color = "#fff3e0" 
elif any(x in d for x in ["paris", "londres", "europa", "roma"]): bg_color = "#f5f5f5"
elif any(x in d for x in ["brasil", "caribe", "asia", "tailandia"]): bg_color = "#e8f5e9"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: background 0.8s ease; }}
    .header-container {{
        background: linear-gradient(90deg, #00838f, #00acc1);
        padding: 40px; border-radius: 25px; color: white; text-align: center; margin-bottom: 30px;
    }}
    .resenia-box {{
        background: white; padding: 30px; border-radius: 20px;
        margin-bottom: 30px; border-left: 10px solid #ff9800;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }}
    .punto-card {{
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-bottom: 6px solid #00acc1;
    }}
    .info-relevante-box {{
        background: #102027; color: #ffffff; padding: 40px;
        border-radius: 25px; margin-top: 50px; border-top: 8px solid #ff9800;
    }}
    .btn-action {{
        display: inline-block; padding: 12px 20px; border-radius: 12px;
        text-decoration: none; font-weight: 700; margin-top: 15px; margin-right: 10px;
    }}
    .btn-map {{ background: #00acc1; color: white !important; }}
    .btn-tkt {{ background: #ff9800; color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en Secrets.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu guía inteligente de viaje</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Ciudad del Cabo")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest:
        st.session_state.last_dest = dest
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Analizando {dest}..."):
                # PROMPT REFORZADO PARA EVITAR ERRORES DE JSON
                prompt = f"""Genera un JSON estrictamente válido para un viajero {nac} en {dest} en {lang}.
                Estructura:
                {{
                    "resenia_corta": "Texto breve",
                    "puntos": [{{ "nombre": "Lugar", "resenia": "Info", "horario": "Info", "precio": "Info", "url_ticket": "link" }}],
                    "finanzas": {{ "cambio_local_usd": "1 USD = ?", "cambio_nacional_usd": "1 USD = ?" }},
                    "clima": "Pronóstico 7 días",
                    "consulado": "info",
                    "hospital": "info"
                }}"""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                try:
                    guia = json.loads(chat.choices[0].message.content)
                    supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except Exception as e:
                    st.error("Hubo un problema al procesar los datos. Por favor, intenta de nuevo.")
                    st.stop()

        if guia:
            # A. FOTO Y RESEÑA
            img_dest = urllib.parse.quote(dest)
            st.image(f"https://loremflickr.com/1200/500/{img_dest},city/all", use_container_width=True)
            st.markdown(f'<div class="resenia-box"><h2>Sobre {dest}</h2><p>{guia.get("resenia_corta")}</p></div>', unsafe_allow_html=True)

            # B. PUNTOS IMPERDIBLES
            st.subheader(f"📍 Imperdibles en {dest}")
            puntos = guia.get('puntos', [])
            for p in puntos:
                n = p.get('nombre', 'Lugar')
                t_url = p.get('url_ticket', '')
                btn_tkt = ""
                if "gratis" not in str(p.get('precio', '')).lower():
                    if "http" not in str(t_url): t_url = f"https://www.google.com/search?q=tickets+official+{urllib.parse.quote(n)}"
                    btn_tkt = f'<a href="{t_url}" target="_blank" class="btn-action btn-tkt">🎟️ TICKETS</a>'
                
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n}</h3>
                    <p>{p.get('resenia', '')}</p>
                    <small>⏰ {p.get('horario')} | 💰 {p.get('precio')}</small><br>
                    <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(n + ' ' + dest)}" target="_blank" class="btn-action btn-map">🗺️ MAPA</a>
                    {btn_tkt}
                </div>
                """, unsafe_allow_html=True)

            # C. INFORMACIÓN RELEVANTE (ABAJO)
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#00acc1">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div>
                        <h4 style="color:#ff9800">💰 Moneda (USD)</h4>
                        <p><b>{dest}:</b> {guia.get('finanzas', {}).get('cambio_local_usd', 'Consultar')}</p>
                        <p><b>{nac}:</b> {guia.get('finanzas', {}).get('cambio_nacional_usd', 'Consultar')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800">☀️ Clima</h4>
                        <p>{guia.get('clima', 'No disponible')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800">🏛️ Consulado</h4>
                        <p>{guia.get('consulado', 'Ver online')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800">🏥 Hospital</h4>
                        <p>{guia.get('hospital', 'Ver online')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.rerun() # Para actualizar el color de fondo inmediatamente