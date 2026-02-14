import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE Y DINÁMICO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

# Lógica de color de fondo según destino (Simplificada por keywords)
bg_color = "#e0f7fa" # Default (Turquesa claro)
if "dest" in st.session_state:
    d = st.session_state.dest.lower()
    if any(x in d for x in ["españa", "madrid", "barcelona", "méxico", "colombia"]): bg_color = "#fff3e0" # Cálido
    elif any(x in d for x in ["francia", "parís", "londres", "inglaterra", "italia"]): bg_color = "#f5f5f5" # Elegante
    elif any(x in d for x in ["brasil", "rio", "tailandia", "caribe"]): bg_color = "#e8f5e9" # Tropical

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: background 1s ease; }}
    .header-container {{
        background: linear-gradient(90deg, #00bcd4, #00acc1);
        padding: 40px; border-radius: 25px; color: white;
        text-align: center; margin-bottom: 30px;
    }}
    .resenia-box {{
        background: white; padding: 25px; border-radius: 20px;
        margin-bottom: 30px; border-left: 8px solid #ff9800;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
    }}
    .punto-card {{
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-bottom: 6px solid #00bcd4;
    }}
    .info-relevante-box {{
        background: #263238; color: #eceff1; padding: 30px;
        border-radius: 25px; margin-top: 50px;
    }}
    .btn-action {{
        display: inline-block; padding: 12px 20px; border-radius: 12px;
        text-decoration: none; font-weight: 700; margin-top: 15px; margin-right: 10px;
    }}
    .btn-map {{ background: #00bcd4; color: white !important; }}
    .btn-tkt {{ background: #ff9800; color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de configuración en Secrets.")
    st.stop()

# Header
st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Descubre el mundo con información en tiempo real</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ DE BÚSQUEDA
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Tu Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: París, Francia", key="dest_input")
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
            with st.spinner("Sincronizando fotos, clima y finanzas..."):
                prompt = f"""Genera una guía de viaje para un {nac} en {dest} en {lang}.
                Responde ÚNICAMENTE un JSON con:
                - "resenia_corta": "Un párrafo impactante sobre la ciudad",
                - "puntos": [{"nombre": "..", "resenia": "..", "horario": "..", "precio": "..", "url_ticket": ".."}],
                - "finanzas": {{"cambio_local_usd": "1 USD = ?", "cambio_nacional_usd": "1 USD = ?"}},
                - "clima": "Pronóstico de los próximos 7 días",
                - "consulado": "info", "hospital": "info"
                """
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. FOTO Y RESEÑA
            st.image(f"https://loremflickr.com/1200/500/{dest.replace(' ', '')},landscape/all", use_container_width=True)
            st.markdown(f'<div class="resenia-box"><h3>Sobre {dest}</h3><p>{guia.get("resenia_corta")}</p></div>', unsafe_allow_html=True)

            # B. PUNTOS IMPERDIBLES
            st.subheader(f"📍 Imperdibles en {dest}")
            puntos = guia.get('puntos', [])
            for p in puntos:
                nombre = p.get('nombre', 'Lugar')
                q_map = urllib.parse.quote(f"{nombre} {dest}")
                map_url = f"https://www.google.com/maps/search/?api=1&query={q_map}"
                
                tkt_url = p.get('url_ticket', '')
                btn_tkt = ""
                if "gratis" not in str(p.get('precio')).lower():
                    if "http" not in str(tkt_url): tkt_url = f"https://www.google.com/search?q=tickets+{urllib.parse.quote(nombre)}"
                    btn_tkt = f'<a href="{tkt_url}" target="_blank" class="btn-action btn-tkt">🎟️ TICKETS</a>'

                st.markdown(f"""
                <div class="punto-card">
                    <h3>{nombre}</h3>
                    <p>{p.get('resenia')}</p>
                    <small>⏰ {p.get('horario')} | 💰 {p.get('precio')}</small><br>
                    <a href="{map_url}" target="_blank" class="btn-action btn-map">🗺️ MAPA</a>
                    {btn_tkt}
                </div>
                """, unsafe_allow_html=True)

            # C. INFORMACIÓN RELEVANTE (ABAJO DE TODO)
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#00acc1">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h4>💰 Finanzas (Dólar)</h4>
                        <p><b>En {dest}:</b> {guia.get('finanzas', {}).get('cambio_local_usd')}</p>
                        <p><b>En {nac}:</b> {guia.get('finanzas', {}).get('cambio_nacional_usd')}</p>
                    </div>
                    <div>
                        <h4>☀️ Clima (7 días)</h4>
                        <p>{guia.get('clima')}</p>
                    </div>
                    <div>
                        <h4>🏛️ Consulado</h4>
                        <p>{guia.get('consulado')}</p>
                    </div>
                    <div>
                        <h4>🏥 Hospital</h4>
                        <p>{guia.get('hospital')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)