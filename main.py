import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE Y LIMPIO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

if "dest" not in st.session_state: st.session_state.dest = ""

# Color dinámico de fondo
bg_color = "#f0faff"
d = st.session_state.dest.lower()
if any(x in d for x in ["valencia", "españa", "italia", "amalfi", "mexico"]): bg_color = "#fffcf0"
elif any(x in d for x in ["paris", "londres", "tokyo"]): bg_color = "#f8f9fa"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_color}; transition: background 0.8s ease; }}
    .header-container {{
        background: linear-gradient(90deg, #0288d1, #26c6da);
        padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 25px;
    }}
    .resenia-box {{
        background: white; padding: 25px; border-radius: 15px; margin-bottom: 25px;
        border-left: 8px solid #ff9800; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    .punto-card {{
        background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-bottom: 4px solid #26c6da;
    }}
    .info-relevante-box {{
        background: #1a237e; color: #ffffff; padding: 35px;
        border-radius: 20px; margin-top: 40px; border-top: 6px solid #ff9800;
    }}
    .currency-val {{ color: #ffeb3b; font-weight: 800; font-size: 1.4rem; display: block; margin-top: 5px; }}
    .btn-action {{
        display: inline-block; padding: 10px 18px; border-radius: 8px;
        text-decoration: none; font-weight: 700; margin-top: 15px; margin-right: 10px;
    }}
    .btn-map {{ background: #26c6da; color: white !important; }}
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

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Información real para viajeros reales</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_input = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Valencia", key="user_dest")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR!", use_container_width=True) or (dest_input and dest_input != st.session_state.dest):
    if dest_input:
        st.session_state.dest = dest_input
        search_key = f"{dest_input.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Analizando {dest_input}..."):
                # PROMPT EXTREMADAMENTE ESTRICTO
                prompt = f"""Genera un JSON para un viajero {nac} visitando {dest_input}. Idioma: {lang}.
                REGLA DE ORO: NO incluyas títulos como 'Descripción:' o 'Precio:' dentro de los valores.
                JSON:
                - "resenia": "Solo el párrafo de descripción de la ciudad",
                - "puntos": [{"nombre": "Lugar", "info": "Solo descripción", "horario": "Solo horas", "precio": "Solo valor", "tkt": "url"}],
                - "moneda_destino": "Nombre moneda del país de {dest_input}",
                - "cambio_destino_usd": "Solo el número (ej: 0.92)",
                - "moneda_viajero": "Nombre moneda de {nac}",
                - "cambio_viajero_usd": "Solo el número (ej: 1100)",
                - "clima": "Solo el resumen de 7 días",
                - "consulado": "Solo datos de contacto",
                - "hospital": "Solo nombre y dirección"
                """
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. IMAGEN (Nueva fuente más confiable)
            img_dest = dest_input.replace(" ", "+")
            st.markdown(f'<img src="https://source.unsplash.com/featured/1200x500?{img_dest},city" style="width:100%; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
            
            st.markdown(f'<div class="resenia-box"><h2>Sobre {dest_input}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            # B. PUNTOS
            st.subheader("📍 Imperdibles")
            for p in guia.get('puntos', []):
                n = p.get('nombre', 'Lugar')
                t_url = p.get('tkt', '')
                btn_tkt = ""
                if "gratis" not in str(p.get('precio')).lower():
                    if "http" not in str(t_url): t_url = f"https://www.google.com/search?q=tickets+{urllib.parse.quote(n)}"
                    btn_tkt = f'<a href="{t_url}" target="_blank" class="btn-action btn-tkt">🎟️ TICKETS</a>'
                
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n}</h3>
                    <p>{p.get('info')}</p>
                    <small>⏰ {p.get('horario')} | 💰 {p.get('precio')}</small><br>
                    <a href="https://www.google.com/maps/search/{urllib.parse.quote(n + ' ' + dest_input)}" target="_blank" class="btn-action btn-map">🗺️ MAPA</a>
                    {btn_tkt}
                </div>
                """, unsafe_allow_html=True)

            # C. INFORMACIÓN RELEVANTE
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#26c6da; margin-bottom:25px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 30px;">
                    <div>
                        <h4 style="color:#ff9800;">💰 Cambio vs 1 USD</h4>
                        <p><b>{guia.get('moneda_destino')}:</b> <span class="currency-val">{guia.get('cambio_destino_usd')}</span></p>
                        <p style="margin-top:15px;"><b>{guia.get('moneda_viajero')}:</b> <span class="currency-val">{guia.get('cambio_viajero_usd')}</span></p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">☀️ Clima (7 días)</h4>
                        <p>{guia.get('clima')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">🏛️ Seguridad y Salud</h4>
                        <p><b>Consulado:</b><br>{guia.get('consulado')}</p>
                        <p style="margin-top:10px;"><b>Hospital:</b><br>{guia.get('hospital')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)