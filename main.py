import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re
import random

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

def limpiar_cambio(texto):
    """Elimina repeticiones de '1 USD =' o símbolos para evitar el tartamudeo visual"""
    texto = str(texto)
    # Elimina frases como '1 USD =', '1 USD = ', 'USD', '$'
    texto = re.sub(r'1\s*USD\s*=\s*', '', texto, flags=re.IGNORECASE)
    texto = texto.replace('$', '').strip()
    return texto

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
    .currency-val {{ color: #00e5ff; font-weight: 800; font-size: 1.6rem; display: block; }}
    .disclaimer {{
        margin-top: 30px; padding: 15px; border-radius: 10px;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.85rem; color: #b0bec5;
    }}
    .img-main {{ width:100%; border-radius:20px; height: 450px; object-fit: cover; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en las credenciales (Secrets).")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu inteligencia de viaje sin errores</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_input = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Tel Aviv")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest_input:
        search_key = f"{dest_input.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Sincronizando datos reales para {dest_input}..."):
                prompt = f"""Genera un JSON para viajero {nac} en {dest_input}. Idioma: {lang}.
                IMPORTANTE: Estamos en Feb 2026. 1 USD en Argentina son aprox 1420 ARS. 
                Responde solo el número y moneda en los campos de cambio.
                {{
                    "resenia": "Texto",
                    "puntos": [{{ "nombre": "Lugar", "desc": "Info", "h": "Horas", "p": "Precio" }}],
                    "m_dest": "Nombre moneda destino",
                    "c_dest": "Solo el numero y sigla",
                    "m_nac": "Nombre moneda {nac}",
                    "c_nac": "Solo el numero y sigla",
                    "clima": "Resumen 7 días",
                    "consulado": "Info",
                    "hospital": "Info"
                }}"""
                chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. IMAGEN (Unsplash con Cache Buster para que no falle)
            img_id = random.randint(1, 1000)
            img_url = f"https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80" # Default
            search_slug = urllib.parse.quote(dest_input)
            st.markdown(f'<img src="https://source.unsplash.com/1600x900/?{search_slug},landmark&sig={img_id}" class="img-main">', unsafe_allow_html=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Sobre {dest_input}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS
            st.subheader("📍 Imperdibles")
            for p in guia.get('puntos', []):
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{p.get('nombre')}</h3>
                    <p>{p.get('desc')}</p>
                    <small><b>⏰ Horario:</b> {p.get('h')} | <b>💰 Precio:</b> {p.get('p')}</small><br>
                    <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(p.get('nombre') + ' ' + dest_input)}" target="_blank" style="color:#00acc1; font-weight:bold; text-decoration:none;">🗺️ VER EN MAPA</a>
                </div>
                """, unsafe_allow_html=True)

            # D. INFORMACIÓN RELEVANTE
            # Limpiamos los datos de la moneda antes de mostrar
            cambio_d = limpiar_cambio(guia.get('c_dest'))
            cambio_n = limpiar_cambio(guia.get('c_nac'))

            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#00acc1; margin-bottom:30px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px;">
                    <div>
                        <h4 style="color:#ff9800;">💰 Tipo de Cambio</h4>
                        <p style="color:#b0bec5; margin-bottom:2px;">1 USD en {dest_input} ({guia.get('m_dest')}):</p>
                        <span class="currency-val">1 USD = {cambio_d}</span>
                        <br>
                        <p style="color:#b0bec5; margin-bottom:2px;">1 USD para vos ({guia.get('m_nac')}):</p>
                        <span class="currency-val">1 USD = {cambio_n}</span>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">☀️ Clima (7 días)</h4>
                        <p>{guia.get('clima')}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">🏛️ Seguridad y Salud</h4>
                        <p><b>Consulado:</b> {guia.get('consulado')}</p>
                        <p><b>Hospital:</b> {guia.get('hospital')}</p>
                    </div>
                </div>
                <div class="disclaimer">
                    <b>Nota:</b> Información actualizada a Feb 2026. SOS Passport es una guía orientativa y no se responsabiliza por cambios en las cotizaciones o datos brindados.
                </div>
            </div>
            """, unsafe_allow_html=True)