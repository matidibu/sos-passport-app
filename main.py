import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

def seguro(texto, default="Información no disponible"):
    if not texto or str(texto).lower() == "none": return default
    return str(texto).strip().title()

def limpiar_json(texto):
    try:
        match = re.search(r'\{.*\}', texto, re.DOTALL)
        return match.group(0) if match else texto
    except: return texto

# 2. ESTILOS
st.markdown("""
    <style>
    .stApp { background: #f8fafc; font-family: 'Inter', sans-serif; }
    .header-container { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 40px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-bottom: 30px; }
    .resenia-box { background: white; padding: 25px; border-radius: 15px; border-left: 8px solid #0ea5e9; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .punto-card { background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .info-relevante-box { background: #0f172a; color: white; padding: 30px; border-radius: 20px; margin-top: 30px; }
    .grid-logistica { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
    .btn-viaje { display: inline-block; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px; margin-right: 10px; font-size: 14px; }
    .btn-mapa { background: #0ea5e9; color: white !important; }
    .btn-tkt { background: #f59e0b; color: white !important; }
    .btn-log { display: block; text-align: center; border: 1px solid #38bdf8; color: #38bdf8 !important; padding: 8px; border-radius: 5px; margin-top: 10px; text-decoration: none; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXIONES
supabase = None
client = None
try:
    if "SUPABASE_URL" in st.secrets:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except: st.error("Error en Secrets.")

st.markdown('<div class="header-container"><h1>SOS PASSPORT ✈️</h1><p>Logística y Tickets en Tiempo Real</p></div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
with c2: dest = st.text_input("📍 Ciudad", placeholder="Ej: París")
with c3: lng = st.selectbox("🗣️ Idioma", ["Español", "English", "Português"])

if st.button("GENERAR GUÍA", use_container_width=True):
    if not dest:
        st.warning("Escribe un destino.")
    else:
        clave = f"{dest.lower()}-{nac.lower()}-{lng.lower()}"
        guia = None
        
        if supabase:
            try:
                res = supabase.table("guias").select("*").eq("clave_busqueda", clave).execute()
                if res.data: guia = res.data[0]['datos_jsonb']
            except: pass

        if not guia and client:
            with st.spinner("Construyendo itinerario..."):
                try:
                    p = f"Genera un JSON para {nac} en {dest} ({lng}). Estructura: {{'resenia':'','puntos':[{{'n':'','d':'','h':'','p':''}}],'cambio':'','autos':'','alojamiento':'','clima':'','consulado':'','hospital':''}}"
                    resp = client.chat.completions.create(messages=[{"role":"user","content":p}], model="llama-3.3-70b-versatile", response_format={"type":"json_object"})
                    guia = json.loads(limpiar_json(resp.choices[0].message.content))
                    if supabase: supabase.table("guias").upsert({"clave_busqueda": clave, "datos_jsonb": guia}).execute()
                except Exception as e: st.error(f"Error IA: {e}")

        if guia:
            # IMAGEN PRINCIPAL
            t = int(time.time())
            st.image(f"https://loremflickr.com/1200/500/landscape,city,{urllib.parse.quote(dest)}/all?lock={t}", use_container_width=True)
            
            # RESEÑA
            st.markdown(f'<div class="resenia-box"><h3>Guía de {seguro(dest)}</h3><p>{guia.get("resenia", "Información breve no disponible.")}</p></div>', unsafe_allow_html=True)

            # PUNTOS DE INTERÉS
            st.subheader("📍 Lugares Recomendados")
            puntos = guia.get('puntos', [])
            if isinstance(puntos, list):
                for i, pt in enumerate(puntos):
                    nombre = seguro(pt.get('n'))
                    desc = pt.get('d', 'Sin descripción.')
                    horario = pt.get('h', 'Consultar')
                    precio = pt.get('p', 'Variable')
                    
                    img_url = f"https://loremflickr.com/800/450/landmark,{urllib.parse.quote(nombre)}/all?lock={t+i}"
                    q = urllib.parse.quote(f"{nombre} {dest}")
                    
                    st.markdown(f"""
                    <div class="punto-card">
                        <img src="{img_url}" style="width:100%; border-radius:12px; height:250px; object-fit:cover; margin-bottom:15px;">
                        <h4>{nombre}</h4>
                        <p>{desc}</p>
                        <small><b>⏰:</b> {horario} | <b>💰:</b> {precio}</small><br>
                        <a href="https://www.google.com/maps/search/?api=1&query={q}" target="_blank" class="btn-viaje btn-mapa">🗺️ VER MAPA</a>
                        <a href="https://www.google.com/search?q=official+tickets+{q}" target="_blank" class="btn-viaje btn-tkt">🎟️ TICKETS</a>
                    </div>
                    """, unsafe_allow_html=True)

            # LOGÍSTICA
            st.markdown(f"""
            <div class="info-relevante-box">
                <h3 style="color:white; text-align:center; margin-bottom:20px;">📊 Datos de Logística</h3>
                <div class="grid-logistica">
                    <div class="log-item">
                        <h5 style="color:#38bdf8;">🏥 Salud / Hospitales</h5>
                        <p>{guia.get('hospital', 'Consultar centros locales.')}</p>
                        <a href="https://www.google.com/maps/search/?api=1&query=hospitales+en+{urllib.parse.quote(dest)}" target="_blank" class="btn-log">BUSCAR HOSPITALES</a>
                    </div>
                    <div class="log-item">
                        <h5 style="color:#38bdf8;">💰 Casas de Cambio</h5>
                        <p>{guia.get('cambio', 'Consultar zonas seguras.')}</p>
                        <a href="https://www.google.com/maps/search/?api=1&query=currency+exchange+in+{urllib.parse.quote(dest)}" target="_blank" class="btn-log">CASAS DE CAMBIO</a>
                    </div>
                    <div class="log-item">
                        <h5 style="color:#38bdf8;">🏨 Alojamiento</h5>
                        <p>{guia.get('alojamiento', 'Info no disponible.')}</p>
                    </div>
                    <div class="log-item">
                        <h5 style="color:#38bdf8;">🏛️ Consulado</h5>
                        <p>{guia.get('consulado', 'Consultar cancillería.')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)