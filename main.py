import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

def seguro(texto): 
    """Evita errores de tipo None y asegura mayúsculas en nombres propios"""
    if not texto: return "Dato no disponible"
    return str(texto).strip().capitalize()

def limpiar_cambio(texto):
    """Limpia el '1 USD =' duplicado"""
    if not texto: return "Consultar"
    texto = str(texto)
    texto = re.sub(r'1\s*USD\s*=\s*', '', texto, flags=re.IGNORECASE)
    return texto.replace('$', '').strip()

st.markdown("""
    <style>
    .stApp { background: #f4f7f6; }
    .header-container {
        background: linear-gradient(90deg, #00838f, #00acc1);
        padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 25px;
    }
    .resenia-box {
        background: white; padding: 25px; border-radius: 15px; margin-bottom: 25px;
        border-left: 10px solid #ff9800; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .punto-card {
        background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-bottom: 5px solid #00acc1;
    }
    .info-relevante-box {
        background: #0d1b2a; color: #ffffff; padding: 40px;
        border-radius: 20px; margin-top: 40px; border-top: 8px solid #ff9800;
    }
    .currency-val { color: #00e5ff; font-weight: 800; font-size: 1.5rem; }
    .disclaimer {
        margin-top: 30px; padding: 20px; border-radius: 10px;
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.85rem; color: #b0bec5;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en las credenciales.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu guía de viaje inteligente</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac_in = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_in = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Paris")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = seguro(nac_in)
destino = seguro(dest_in)

if st.button("¡EXPLORAR DESTINO!", use_container_width=True):
    if dest_in:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Analizando {destino}..."):
                prompt = f"""Genera un JSON para {nacionalidad} visitando {destino}. Idioma: {lang}. 
                Cambio ARS/USD Feb 2026: 1420. Nombres propios con Mayúscula.
                {{
                    "resenia": "Texto",
                    "puntos": [{{ "nombre": "Lugar", "desc": "Info", "h": "Horas", "p": "Precio" }}],
                    "mon_d": "Moneda local", "cam_d": "Valor",
                    "mon_n": "Moneda {nacionalidad}", "cam_n": "Valor",
                    "clima": "Clima", "cons": "Consulado", "hosp": "Hospital"
                }}"""
                chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. IMAGEN (Búsqueda específica de ciudad)
            st.image(f"https://loremflickr.com/1200/500/{urllib.parse.quote(destino)}", use_container_width=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS IMPERDIBLES (Blindado contra errores de texto)
            st.subheader("📍 Lugares Recomendados")
            for p in guia.get('puntos', []):
                n_p = seguro(p.get('nombre'))
                d_p = seguro(p.get('desc'))
                # Link de mapa ultra-seguro (f-string)
                link_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{n_p} {destino}')}"
                
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n_p}</h3>
                    <p>{d_p}</p>
                    <small>⏰ {p.get('h')} | 💰 {p.get('p')}</small><br>
                    <a href="{link_mapa}" target="_blank" style="background:#00acc1; color:white; padding:8px 15px; border-radius:5px; text-decoration:none; display:inline-block; margin-top:10px; font-weight:bold;">🗺️ MAPA</a>
                </div>
                """, unsafe_allow_html=True)

            # D. INFORMACIÓN RELEVANTE + DISCLAIMER
            c_dest = limpiar_cambio(guia.get('cam_d'))
            c_nac = limpiar_cambio(guia.get('cam_n'))

            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#00acc1; margin-bottom:30px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px;">
                    <div>
                        <h4 style="color:#ff9800;">💰 Tipo de Cambio (vs 1 USD)</h4>
                        <p>En {destino}: {guia.get('mon_d')}</p>
                        <p class="currency-val">1 USD = {c_dest}</p>
                        <hr style="opacity:0.2">
                        <p>En {nacionalidad}: {guia.get('mon_n')}</p>
                        <p class="currency-val">1 USD = {c_nac}</p>
                    </div>
                    <div>
                        <h4 style="color:#ff9800;">☀️ Clima y Seguridad</h4>
                        <p><b>Clima:</b> {guia.get('clima')}</p>
                        <p><b>Consulado:</b> {guia.get('cons')}</p>
                        <p><b>Hospital:</b> {guia.get('hosp')}</p>
                    </div>
                </div>
                <div class="disclaimer">
                    <b>Nota sobre la información:</b> Los datos de moneda, clima y contacto provienen de fuentes públicas analizadas por IA a Febrero de 2026. <br><br>
                    <i>SOS Passport brinda esta información con fines orientativos. <b>No nos hacemos responsables</b> si la información brindada es errónea o está desactualizada. Recomendamos verificar datos críticos en canales oficiales antes de viajar.</i>
                </div>
            </div>
            """, unsafe_allow_html=True)