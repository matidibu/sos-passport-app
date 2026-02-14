import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto):
    if not texto or texto == "None": return "Información no disponible"
    return str(texto).strip().title()

def limpiar_json(texto):
    """Extrae solo el contenido entre llaves para evitar errores de parseo"""
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    return match.group(0) if match else texto

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background: #f8fafc; font-family: 'Inter', sans-serif; }
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 50px 20px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .header-container h1 { font-weight: 800; font-size: 3.2rem; letter-spacing: -1.5px; margin: 0; }
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
    .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 35px; }
    .info-item h4 { color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px; }
    .btn-action { display: inline-block; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 700; margin-top: 15px; margin-right: 10px; text-align: center; }
    .btn-primary { background: #0ea5e9; color: white !important; }
    .btn-secondary { background: #f59e0b; color: white !important; }
    .btn-link { display: block; background: #1e293b; color: #38bdf8 !important; border: 1px solid #38bdf8; font-size: 0.75rem; padding: 8px; border-radius: 6px; text-decoration: none; text-align: center; margin-top: 10px; }
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
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except:
            pass # Si falla Supabase, permitimos que la IA genere info nueva
        
        if not guia:
            with st.spinner("Conectando con servicios locales..."):
                try:
                    prompt = f"""Genera un JSON estrictamente válido para un viajero {nacionalidad} en {destino}. Idioma: {lang}.
                    JSON esperado:
                    {{
                        "resenia": "Breve descripción",
                        "puntos": [{{ "n": "Nombre", "d": "Info", "h": "Horas", "p": "Precio" }}],
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
                        temperature=0.3, # Menos creatividad para evitar errores
                        response_format={"type":"json_object"}
                    )
                    raw_content = chat.choices[0].message.content
                    guia = json.loads(limpiar_json(raw_content))
                    
                    # Intentar guardar pero no morir si falla
                    try:
                        supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                    except:
                        pass
                except Exception as e:
                    st.error(f"Error al generar datos: {e}")
                    st.stop()

        if guia:
            # IMAGEN CON FALLBACK
            st.image(f"https://loremflickr.com/1200/500/city,landscape,{urllib.parse.quote(destino)}/all", use_container_width=True)
            
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia", "Sin reseña disponible.")}</p></div>', unsafe_allow_html=True)

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
                        <small><b>⏰ Horario:</b> {p.get('h', 'Consultar')} | <b>💰 Precio:</b> {p.get('p', 'Consultar')}</small><br>
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
                        <h4>🏨 Alojamiento</h4><p>{guia.get('alojamiento', 'Info no disponible')}</p>
                        <a href="https://www.airbnb.com/s/{urllib.parse.quote(destino)}/homes" target="_blank" class="btn-link">🔗 AIRBNB</a>
                    </div>
                    <div class="info-item">
                        <h4>🚗 Autos</h4><p>{guia.get('autos', 'Info no disponible')}</p>
                        <a href="https://www.rentalcars.com/search-results?locationName={urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 RENTACARS</a>
                    </div>
                    <div class="info-item">
                        <h4>💰 Cambio</h4><p>{guia.get('cambio', 'Info no disponible')}</p>
                        <a href="https://www.google.com/maps/search/currency+exchange+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 UBICACIONES</a>
                    </div>
                    <div class="info-item">
                        <h4>☀️ Clima</h4><p>{guia.get('clima', 'Info no disponible')}</p>
                        <a href="https://www.google.com/search?q=weather+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 DETALLE</a>
                    </div>
                    <div class="info-item">
                        <h4>🏛️ Consulado</h4><p>{guia.get('consulado', 'Info no disponible')}</p>
                        <a href="https://www.google.com/search?q=consulado+{urllib.parse.quote(nacionalidad)}+en+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 WEB OFICIAL</a>
                    </div>
                    <div class="info-item">
                        <h4>🏥 Salud</h4><p>{guia.get('hospital', 'Info no disponible')}</p>
                        <a href="https://www.google.com/maps/search/hospital+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 HOSPITALES CERCA</a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)