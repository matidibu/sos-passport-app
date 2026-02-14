import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

def capitalizar(texto):
    return texto.strip().title() if texto else ""

def limpiar_valor(texto):
    if not texto: return "Dato no disponible"
    texto = str(texto)
    # Limpia el tartamudeo de '1 USD ='
    texto = re.sub(r'1\s*USD\s*=\s*', '', texto, flags=re.IGNORECASE)
    return texto.replace('$', '').strip()

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-container {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px;
    }
    .resenia-box {
        background: white; padding: 25px; border-radius: 15px;
        border-left: 8px solid #0284c7; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .punto-card {
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 15px;
        border-bottom: 4px solid #0284c7;
    }
    .info-relevante-box {
        background: #0f172a; color: white; padding: 40px;
        border-radius: 20px; margin-top: 40px;
    }
    .currency-val { color: #38bdf8; font-weight: 800; font-size: 1.6rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error crítico: Faltan las llaves de acceso en Secrets.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Información de viaje con precisión quirúrgica</p></div>', unsafe_allow_html=True)

# 3. ENTRADA DE USUARIO
c1, c2, c3 = st.columns(3)
with c1: nac_raw = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Valencia")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = capitalizar(nac_raw)
destino = capitalizar(dest_raw)

if st.button("¡GENERAR GUÍA!", use_container_width=True):
    if not destino:
        st.warning("Por favor, ingresa una ciudad de destino.")
    else:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        # Consultar Supabase
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass

        if not guia:
            with st.spinner(f"Sincronizando datos de {destino}..."):
                try:
                    prompt = f"""Genera un JSON para un viajero {nacionalidad} en {destino}. Idioma: {lang}.
                    REGLAS: Ortografía impecable, nombres propios con Mayúscula. 
                    FECHA: Feb 2026. Cambio ARS/USD aprox 1420.
                    JSON:
                    {{
                        "resenia": "Breve descripción",
                        "puntos": [{{ "n": "Nombre Propio", "d": "Descripción", "h": "Horas", "p": "Precio" }}],
                        "moneda_d": "Moneda local",
                        "cambio_d": "Solo número y sigla",
                        "moneda_n": "Moneda de {nacionalidad}",
                        "cambio_n": "Solo número y sigla",
                        "clima": "Estado del tiempo",
                        "consulado": "Contacto consular",
                        "hospital": "Hospital cercano"
                    }}"""
                    
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    guia = json.loads(chat.choices[0].message.content)
                    supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except Exception as e:
                    st.error(f"Error al conectar con la IA. Intenta de nuevo. Detalles: {e}")
                    st.stop()

        if guia:
            # A. IMAGEN (Método nativo de Streamlit)
            img_url = f"https://loremflickr.com/1200/500/{urllib.parse.quote(destino)},city/all"
            st.image(img_url, caption=f"Vista panorámica de {destino}", use_container_width=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia", "Información no disponible.")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS
            st.subheader(f"📍 Imperdibles en {destino}")
            for p in guia.get('puntos', []):
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{capitalizar(p.get('n'))}</h3>
                    <p>{p.get('d')}</p>
                    <small>⏰ {p.get('h')} | 💰 {p.get('p')}</small><br>
                    <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(p.get('n') + ' ' + destino)}" target="_blank" style="color:#0284c7; font-weight:bold; text-decoration:none;">🗺️ Ver mapa</a>
                </div>
                """, unsafe_allow_html=True)

            # D. INFO RELEVANTE
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#38bdf8; margin-bottom:30px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px;">
                    <div>
                        <h4 style="color:#94a3b8;">💰 Cambio (vs 1 USD)</h4>
                        <p>{guia.get('moneda_d')}: <span class="currency-val">1 USD = {limpiar_valor(guia.get('cambio_d'))}</span></p>
                        <p>{guia.get('moneda_n')}: <span class="currency-val">1 USD = {limpiar_valor(guia.get('cambio_n'))}</span></p>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8;">☀️ Clima</h4>
                        <p>{guia.get('clima', 'No disponible')}</p>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8;">🏛️ Asistencia</h4>
                        <p><b>Consulado:</b> {guia.get('consulado', 'Ver web oficial')}</p>
                        <p><b>Hospital:</b> {guia.get('hospital', 'Ver web oficial')}</p>
                    </div>
                </div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:30px; border-top:1px solid #1e293b; padding-top:20px;">
                    <b>Aviso Legal:</b> Datos a Feb 2026. SOS Passport no se responsabiliza por errores en los datos o variaciones del mercado. Verifique siempre fuentes oficiales.
                </div>
            </div>
            """, unsafe_allow_html=True)