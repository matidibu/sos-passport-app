import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import time

# 1. CONFIGURACIÓN Y ESTILO BLINDADO
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto, default="Dato no disponible"): 
    if not texto or str(texto).lower() == "none": return default
    return str(texto).strip().title()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px 20px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 30px;
    }
    
    /* Contenedor de Imagen Dinámico */
    .img-wrapper {
        width: 100%; height: 400px; border-radius: 25px; overflow: hidden;
        margin-bottom: 30px; box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        background: #cbd5e1;
    }
    .img-wrapper img { width: 100%; height: 100%; object-fit: cover; }

    .card-base {
        background: white; padding: 25px; border-radius: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .punto-item { border-left: 6px solid #0ea5e9; }
    
    .logistica-box {
        background: #0f172a; color: white; padding: 40px;
        border-radius: 30px; margin-top: 40px;
    }
    .grid-info {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px;
    }
    
    .btn-viaje {
        display: inline-block; padding: 10px 18px; border-radius: 8px;
        text-decoration: none; font-weight: 700; font-size: 0.8rem;
        margin-top: 10px; margin-right: 8px; text-align: center;
    }
    .btn-map { background: #0ea5e9; color: white !important; }
    .btn-tkt { background: #f59e0b; color: white !important; }
    .btn-link-log { 
        display: block; border: 1px solid #38bdf8; color: #38bdf8 !important;
        text-align: center; padding: 8px; border-radius: 6px; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión. Verifica tus Secrets.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS PASSPORT ✈️</h1><p>Terminal de Logística Global</p></div>', unsafe_allow_html=True)

# 3. ENTRADA DE DATOS
c1, c2, c3 = st.columns(3)
with c1: nac_in = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: París, Francia")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("SINCRONIZAR DESTINO", use_container_width=True):
    if dest_raw:
        destino = seguro(dest_raw)
        nacionalidad = seguro(nac_in)
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        
        # Cache de Supabase
        res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
        guia = res.data[0]['datos_jsonb'] if res.data else None
        
        if not guia:
            with st.spinner("Generando inteligencia de viaje..."):
                prompt = f"""Genera un JSON para {nacionalidad} en {destino} ({lang}).
                JSON: {{
                    "resenia": "...",
                    "puntos": [{{ "n": "Lugar", "d": "Info", "h": "Horas", "p": "Precio" }}],
                    "cambio": "Zonas de cambio seguras",
                    "hospital": "Centros médicos recomendados",
                    "alojamiento": "Mejores barrios",
                    "clima": "Resumen clima",
                    "autos": "Rentadoras",
                    "consulado": "Datos consulado"
                }}"""
                chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # --- SOLUCIÓN IMAGEN: Forzado de refresco con ID dinámico ---
            t = int(time.time())
            img_query = urllib.parse.quote(f"landscape,city,{destino}")
            st.markdown(f"""
                <div class="img-wrapper">
                    <img src="https://source.unsplash.com/featured/1200x500?landscape,city,{img_query}&sig={t}" 
                    onerror="this.src='https://loremflickr.com/1200/500/city,landscape,{img_query}?random={t}'">
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="card-base"><h2>Explorando {destino}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            # --- SECCIÓN TICKETS ---
            st.subheader("🎟️ Itinerario y Entradas Oficiales")
            for p in guia.get('puntos', []):
                nombre = seguro(p.get('n'))
                q_map = urllib.parse.quote(f"{nombre} {destino}")
                st.markdown(f"""
                <div class="card-base punto-item">
                    <h4>{nombre}</h4>
                    <p>{p.get('d')}</p>
                    <small><b>⏰ Horario:</b> {p.get('h')} | <b>💰 Costo:</b> {p.get('p')}</small><br>
                    <a href="https://www.google.com/maps/search/?api=1&query={q_map}" target="_blank" class="btn-viaje btn-map">🗺️ MAPA</a>
                    <a href="https://www.google.com/search?q=official+tickets+{q_map}" target="_blank" class="btn-viaje btn-tkt">🎟️ TICKETS</a>
                </div>
                """, unsafe_allow_html=True)

            # --- SECCIÓN LOGÍSTICA (Hospital y Cambio restaurados y fijos) ---
            st.markdown(f"""
            <div class="logistica-box">
                <h2 style="color:white; text-align:center; margin-bottom:30px;">📊 Datos Críticos de Logística</h2>
                <div class="grid-info">
                    <div class="info-card">
                        <h4 style="color:#38bdf8;">💰 Casas de Cambio</h4>
                        <p>{guia.get('cambio')}</p>
                        <a href="https://www.google.com/maps/search/currency+exchange+{urllib.parse.quote(destino)}" target="_blank" class="btn-link-log">VER EN MAPA</a>
                    </div>
                    <div class="info-card">
                        <h4 style="color:#38bdf8;">🏥 Hospitales</h4>
                        <p>{guia.get('hospital')}</p>
                        <a href="https://www.google.com/maps/search/hospital+{urllib.parse.quote(destino)}" target="_blank" class="btn-link-log">CENTROS MÉDICOS</a>
                    </div>
                    <div class="info-card">
                        <h4 style="color:#38bdf8;">🏛️ Consulado ({nacionalidad})</h4>
                        <p>{guia.get('consulado')}</p>
                        <a href="https://www.google.com/search?q=consulado+{urllib.parse.quote(nacionalidad)}+en+{urllib.parse.quote(destino)}" target="_blank" class="btn-link-log">SITIO OFICIAL</a>
                    </div>
                    <div class="info-card">
                        <h4 style="color:#38bdf8;">☀️ Clima</h4>
                        <p>{guia.get('clima')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)