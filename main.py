import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse
import re
import time

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f1f5f9; font-family: 'Inter', sans-serif; }
    .main-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .punto-card { background: white; border-radius: 15px; padding: 15px; border-bottom: 4px solid #0ea5e9; margin-bottom: 20px; shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .header { background: #0f172a; color: white; padding: 30px; text-align: center; border-radius: 0 0 20px 20px; margin-bottom: 20px; }
    .btn-link { display: inline-block; padding: 8px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 13px; margin-top: 5px; }
    .btn-map { background: #0ea5e9; color: white !important; }
    .btn-tkt { background: #f59e0b; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
@st.cache_resource
def init_connections():
    try:
        s = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        g = Groq(api_key=st.secrets["GROQ_API_KEY"])
        return s, g
    except:
        return None, None

supabase, client = init_connections()

st.markdown('<div class="header"><h1>SOS PASSPORT ✈️</h1><p>Logística de Viaje Inteligente</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ DE ENTRADA
col1, col2, col3 = st.columns(3)
with col1: nacionalidad = st.text_input("🌎 Nacionalidad", "Argentina")
with col2: destino = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Roma")
with col3: idioma = st.selectbox("🗣️ Idioma", ["Español", "English", "Português"])

if st.button("OBTENER GUÍA COMPLETA", use_container_width=True):
    if not destino:
        st.error("Por favor, ingresa un destino.")
    else:
        search_key = f"{destino.lower()}-{nacionalidad.lower()}-{idioma.lower()}"
        guia = None

        # A. Intentar buscar en Base de Datos
        if supabase:
            try:
                res = supabase.table("guias").select("datos_jsonb").eq("clave_busqueda", search_key).execute()
                if res.data: guia = res.data[0]['datos_jsonb']
            except: pass

        # B. Si no existe, pedir a la IA (Llama 3)
        if not guia and client:
            with st.spinner(f"Generando logística para {destino}..."):
                try:
                    prompt = f"Genera un JSON estrictamente válido para un viajero {nacionalidad} en {destino}. Idioma: {idioma}. JSON: {{ 'resenia': '...', 'puntos': [{{ 'n': 'Lugar', 'd': 'Breve info', 'h': 'Horario', 'p': 'Precio' }}], 'hospital': '...', 'cambio': '...', 'alojamiento': '...' }}"
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    guia = json.loads(completion.choices[0].message.content)
                    if supabase:
                        supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except Exception as e:
                    st.error(f"Error de IA: {e}")

        # C. MOSTRAR RESULTADOS (ESTRUCTURA BLINDADA)
        if guia:
            # Foto principal garantizada
            t = int(time.time())
            img_main = f"https://loremflickr.com/1200/500/{urllib.parse.quote(destino)},city,landscape/all?lock={t}"
            st.image(img_main, use_container_width=True, caption=f"Vista de {destino}")

            # Reseña
            st.markdown(f"""<div class="main-card"><h3>Sobre {destino}</h3><p>{guia.get('resenia', 'No hay descripción disponible.')}</p></div>""", unsafe_allow_html=True)

            # Itinerario
            st.subheader("📍 Itinerario Sugerido")
            puntos = guia.get('puntos', [])
            if isinstance(puntos, list):
                for i, p in enumerate(puntos):
                    nombre = p.get('n', 'Lugar Turístico')
                    desc = p.get('d', 'Sin descripción.')
                    
                    # Foto específica del lugar
                    img_p = f"https://loremflickr.com/800/450/{urllib.parse.quote(nombre)},{urllib.parse.quote(destino)}/all?lock={t+i}"
                    q = urllib.parse.quote(f"{nombre} {destino}")
                    
                    st.markdown(f"""
                    <div class="punto-card">
                        <img src="{img_p}" style="width:100%; height:250px; object-fit:cover; border-radius:10px; margin-bottom:10px;">
                        <h4>{nombre}</h4>
                        <p>{desc}</p>
                        <p style="font-size:0.8rem;"><b>Horario:</b> {p.get('h', 'Verificar')} | <b>Precio:</b> {p.get('p', 'Verificar')}</p>
                        <a href="https://www.google.com/maps/search/?api=1&query={q}" target="_blank" class="btn-link btn-map">🗺️ MAPA</a>
                        <a href="https://www.google.com/search?q=tickets+official+{q}" target="_blank" class="btn-link btn-tkt">🎟️ ENTRADAS</a>
                    </div>
                    """, unsafe_allow_html=True)

            # Logística Final
            st.subheader("📊 Logística y Seguridad")
            c_h, c_c, c_a = st.columns(3)
            with c_h: 
                st.info(f"🏥 **Salud:**\n{guia.get('hospital', 'Consultar emergencias locales.')}")
            with c_c:
                st.warning(f"💰 **Cambio:**\n{guia.get('cambio', 'Usar casas oficiales.')}")
            with c_a:
                st.success(f"🏨 **Alojamiento:**\n{guia.get('alojamiento', 'Zonas recomendadas en Airbnb.')}")
        else:
            st.error("No se pudieron cargar los datos. Reintenta en unos segundos.")