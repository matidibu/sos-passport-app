import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto): 
    if not texto or texto == "None": return "Información no disponible"
    return str(texto).strip().title()

# Estilos CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background: #f8fafc; font-family: 'Inter', sans-serif; }
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 50px 20px; border-radius: 0 0 30px 30px;
        color: white; text-align: center; margin-bottom: 40px;
    }
    .img-container {
        width:100%; height:450px; border-radius:25px; overflow:hidden; 
        margin-bottom:35px; box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    .resenia-box {
        background: white; padding: 30px; border-radius: 20px; 
        border-left: 10px solid #0ea5e9; margin-bottom: 30px;
    }
    .punto-card {
        background: white; border-radius: 20px; padding: 25px; margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-bottom: 5px solid #0ea5e9;
    }
    .btn-action {
        display: inline-block; padding: 10px 20px; border-radius: 8px;
        text-decoration: none; font-size: 0.85rem; font-weight: 700; margin-top: 10px; margin-right: 10px;
    }
    .btn-primary { background: #0ea5e9; color: white !important; }
    .btn-secondary { background: #f59e0b; color: white !important; }
    .info-relevante-box {
        background: #0f172a; color: white; padding: 50px; border-radius: 30px; margin-top: 40px;
    }
    .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
    .btn-link { 
        display: block; background: #1e293b; color: #38bdf8 !important; border: 1px solid #38bdf8;
        padding: 8px; border-radius: 6px; text-decoration: none; text-align: center; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en credenciales.")
    st.stop()

st.markdown('<div class="header-container"><h1>SOS PASSPORT ✈️</h1><p>Logística y Tickets Oficiales</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac_in = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Tokyo, Japón")
with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = seguro(nac_in)
destino = seguro(dest_raw)

if st.button("GENERAR GUÍA", use_container_width=True):
    if dest_raw:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Buscando datos..."):
                prompt = f"Genera un JSON para {nacionalidad} en {destino}. Idioma: {lang}. Estructura: {{'resenia':'','puntos':[{{'n':'','d':'','h':'','p':''}}],'cambio':'','autos':'','alojamiento':'','clima':'','consulado':'','hospital':''}}"
                chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # SOLUCIÓN IMAGEN: Link dinámico para evitar que se quede trabada
            timestamp = int(time.time()) # Evita el caché del navegador
            img_query = urllib.parse.quote(f"landscape city {destino}")
            # Usamos una URL que genera una imagen distinta basada en el destino
            foto_url = f"https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=1200" # Default
            # Inyectamos la imagen con un truco de CSS para que sea dinámica
            st.markdown(f"""
                <div class="img-container">
                    <img src="https://source.unsplash.com/featured/1200x500?landscape,city,{img_query}&sig={timestamp}" 
                    style="width:100%; height:100%; object-fit:cover;" 
                    onerror="this.src='https://loremflickr.com/1200/500/city,landscape,{img_query}'">
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            st.subheader("📍 Puntos de Interés")
            for p in guia.get('puntos', []):
                n_p = seguro(p.get('n'))
                link_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{n_p} {destino}')}"
                link_tkt = f"https://www.google.com/search?q=official+tickets+{urllib.parse.quote(f'{n_p} {destino}')}"
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n_p}</h3>
                    <p>{p.get('d')}</p>
                    <small><b>⏰ Horario:</b> {p.get('h')} | <b>💰 Precio:</b> {p.get('p')}</small><br>
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
                        <a href="https://www.airbnb.com/s/{urllib.parse.quote(destino)}/homes" target="_blank" class="btn-link">AIRBNB</a>
                    </div>
                    <div class="info-item">
                        <h4>🚗 Autos</h4><p>{guia.get('autos')}</p>
                        <a href="https://www.rentalcars.com/search-results?locationName={urllib.parse.quote(destino)}" target="_blank" class="btn-link">RENTALCARS</a>
                    </div>
                    <div class="info-item">
                        <h4>💰 Cambio</h4><p>{guia.get('cambio')}</p>
                        <a href="https://www.google.com/maps/search/currency+exchange+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">MAPA</a>
                    </div>
                    <div class="info-item">
                        <h4>☀️ Clima</h4><p>{guia.get('clima')}</p>
                        <a href="https://www.google.com/search?q=weather+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">DETALLE</a>
                    </div>
                    <div class="info-item">
                        <h4>🏛️ Consulado</h4><p>{guia.get('consulado')}</p>
                    </div>
                    <div class="info-item">
                        <h4>🏥 Salud</h4><p>{guia.get('hospital')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)