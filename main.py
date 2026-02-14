import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

if "dest" not in st.session_state: st.session_state.dest = ""

# Color dinámico
bg_color = "#f0faff"
d = st.session_state.dest.lower()
if any(x in d for x in ["cabo", "africa", "mexico", "amalfi", "costa"]): bg_color = "#fff3e0"
elif any(x in d for x in ["paris", "londres", "europa"]): bg_color = "#f5f5f5"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: background 0.8s ease; }}
    .header-container {{
        background: linear-gradient(90deg, #00838f, #00acc1);
        padding: 40px; border-radius: 25px; color: white; text-align: center; margin-bottom: 20px;
    }}
    .resenia-box {{
        background: white; padding: 30px; border-radius: 20px; margin-bottom: 30px;
        border-left: 10px solid #ff9800; box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }}
    .punto-card {{
        background: white; border-radius: 20px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05); border-bottom: 6px solid #00acc1;
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

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu guía inteligente para explorar el mundo</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ (Sin Form para respuesta inmediata)
c1, c2, c3 = st.columns(3)
with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_input = st.text_input("📍 Destino", placeholder="Ej: Costa Amalfitana", key="user_dest")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

# El disparador es el botón, pero el flujo es más directo ahora
if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True) or (dest_input and dest_input != st.session_state.dest):
    if dest_input:
        st.session_state.dest = dest_input
        search_key = f"{dest_input.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        # Consultar base de datos
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Diseñando tu viaje a {dest_input}..."):
                try:
                    prompt = f"Genera JSON para viajero {nac} en {dest_input} en {lang}: resenia_corta, puntos (nombre, resenia, horario, precio, url_ticket), finanzas (cambio_local_usd, cambio_nacional_usd), clima, consulado, hospital."
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    guia = json.loads(chat.choices[0].message.content)
                    supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except Exception as e:
                    st.error(f"La región es muy amplia. Intentá con una ciudad específica (ej: Positano) si esto falla.")
                    st.stop()

        if guia:
            # A. FOTO Y RESEÑA
            img_url = f"https://loremflickr.com/1200/500/{urllib.parse.quote(dest_input)},landscape/all"
            st.image(img_url, use_container_width=True)
            st.markdown(f'<div class="resenia-box"><h2>Sobre {dest_input}</h2><p style="font-size:1.1rem;">{guia.get("resenia_corta")}</p></div>', unsafe_allow_html=True)

            # B. PUNTOS
            st.subheader(f"📍 Imperdibles Seleccionados")
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
                    <p>{p.get('resenia')}</p>
                    <span style="background:#e0f7fa; padding:5px 10px; border-radius:8px; font-size:0.8rem; font-weight:bold; color:#006064;">⏰ {p.get('horario')}</span>
                    <span style="background:#f1f8e9; padding:5px 10px; border-radius:8px; font-size:0.8rem; font-weight:bold; color:#2e7d32; margin-left:10px;">💰 {p.get('precio')}</span>
                    <br>
                    <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(n + ' ' + dest_input)}" target="_blank" class="btn-action btn-map">🗺️ MAPA</a>
                    {btn_tkt}
                </div>
                """, unsafe_allow_html=True)

            # C. INFORMACIÓN RELEVANTE (ABAJO)
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#00acc1">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div>
                        <h4 style="color:#ff9800">💰 Moneda (vs USD)</h4>
                        <p><b>{dest_input}:</b> {guia.get('finanzas', {}).get('cambio_local_usd')}</p>
                        <p><b>{nac}:</b> {guia.get('finanzas', {}).get('cambio_nacional_usd')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800">☀️ Clima</h4>
                        <p>{guia.get('clima')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800">🏛️ Consulado e Higiene</h4>
                        <p><b>Asistencia:</b> {guia.get('consulado')}</p>
                        <p><b>Hospital:</b> {guia.get('hospital')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)