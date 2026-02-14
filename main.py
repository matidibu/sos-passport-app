import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto): 
    if not texto: return "Dato no disponible"
    return str(texto).strip().title()

# CSS Personalizado: Estilo Moderno y Profesional
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    .stApp { background: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    .header-container {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 60px 20px;
        border-radius: 0 0 30px 30px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        font-weight: 800;
        font-size: 3.5rem;
        letter-spacing: -2px;
        margin-bottom: 10px;
    }
    
    .header-container p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 400;
    }

    .resenia-box {
        background: white; padding: 30px; border-radius: 20px; margin-bottom: 30px;
        border-left: 10px solid #0ea5e9; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .punto-card {
        background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-bottom: 4px solid #0ea5e9;
        transition: transform 0.2s;
    }
    
    .punto-card:hover { transform: translateY(-5px); }

    .info-relevante-box {
        background: #0f172a; color: #f8fafc; padding: 50px;
        border-radius: 30px; margin-top: 50px;
    }
    
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 30px;
    }

    .info-item h4 {
        color: #38bdf8;
        border-bottom: 1px solid #334155;
        padding-bottom: 10px;
        margin-bottom: 15px;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }

    .btn-map {
        background: #0ea5e9; color: white !important; padding: 10px 20px;
        border-radius: 8px; text-decoration: none; font-weight: 700;
        display: inline-block; margin-top: 15px;
    }

    .disclaimer {
        margin-top: 40px; padding: 20px; border-radius: 15px;
        background: rgba(255, 255, 255, 0.05); font-size: 0.85rem; color: #94a3b8;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en las credenciales de conexión.")
    st.stop()

st.markdown("""
    <div class="header-container">
        <h1>SOS PASSPORT ✈️</h1>
        <p>Logística inteligente para el viajero global</p>
    </div>
    """, unsafe_allow_html=True)

# 3. INTERFAZ DE BÚSQUEDA
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1: nac_in = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest_in = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Madrid, Tokyo, Roma...")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

nacionalidad = seguro(nac_in)
destino = seguro(dest_in)

if st.button("INICIAR PLANIFICACIÓN", use_container_width=True):
    if dest_in:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Configurando logística para {destino}..."):
                prompt = f"""Genera un JSON para un viajero {nacionalidad} en {destino}. Idioma: {lang}.
                REGLAS: Ortografía perfecta, nombres propios con Mayúscula.
                JSON:
                {{
                    "resenia": "Descripción profesional de la ciudad",
                    "puntos": [{{ "n": "Lugar", "d": "Info", "h": "Horas", "p": "Precio" }}],
                    "casas_cambio": "Nombres de zonas o locales confiables para cambiar dinero",
                    "renta_autos": "Empresas principales y zonas de retiro",
                    "alojamiento": "Mejores zonas para Airbnb y hoteles recomendados",
                    "clima": "Reporte de 7 días",
                    "consulado": "Datos de contacto consulado de {nacionalidad}",
                    "hospital": "Centro de salud recomendado"
                }}"""
                chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # A. IMAGEN DE CABECERA
            st.image(f"https://loremflickr.com/1200/500/{urllib.parse.quote(destino)},city,architecture", use_container_width=True)
            
            # B. RESEÑA
            st.markdown(f'<div class="resenia-box"><h2>Explorando {destino}</h2><p>{guia.get("resenia")}</p></div>', unsafe_allow_html=True)

            # C. PUNTOS IMPERDIBLES
            st.subheader("📍 Itinerario Sugerido")
            for p in guia.get('puntos', []):
                n_p = seguro(p.get('n'))
                link_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{n_p} {destino}')}"
                st.markdown(f"""
                <div class="punto-card">
                    <h3>{n_p}</h3>
                    <p>{p.get('d')}</p>
                    <small><b>⏰ Horario:</b> {p.get('h')} | <b>💰 Precio:</b> {p.get('p')}</small><br>
                    <a href="{link_mapa}" target="_blank" class="btn-map">🗺️ VER EN MAPA</a>
                </div>
                """, unsafe_allow_html=True)

            # D. INFORMACIÓN RELEVANTE (Logística Completa)
            st.markdown(f"""
            <div class="info-relevante-box">
                <h2 style="color:#ffffff; margin-bottom:40px; text-align:center;">📊 Logística y Seguridad</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <h4>💰 Finanzas y Cambio</h4>
                        <p>{guia.get('casas_cambio')}</p>
                    </div>
                    <div class="info-item">
                        <h4>🚗 Movilidad</h4>
                        <p>{guia.get('renta_autos')}</p>
                    </div>
                    <div class="info-item">
                        <h4>🏨 Alojamiento</h4>
                        <p>{guia.get('alojamiento')}</p>
                    </div>
                    <div class="info-item">
                        <h4>☀️ Clima</h4>
                        <p>{guia.get('clima')}</p>
                    </div>
                    <div class="info-item">
                        <h4>🏛️ Consulado ({nacionalidad})</h4>
                        <p>{guia.get('consulado')}</p>
                    </div>
                    <div class="info-item">
                        <h4>🏥 Salud</h4>
                        <p>{guia.get('hospital')}</p>
                    </div>
                </div>
                <div class="disclaimer">
                    <b>AVISO DE RESPONSABILIDAD:</b> SOS Passport es una plataforma informativa basada en modelos de inteligencia artificial (Datos a Feb 2026). 
                    No garantizamos la disponibilidad de locales de renta, hoteles o variaciones climáticas. 
                    Toda la información debe ser contrastada con fuentes oficiales y proveedores directos antes de realizar reservas o transacciones.
                </div>
            </div>
            """, unsafe_allow_html=True)