import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

def corregir_nombre(texto):
    """Asegura que los nombres propios empiecen con mayúscula"""
    return texto.strip().title()

def limpiar_cambio(texto):
    """Limpia redundancias en el tipo de cambio"""
    texto = str(texto)
    texto = re.sub(r'1\s*USD\s*=\s*', '', texto, flags=re.IGNORECASE)
    return texto.replace('$', '').strip()

st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    .header-container {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding: 50px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px;
    }
    .resenia-box {
        background: white; padding: 30px; border-radius: 15px; margin-bottom: 30px;
        border-left: 8px solid #38bdf8; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .punto-card {
        background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); border-bottom: 4px solid #38bdf8;
    }
    .info-relevante-box {
        background: #0f172a; color: #f1f5f9; padding: 45px;
        border-radius: 25px; margin-top: 50px; border-top: 6px solid #38bdf8;
    }
    .currency-val { color: #38bdf8; font-weight: 800; font-size: 1.7rem; display: block; }
    .disclaimer {
        margin-top: 35px; padding: 20px; border-radius: 12px;
        background: rgba(255, 255, 255, 0.03); font-size: 0.85rem; color: #94a3b8;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .img-main { width: 100%; border-radius: 25px; height: 500px; object-fit: cover; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de conexión. Verifique los secretos de la aplicación.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Precisión informativa para viajeros exigentes</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Valencia")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

dest_input = corregir_nombre(dest_raw)
nacionalidad = corregir_nombre(nac)

if st.button("¡EXPLORAR DESTINO!", use_container_width=True):
    if dest_input:
        search_key = f"{dest_input.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Analizando {dest_input} con rigor ortográfico..."):
                prompt = f"""Genera un JSON para un viajero {nacionalidad} en {dest_input}. Idioma: {lang}.
                REGLAS CRÍTICAS: 
                1. Ortografía perfecta. Nombres propios siempre con Mayúscula.
                2. Cambio: 1 USD en Argentina = 1420 ARS (Feb 2026).
                3. JSON puro, sin preámbulos.
                {{
                    "resenia": "Texto descriptivo impecable",
                    "puntos": [{{ "nombre": "Nombre Propio", "desc": "Descripción", "h": "Horarios", "p": "Precios" }}],
                    "moneda_d": "Nombre moneda destino",
                    "cambio_d": "Solo número y sigla",
                    "moneda_n": "Nombre moneda viajero",
                    "cambio_n": "Solo número y sigla",
                    "clima": "Resumen climático",
                    "consulado": "Datos oficiales",
                    "hospital": "Centro de salud"
                }}"""
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(completion.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. IMAGEN (Nuevo sistema estable)
            search_url = urllib.parse.quote(f"{dest_input} city landscape")
            st.markdown(f'<img src="https://loremflickr.com/1600/900/{search_url}/all" class="img-main">', unsafe_allow_html=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Explorando {dest_input}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS IMPERDIBLES
            st.subheader(f"📍 Lugares Destacados en {dest_input}")
            for p in guia.get('puntos', []):
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{corregir_nombre(p.get('nombre'))}</h3>
                    <p>{p.get('desc')}</p>
                    <small><b>⏰ Horario:</b> {p.get('h')} | <b>💰 Precio:</b> {p.get('p')}</small><br>
                    <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(p.get('nombre') + ' ' + dest_input)}" target="_blank" style="color:#0ea5e9; font-weight:bold; text-decoration:none; display:inline-block; margin-top:10px;">🗺️ Ver en Google Maps</a>
                </div>
                """, unsafe_allow_html=True)

            # D. INFORMACIÓN RELEVANTE
            c_dest = limpiar_cambio(guia.get('cambio_d'))
            c_nac = limpiar_cambio(guia.get('cambio_n'))

            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#38bdf8; margin-bottom:35px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 40px;">
                    <div>
                        <h4 style="color:#94a3b8; margin-bottom:15px; text-transform: uppercase; letter-spacing: 1px;">💰 Mercado de Divisas</h4>
                        <p style="margin-bottom:5px;">1 USD en {dest_input} ({guia.get('moneda_d')}):</p>
                        <span class="currency-val">1 USD = {c_dest}</span>
                        <hr style="opacity:0.1; margin: 20px 0;">
                        <p style="margin-bottom:5px;">1 USD en {nacionalidad} ({guia.get('moneda_n')}):</p>
                        <span class="currency-val">1 USD = {c_nac}</span>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8; margin-bottom:15px; text-transform: uppercase; letter-spacing: 1px;">☀️ Estado del Clima</h4>
                        <p style="line-height:1.6;">{guia.get('clima')}</p>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8; margin-bottom:15px; text-transform: uppercase; letter-spacing: 1px;">🏛️ Asistencia</h4>
                        <p><b>Consulado:</b><br>{guia.get('consulado')}</p>
                        <p style="margin-top:15px;"><b>Salud:</b><br>{guia.get('hospital')}</p>
                    </div>
                </div>
                <div class="disclaimer">
                    <b>Nota de Transparencia:</b> La información aquí presentada proviene de modelos de datos globales actualizados a Febrero de 2026. <br><br>
                    <i>SOS Passport ofrece estos datos con fines orientativos. Dada la naturaleza cambiante de la economía y el clima, no asumimos responsabilidad legal por discrepancias en las cifras o servicios mencionados. Recomendamos encarecidamente contrastar información crítica con fuentes gubernamentales oficiales antes de iniciar su viaje.</i>
                </div>
            </div>
            """, unsafe_allow_html=True)