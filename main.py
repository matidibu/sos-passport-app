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
    if not texto: return "Consultar"
    texto = str(texto)
    # Limpia el tartamudeo de '1 USD ='
    texto = re.sub(r'1\s*USD\s*=\s*', '', texto, flags=re.IGNORECASE)
    return texto.replace('$', '').strip()

# Estilos CSS mejorados
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
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error: No se pudieron cargar las credenciales.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS Passport 🏖️</h1><p>Tu guía de viaje inteligente y robusta</p></div>', unsafe_allow_html=True)

# 3. ENTRADA DE USUARIO
c1, c2, c3 = st.columns(3)
with c1: nac_raw = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Valencia")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = capitalizar(nac_raw)
destino = capitalizar(dest_raw)

if st.button("¡GENERAR GUÍA!", use_container_width=True):
    if not destino:
        st.warning("Escribe una ciudad para comenzar.")
    else:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass

        if not guia:
            with st.spinner(f"Analizando {destino}..."):
                try:
                    prompt = f"""Genera un JSON para un viajero {nacionalidad} en {destino}. Idioma: {lang}.
                    REGLAS: Ortografía impecable, nombres propios con Mayúscula. 
                    FECHA: Feb 2026. Cambio ARS/USD aprox 1420.
                    JSON:
                    {{
                        "resenia": "Descripción de la ciudad",
                        "puntos": [{{ "n": "Nombre Lugar", "d": "Info", "h": "Horas", "p": "Precio" }}],
                        "moneda_d": "Moneda local",
                        "cambio_d": "valor",
                        "moneda_n": "Moneda nacional",
                        "cambio_n": "valor",
                        "clima": "Resumen clima",
                        "consulado": "Datos contacto",
                        "hospital": "Centro salud"
                    }}"""
                    
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    guia = json.loads(chat.choices[0].message.content)
                    supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except:
                    st.error("La IA tardó mucho en responder. Por favor, reintenta.")
                    st.stop()

        if guia:
            # A. IMAGEN (Respaldo garantizado)
            img_url = f"https://images.unsplash.com/photo-1449034446853-66c86144b0ad?q=80&w=1200&auto=format&fit=crop" # Default
            if destino:
                img_url = f"https://api.duas.com/v1/image?query={urllib.parse.quote(destino + ' city landmark')}"
                # Usamos una URL de placeholder de alta calidad que siempre carga
                img_url = f"https://picsum.photos/seed/{urllib.parse.quote(destino)}/1200/500"
            
            st.image(img_url, use_container_width=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia", "Sin descripción disponible.")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS IMPERDIBLES (Blindado contra TypeErrors)
            st.subheader(f"📍 Lugares destacados")
            for p in guia.get('puntos', []):
                nombre_lugar = p.get('n', 'Lugar de interés')
                desc_lugar = p.get('d', 'Sin descripción.')
                # Verificamos que 'nombre_lugar' no sea None antes de usar quote
                query_mapa = urllib.parse.quote(f"{nombre_lugar} {destino}")
                
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{capitalizar(nombre_lugar)}</h3>
                    <p>{desc_lugar}</p>
                    <small>⏰ {p.get('h', 'Verificar')} | 💰 {p.get('p', 'Verificar')}</small><br>
                    <a href="https://www.google.com/maps/search/?api=1&query={query_mapa}" target="_blank" style="color:#0284c7; font-weight:bold; text-decoration:none;">🗺️ Ver en Google Maps</a>
                </div>
                """, unsafe_allow_html=True)

            # D. INFO RELEVANTE
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#38bdf8; margin-bottom:30px;">📊 Información Relevante</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px;">
                    <div>
                        <h4 style="color:#94a3b8;">💰 Moneda y Cambio</h4>
                        <p>{guia.get('moneda_d', 'Moneda local')}: <span class="currency-val">1 USD = {limpiar_valor(guia.get('cambio_d'))}</span></p>
                        <p>{guia.get('moneda_n', 'Tu moneda')}: <span class="currency-val">1 USD = {limpiar_valor(guia.get('cambio_n'))}</span></p>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8;">☀️ Clima</h4>
                        <p>{guia.get('clima', 'No disponible')}</p>
                    </div>
                    <div>
                        <h4 style="color:#94a3b8;">🏛️ Asistencia</h4>
                        <p><b>Consulado:</b> {guia.get('consulado', 'No disponible')}</p>
                        <p><b>Hospital:</b> {guia.get('hospital', 'No disponible')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)