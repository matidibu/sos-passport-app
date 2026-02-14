import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto): 
    if not texto or texto == "None": return "Información no disponible"
    return str(texto).strip().title()

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
    .header-container p { font-size: 1.1rem; opacity: 0.7; margin-top: 10px; }

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
    .info-item h4 {
        color: #38bdf8; border-bottom: 1px solid #334155;
        padding-bottom: 10px; margin-bottom: 15px;
        text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1.2px;
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
    st.error("Error en las credenciales (Secrets).")
    st.stop()

st.markdown("""
    <div class="header-container">
        <h1>SOS PASSPORT ✈️</h1>
        <p>Logística de Viaje y Tickets Oficiales</p>
    </div>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2, c3 = st.columns(3)
with c1: nac_in = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest_raw = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Roma, Italia")
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
        except: pass
        
        if not guia:
            with st.spinner(f"Analizando {destino}..."):
                prompt = f"""Genera un JSON para un viajero {nacionalidad} en {destino}. Idioma: {lang}. 
                JSON:
                {{
                    "resenia": "Breve descripción profesional",
                    "puntos": [{{ "n": "Lugar", "d": "Detalle", "h": "Horas", "p": "Precio" }}],
                    "cambio": "Datos casas cambio",
                    "autos": "Rentadoras",
                    "alojamiento": "Airbnb y Hoteles",
                    "clima": "Reporte 7 días",
                    "consulado": "Contacto",
                    "hospital": "Salud"
                }}"""
                chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # CORRECCIÓN DE IMAGEN: Uso de Unsplash con parámetros de búsqueda precisos
            img_url = f"https://source.unsplash.com/1200x500/?city,landscape,{urllib.parse.quote(destino)}"
            # Alternativa si Unsplash falla:
            st.markdown(f"""
                <div style="width:100%; height:400px; border-radius:20px; overflow:hidden; margin-bottom:30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
                    <img src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=1200&q=80" style="width:100%; height:100%; object-fit:cover;" 
                    onerror="this.src='https://loremflickr.com/1200/500/city,landscape,{urllib.parse.quote(destino)}'">
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f'<div class="resenia-box"><h2>Sobre {destino}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS IMPERDIBLES
            st.subheader("📍 Lugares Recomendados")
            puntos = guia.get('puntos', [])
            for p in puntos:
                n_p = seguro(p.get('n'))
                link_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{n_p} {destino}')}"
                link_tkt = f"https://www.google.com/search?q=official+tickets+{urllib.parse.quote(f'{n_p} {destino}')}"
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n_p}</h3>
                    <p>{p.get('d', '')}</p>
                    <small><b>⏰ Horario:</b> {p.get('h')} | <b>💰 Precio:</b> {p.get('p')}</small><br>
                    <div style="margin-top:10px;">
                        <a href="{link_mapa}" target="_blank" class="btn-action btn-primary">🗺️ VER MAPA</a>
                        <a href="{link_tkt}" target="_blank" class="btn-action btn-secondary">🎟️ COMPRAR ENTRADAS</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # D. LOGÍSTICA
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:white; margin-bottom:40px; text-align:center;">📊 Logística</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <h4>🏨 Alojamiento</h4>
                        <p>{guia.get('alojamiento')}</p>
                        <a href="https://www.airbnb.com/s/{urllib.parse.quote(destino)}/homes" target="_blank" class="btn-link">🔗 BUSCAR EN AIRBNB</a>
                    </div>
                    <div class="info-item">
                        <h4>🚗 Renta de Autos</h4>
                        <p>{guia.get('autos')}</p>
                        <a href="https://www.rentalcars.com/search-results?locationName={urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 VER RENTADORAS</a>
                    </div>
                    <div class="info-item">
                        <h4>💰 Casas de Cambio</h4>
                        <p>{guia.get('cambio')}</p>
                        <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'currency exchange {destino}')}" target="_blank" class="btn-link">🔗 UBICACIONES</a>
                    </div>
                    <div class="info-item">
                        <h4>☀️ Clima</h4>
                        <p>{guia.get('clima')}</p>
                        <a href="https://www.google.com/search?q=weather+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 PRONÓSTICO</a>
                    </div>
                    <div class="info-item">
                        <h4>🏛️ Consulado ({nacionalidad})</h4>
                        <p>{guia.get('consulado')}</p>
                        <a href="https://www.google.com/search?q=consulado+{urllib.parse.quote(nacionalidad)}+en+{urllib.parse.quote(destino)}" target="_blank" class="btn-link">🔗 WEB OFICIAL</a>
                    </div>
                    <div class="info-item">
                        <h4>🏥 Salud</h4>
                        <p>{guia.get('hospital')}</p>
                        <a href="https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'hospital {destino}')}" target="_blank" class="btn-link">🔗 CENTROS MÉDICOS</a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)