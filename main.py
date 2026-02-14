import streamlit as st
from groq import Groq
from supabase import create_client
import json
import urllib.parse
import re

# 1. ESTILO Y CONFIGURACIÓN (Tu fuente original)
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto): 
    if not texto or texto == "None": return "Información no disponible"
    return str(texto).strip().title()

# FUNCIÓN CRÍTICA: Limpia el ruido de la IA para que el JSON no falle
def extraer_json(texto):
    try:
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        return match.group(0) if match else texto
    except:
        return texto

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background: #f8fafc; font-family: 'Inter', sans-serif; }
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 50px 20px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 40px;
    }
    .resenia-box {
        background: white; padding: 30px; border-radius: 20px; margin-bottom: 30px;
        border-left: 10px solid #0ea5e9; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .punto-card {
        background: white; border-radius: 20px; padding: 25px; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-bottom: 5px solid #0ea5e9;
    }
    .info-relevante-box {
        background: #0f172a; color: #f8fafc; padding: 50px; border-radius: 30px; margin-top: 50px;
    }
    .info-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 35px;
    }
    .btn-action {
        display: inline-block; padding: 10px 18px; border-radius: 8px;
        text-decoration: none; font-size: 0.85rem; font-weight: 700;
        margin-top: 15px; margin-right: 10px; text-align: center;
    }
    .btn-primary { background: #0ea5e9; color: white !important; }
    .btn-secondary { background: #f59e0b; color: white !important; }
    .btn-link { 
        display: block; background: #1e293b; color: #38bdf8 !important; 
        border: 1px solid #38bdf8; font-size: 0.75rem; padding: 8px; 
        border-radius: 6px; text-decoration: none; text-align: center; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

st.markdown("""<div class="header-container"><h1>SOS PASSPORT ✈️</h1><p>Logística Global y Tickets Oficiales</p></div>""", unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac_in = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Madrid")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = seguro(nac_in)
destino = seguro(dest_raw)

if st.button("GENERAR LOGÍSTICA COMPLETA", use_container_width=True):
    if not dest_raw:
        st.warning("Por favor, ingresa un destino.")
    else:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        # Recuperar de Supabase
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        # Generar con IA si no existe
        if not guia:
            with st.spinner("Conectando con servicios locales..."):
                try:
                    prompt = f"""Genera un JSON para un viajero {nacionalidad} en {destino}. Idioma: {lang}. 
                    JSON:
                    {{
                        "resenia": "Breve descripción",
                        "puntos": [{{ "n": "Lugar", "d": "Info", "h": "Horas", "p": "Precio" }}],
                        "cambio": "Datos casas cambio",
                        "autos": "Rentadoras",
                        "alojamiento": "Zonas Airbnb",
                        "clima": "Pronóstico",
                        "consulado": "Contacto",
                        "hospital": "Salud"
                    }}"""
                    chat = client.chat.completions.create(
                        messages=[{"role":"user","content":prompt}], 
                        model="llama-3.3-70b-versatile", 
                        response_format={"type":"json_object"}
                    )
                    
                    # Limpiamos y cargamos el JSON
                    contenido = extraer_json(chat.choices[0].message.content)
                    guia = json.loads(contenido)
                    
                    # Guardar
                    supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except Exception as e:
                    st.error(f"Error al generar datos: {e}")
                    st.stop()

        if guia:
            # Foto Principal
            st.image(f"https://loremflickr.com/1200/500/{urllib.parse.quote(destino)},city/all", use_container_width=True)
            
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia", "Sin reseña.")}</p></div>', unsafe_allow_html=True)

            # PUNTOS
            st.subheader("📍 Itinerario Sugerido")
            puntos = guia.get('puntos', [])
            if isinstance(puntos, list):
                for p in puntos:
                    n_p = seguro(p.get('n'))
                    link_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{n_p} {destino}')}"
                    link_tkt = f"https://www.google.com/search?q=official+tickets+{urllib.parse.quote(f'{n_p} {destino}')}"
                    st.markdown(f"""
                    <div class="punto-card">
                        <h3>{n_p}</h3>
                        <p>{p.get('d', '')}</p>
                        <small><b>⏰ Horario:</b> {p.get('h', 'Verificar')} | <b>💰 Precio:</b> {p.get('p', 'Verificar')}</small><br>
                        <a href="{link_mapa}" target="_blank" class="btn-action btn-primary">🗺️ MAPA</a>
                        <a href="{link_tkt}" target="_blank" class="btn-action btn-secondary">🎟️ TICKETS</a>
                    </div>
                    """, unsafe_allow_html=True)

            # LOGÍSTICA
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:white; margin-bottom:40px; text-align:center;">📊 Logística</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <h4 style="color:#38bdf8;">🏨 Alojamiento</h4>
                        <p>{guia.get('alojamiento', 'Consultar Airbnb')}</p>
                        <a href="https://www.airbnb.com/s/{urllib.parse.quote(destino)}/homes" target="_blank" class="btn-link">🔗 IR A AIRBNB</a>
                    </div>
                    <div class="info-item">
                        <h4 style="color:#38bdf8;">💰 Casas de Cambio</h4>
                        <p>{guia.get('cambio', 'Consultar mapas')}</p>
                        <a href="https://www.google.com/maps/search/currency+exchange+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 VER UBICACIONES</a>
                    </div>
                    <div class="info-item">
                        <h4 style="color:#38bdf8;">🏥 Salud</h4>
                        <p>{guia.get('hospital', 'Consultar centros')}</p>
                        <a href="https://www.google.com/maps/search/hospital+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 HOSPITALES CERCA</a>
                    </div>
                    <div class="info-item">
                        <h4 style="color:#38bdf8;">🏛️ Consulado</h4>
                        <p>{guia.get('consulado', 'Consultar')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)