import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto): 
    if not texto or texto == "None": return "Dato no disponible"
    return str(texto).strip().title()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background: #f8fafc; font-family: 'Inter', sans-serif; }
    
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 50px 20px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 40px;
    }
    .header-container h1 { font-weight: 800; font-size: 3.2rem; letter-spacing: -1.5px; margin: 0; }
    
    /* Contenedor de imagen blindado */
    .img-frame {
        width: 100%;
        height: 450px;
        background-color: #e2e8f0;
        border-radius: 25px;
        margin-bottom: 35px;
        overflow: hidden;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    .img-frame img {
        width: 100%;
        height: 100%;
        object-fit: cover;
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
except:
    st.error("Error en las credenciales.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS PASSPORT ✈️</h1><p>Logística y Tickets Oficiales</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac_in = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: París, Francia")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = seguro(nac_in)
destino = seguro(dest_raw)

if st.button("GENERAR LOGÍSTICA DE VIAJE", use_container_width=True):
    if dest_raw:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
        if res.data: guia = res.data[0]['datos_jsonb']
        
        if not guia:
            with st.spinner(f"Analizando infraestructura en {destino}..."):
                prompt = f"""Genera un JSON para {nacionalidad} en {destino}. Idioma: {lang}. 
                JSON: {{ "resenia": "", "puntos": [{{ "n": "", "d": "", "h": "", "p": "" }}], "cambio": "", "autos": "", "alojamiento": "", "clima": "", "consulado": "", "hospital": "" }}"""
                chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # SOLUCIÓN DEFINITIVA PARA LA IMAGEN
            # Usamos una URL de alta disponibilidad con tags específicos
            img_query = urllib.parse.quote(f"landscape,city,{destino}")
            st.markdown(f"""
                <div class="img-frame">
                    <img src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80" 
                    onerror="this.src='https://loremflickr.com/1200/500/{img_query}'" 
                    alt="Foto paisaje de la ciudad de {destino}">
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="resenia-box"><h2>Explorando {destino}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            st.subheader("📍 Lugares Recomendados")
            for p in guia.get('puntos', []):
                n_p = seguro(p.get('n'))
                link_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{n_p} {destino}')}"
                link_tkt = f"https://www.google.com/search?q=official+tickets+{urllib.parse.quote(f'{n_p} {destino}')}"
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n_p}</h3>
                    <p>{p.get('d')}</p>
                    <small><b>Horario:</b> {p.get('h')} | <b>Precio:</b> {p.get('p')}</small><br>
                    <a href="{link_mapa}" target="_blank" class="btn-action btn-primary">🗺️ MAPA</a>
                    <a href="{link_tkt}" target="_blank" class="btn-action btn-secondary">🎟️ TICKETS</a>
                </div>
                """, unsafe_allow_html=True)

            # LOGÍSTICA
            st.markdown(f"""
            <div class="info-relevante-box">
                <div class="info-grid">
                    <div class="info-item">
                        <h4>🏨 Alojamiento</h4><p>{guia.get('alojamiento')}</p>
                        <a href="https://www.airbnb.com/s/{urllib.parse.quote(destino)}/homes" target="_blank" class="btn-link">🔗 AIRBNB</a>
                    </div>
                    <div class="info-item">
                        <h4>🚗 Autos</h4><p>{guia.get('autos')}</p>
                        <a href="https://www.rentalcars.com/search-results?locationName={urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 RENTACARS</a>
                    </div>
                    <div class="info-item">
                        <h4>☀️ Clima</h4><p>{guia.get('clima')}</p>
                        <a href="https://www.google.com/search?q=weather+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 DETALLE</a>
                    </div>
                    <div class="info-item">
                        <h4>🏛️ Consulado</h4><p>{guia.get('consulado')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)