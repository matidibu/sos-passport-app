import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

if "dest" not in st.session_state: st.session_state.dest = ""

st.markdown(f"""
    <style>
    .stApp {{ background: #f4f7f6; }}
    .header-container {{
        background: linear-gradient(90deg, #00838f, #00acc1);
        padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 25px;
    }}
    .resenia-box {{
        background: white; padding: 25px; border-radius: 15px; margin-bottom: 25px;
        border-left: 10px solid #ff9800; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    .punto-card {{
        background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-bottom: 5px solid #00acc1;
    }}
    .info-relevante-box {{
        background: #0d1b2a; color: #ffffff; padding: 40px;
        border-radius: 20px; margin-top: 40px; border-top: 8px solid #ff9800;
    }}
    .currency-val {{ color: #00e5ff; font-weight: 800; font-size: 1.5rem; }}
    .disclaimer {{
        margin-top: 30px; padding: 15px; border-radius: 10px;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.85rem; color: #b0bec5; line-height: 1.4;
    }}
    .btn-action {{
        display: inline-block; padding: 12px 20px; border-radius: 10px;
        text-decoration: none; font-weight: 700; margin-top: 15px; margin-right: 10px; text-align: center;
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
    st.error("Error en las credenciales (Secrets).")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu compañero de viaje inteligente</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac = st.text_input("🌎 Tu Nacionalidad", value="Argentina")
with c2: dest_input = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Valencia, España", key="user_dest")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest_input:
        st.session_state.dest = dest_input
        search_key = f"{dest_input.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Sincronizando datos de {dest_input}..."):
                prompt = f"""Genera un JSON para un viajero de nacionalidad {nac} que visita {dest_input}. Idioma: {lang}.
                INSTRUCCIONES: Identifica monedas oficiales de ambos países y cambio vs USD.
                ESTRUCTURA JSON:
                {{
                    "resenia_ciudad": "Texto descriptivo",
                    "puntos_imperdibles": [{{ "nombre": "Nombre", "descripcion": "Info", "horario": "Horas", "precio": "Valor", "url": "url" }}],
                    "moneda_destino_nombre": "Moneda local",
                    "cambio_destino_usd": "1 USD = ?",
                    "moneda_usuario_nombre": "Tu moneda",
                    "cambio_usuario_usd": "1 USD = ?",
                    "pronostico_7_dias": "Clima",
                    "datos_consulado": "Contacto",
                    "datos_hospital": "Dirección"
                }}"""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. IMAGEN
            img_query = urllib.parse.quote(dest_input)
            st.markdown(f'<img src="https://loremflickr.com/1200/500/{img_query},city/all" style="width:100%; border-radius:15px; margin-bottom:20px;">', unsafe_allow_html=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Sobre {dest_input}</h2><p>{guia.get("resenia_ciudad")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS
            st.subheader("📍 Lugares que no te puedes perder")
            for p in guia.get('puntos_imperdibles', []):
                nombre_p = p.get('nombre', 'Lugar')
                desc_clean = str(p.get('descripcion', '')).replace('Descripción:', '').replace('descripcion:', '')
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{nombre_p}</h3>
                    <p>{desc_clean}</p>
                    <small><b>⏰ Horario:</b> {p.get('horario')} | <b>💰 Precio:</b> {p.get('precio')}</small><br>
                    <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(nombre_p + ' ' + dest_input)}" target="_blank" class="btn-action btn-map">🗺️ MAPA</a>
                    <a href="https://www.google.com/search?q=tickets+official+{urllib.parse.quote(nombre_p)}" target="_blank" class="btn-action btn-tkt">🎟️ TICKETS</a>
                </div>
                """, unsafe_allow_html=True)

            # D. INFORMACIÓN RELEVANTE + DISCLAIMER
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#00acc1; margin-bottom:30px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px;">
                    <div>
                        <h4 style="color:#ff9800;">💰 Tipo de Cambio (vs 1 USD)</h4>
                        <p>Moneda en {dest_input}: <b>{guia.get('moneda_destino_nombre')}</b></p>
                        <p class="currency-val">1 USD = {guia.get('cambio_destino_usd')}</p>
                        <hr style="opacity:0.2">
                        <p>Tu Moneda ({nac}): <b>{guia.get('moneda_usuario_nombre')}</b></p>
                        <p class="currency-val">1 USD = {guia.get('cambio_usuario_usd')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">☀️ Clima (7 días)</h4>
                        <p>{guia.get('pronostico_7_dias')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">🏛️ Seguridad y Salud</h4>
                        <p><b>Consulado:</b><br>{guia.get('datos_consulado')}</p>
                        <p style="margin-top:10px;"><b>Hospital:</b><br>{guia.get('datos_hospital')}</p>
                    </div>
                </div>
                <div class="disclaimer">
                    <b>Nota sobre la información:</b> Los datos financieros, climáticos y de contacto son obtenidos de fuentes públicas y modelos predictivos globales (como Google Finance y OpenWeather). <br><br>
                    <i>SOS Passport brinda esta información con fines informativos y recreativos. No nos hacemos responsables por inexactitudes, cambios de último momento o decisiones tomadas basadas en estos datos. Recomendamos siempre verificar información crítica en fuentes oficiales antes de viajar.</i>
                </div>
            </div>
            """, unsafe_allow_html=True)