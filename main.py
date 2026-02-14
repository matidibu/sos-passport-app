import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

def capitalizar(texto):
    if not texto: return ""
    return str(texto).strip().title()

def limpiar_valor(texto):
    if not texto or texto == "None": return "Consultar dato"
    texto = str(texto)
    texto = re.sub(r'1\s*USD\s*=\s*', '', texto, flags=re.IGNORECASE)
    return texto.replace('$', '').strip()

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-container {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        padding: 40px; border-radius: 20px; color: white; text-align: center; margin-bottom: 30px;
    }
    .resenia-box {
        background: white; padding: 25px; border-radius: 15px;
        border-left: 8px solid #0284c7; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    .punto-card {
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-bottom: 4px solid #0284c7;
    }
    .info-relevante-box {
        background: #0f172a; color: white; padding: 40px;
        border-radius: 20px; margin-top: 40px;
    }
    .currency-val { color: #38bdf8; font-weight: 800; font-size: 1.6rem; }
    .img-container img { width: 100%; border-radius: 20px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión. Revisa tus Secrets.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu guía inteligente con datos verificados</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac_raw = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Paris")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = capitalizar(nac_raw)
destino = capitalizar(dest_raw)

if st.button("¡GENERAR GUÍA!", use_container_width=True):
    if not destino:
        st.warning("Escribe un destino válido.")
    else:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass

        if not guia:
            with st.spinner(f"Obteniendo datos precisos de {destino}..."):
                try:
                    # Prompt más estricto para evitar alucinaciones
                    prompt = f"""Genera un JSON para un viajero {nacionalidad} en {destino}. Idioma: {lang}.
                    - resenia: Descripción histórica y moderna.
                    - puntos: [{{ "n": "Nombre", "d": "Detalle", "h": "Horario", "p": "Costo" }}]
                    - moneda_d: Moneda local
                    - cambio_d: Solo el número y sigla (Ej: 0.92 EUR)
                    - moneda_n: Moneda de {nacionalidad}
                    - cambio_n: 1420 ARS (si es Argentina) o valor real a Feb 2026.
                    - clima: Reporte 7 días.
                    - consulado: Dirección y tel.
                    - hospital: Nombre y dirección.
                    """
                    
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    contenido = chat.choices[0].message.content
                    if contenido:
                        guia = json.loads(contenido)
                        supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except Exception as e:
                    st.error(f"Hubo un problema al generar los datos. Reintenta por favor.")

        if guia:
            # A. IMAGEN (Buscador temático real)
            # Usamos Unsplash con parámetros de búsqueda específicos para la ciudad
            query_img = urllib.parse.quote(destino)
            st.image(f"https://loremflickr.com/1200/500/{query_img},landscape/all", caption=f"Explorando {destino}", use_container_width=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia", "Sin datos.")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS
            st.subheader(f"📍 Imperdibles")
            puntos = guia.get('puntos', [])
            if puntos:
                for p in puntos:
                    n_lug = capitalizar(p.get('n', 'Lugar'))
                    st.markdown(f"""
                    <div class="punto-card">
                        <h3>{n_lug}</h3>
                        <p>{p.get('d', 'Sin descripción')}</p>
                        <small><b>Horario:</b> {p.get('h')} | <b>Precio:</b> {p.get('p')}</small><br>
                        <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(n_lug + ' ' + destino)}" target="_blank" style="color:#0284c7; font-weight:bold; text-decoration:none;">🗺️ Abrir Mapa</a>
                    </div>
                    """, unsafe_allow_html=True)

            # D. INFO RELEVANTE
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#38bdf8; margin-bottom:30px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px;">
                    <div>
                        <h4 style="color:#94a3b8;">💰 Cambio (vs 1 USD)</h4>
                        <p>{guia.get('moneda_d')}: <span class="currency-val">1 USD = {limpiar_valor(guia.get('cambio_d'))}</span></p>
                        <p>{guia.get('moneda_n')}: <span class="currency-val">1 USD = {limpiar_valor(guia.get('cambio_n'))}</span></p>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8;">☀️ Clima</h4>
                        <p>{guia.get('clima', 'Consultar fuentes locales.')}</p>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8;">🏛️ Asistencia</h4>
                        <p><b>Consulado:</b> {guia.get('consulado')}</p>
                        <p><b>Hospital:</b> {guia.get('hospital')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)