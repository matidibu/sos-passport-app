import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO DINÁMICO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

# Lógica de color de fondo dinámica
bg_color = "#f0faff" 
if "dest" in st.session_state:
    d = st.session_state.dest.lower()
    if any(x in d for x in ["cabo", "africa", "safari"]): bg_color = "#fff8e1" # Arena/Sol
    elif any(x in d for x in ["paris", "francia", "roma"]): bg_color = "#f5f5f5" # Piedra/Elegante
    elif any(x in d for x in ["new york", "tokyo", "londres"]): bg_color = "#eceff1" # Urbano

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: all 0.8s ease; }}
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
        border-bottom: 6px solid #00acc1; transition: 0.3s;
    }}
    .punto-card:hover {{ transform: translateY(-5px); }}
    .info-relevante-box {{
        background: #102027; color: #ffffff; padding: 40px;
        border-radius: 25px; margin-top: 50px; border-top: 8px solid #ff9800;
    }}
    .btn-action {{
        display: inline-block; padding: 12px 20px; border-radius: 12px;
        text-decoration: none; font-weight: 700; margin-top: 15px; margin-right: 10px; text-align: center;
    }}
    .btn-map {{ background: #00acc1; color: white !important; }}
    .btn-tkt {{ background: #ff9800; color: white !important; }}
    .grid-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de configuración de Secrets.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu inteligencia de viaje en tiempo real</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Ciudad del Cabo, Sudáfrica")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest:
        st.session_state.dest = dest
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Analizando {dest} para vos..."):
                prompt = f"""Genera una guía profesional para un viajero {nac} en {dest} en {lang}.
                IMPORTANTE: Responde EXCLUSIVAMENTE un JSON válido:
                {{
                    "resenia_corta": "info",
                    "puntos": [{"nombre": "..", "resenia": "..", "horario": "..", "precio": "..", "url_ticket": ".."}],
                    "finanzas": {{"cambio_local_usd": "1 USD = ?", "cambio_nacional_usd": "1 USD = ?"}},
                    "clima": "info 7 días", "consulado": "info", "hospital": "info"
                }}"""
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. FOTO Y RESEÑA
            st.image(f"https://loremflickr.com/1200/500/{urllib.parse.quote(dest)},city/all", use_container_width=True)
            st.markdown(f'<div class="resenia-box"><h2>Sobre {dest.title()}</h2><p style="font-size:1.1rem; line-height:1.6;">{guia.get("resenia_corta")}</p></div>', unsafe_allow_html=True)

            # B. IMPERDIBLES
            st.subheader(f"📍 Imperdibles Seleccionados")
            puntos = guia.get('puntos', [])
            for p in puntos:
                n = p.get('nombre', 'Lugar')
                t_url = p.get('url_ticket', '')
                btn_tkt = ""
                if "gratis" not in str(p.get('precio')).lower():
                    if "http" not in str(t_url): t_url = f"https://www.google.com/search?q=tickets+official+{urllib.parse.quote(n)}+{urllib.parse.quote(dest)}"
                    btn_tkt = f'<a href="{t_url}" target="_blank" class="btn-action btn-tkt">🎟️ TICKETS</a>'
                
                q_map = urllib.parse.quote(f"{n} {dest}")
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n}</h3>
                    <p>{p.get('resenia')}</p>
                    <span style="background:#e0f7fa; padding:5px 10px; border-radius:8px; font-size:0.8rem; font-weight:bold; color:#006064;">⏰ {p.get('horario')}</span>
                    <span style="background:#f1f8e9; padding:5px 10px; border-radius:8px; font-size:0.8rem; font-weight:bold; color:#2e7d32; margin-left:10px;">💰 {p.get('precio', 'Variable')}</span>
                    <br>
                    <a href="https://www.google.com/maps/search/?api=1&query={q_map}" target="_blank" class="btn-action btn-map">🗺️ MAPA</a>
                    {btn_tkt}
                </div>
                """, unsafe_allow_html=True)

            # C. INFORMACIÓN RELEVANTE
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#00acc1; margin-top:0;">📊 Información Relevante</h2>
                <div class="grid-info">
                    <div>
                        <h4 style="color:#ff9800;">💰 Moneda & Cambio</h4>
                        <p><b>En {dest}:</b> {guia.get('finanzas', {}).get('cambio_local_usd', 'Consultar')}</p>
                        <p><b>Tu moneda ({nac}):</b> {guia.get('finanzas', {}).get('cambio_nacional_usd', 'Consultar')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">☀️ Clima Próximos 7 Días</h4>
                        <p>{guia.get('clima', 'No disponible en este momento.')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">🏛️ Seguridad & Salud</h4>
                        <p><b>Consulado:</b> {guia.get('consulado')}</p>
                        <p><b>Hospital:</b> {guia.get('hospital')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)