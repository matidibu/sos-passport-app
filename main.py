import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json

# 1. ESTILO VIBRANTE Y DE DESCANSO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0faff 0%, #ffffff 100%); }
    .main-title { color: #00838f; font-weight: 800; font-size: 3.5rem !important; margin-bottom: 0; }
    .punto-card {
        background: white; border-radius: 20px; padding: 30px;
        box-shadow: 0px 15px 35px rgba(0, 131, 143, 0.1);
        margin-bottom: 30px; border-left: 10px solid #00acc1;
        transition: transform 0.3s;
    }
    .punto-card:hover { transform: translateY(-5px); }
    .info-tag { background: #e0f7fa; padding: 8px 15px; border-radius: 15px; font-size: 0.9rem; color: #006064; font-weight: bold; margin-right: 10px; }
    .map-btn {
        display: inline-block; padding: 10px 20px; background-color: #00838f; color: white !important;
        text-decoration: none; border-radius: 25px; font-weight: bold; margin-top: 20px;
        box-shadow: 0px 4px 10px rgba(0,131,143,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión. Verificá tus Secrets.")
    st.stop()

# 3. INTERFAZ DE INICIO
st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu compañero de viaje para descubrir el mundo sin estrés.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 ¿A dónde vas?", placeholder="Ej: Londres, Reino Unido")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡GENERAR MI EXPERIENCIA!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        # Consultar DB
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        # Generar con IA si no existe
        if not guia:
            with st.spinner(f"Sincronizando lo mejor de {dest}..."):
                prompt = f"""Genera una guía alegre para un {nac} en {dest} en {lang}. 
                Responde EXCLUSIVAMENTE un JSON con:
                'consulado': 'Nombre, dirección y teléfono',
                'hospital': 'Nombre y dirección del mejor hospital cercano',
                'puntos': [{{'nombre': '..', 'resenia': '..', 'horario': '..', 'precio': '..'}}]
                Mínimo 7 puntos, máximo 10. Sé específico con los precios en moneda local."""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.divider()
            # Imagen de cabecera dinámica
            st.image(f"https://source.unsplash.com/1600x600/?{dest.replace(' ', ',')},travel", use_container_width=True)
            
            # SECCIÓN SEGURIDAD
            st.subheader("🛡️ Viajá con Tranquilidad")
            cs1, cs2 = st.columns(2)
            cs1.info(f"🏛️ **Asistencia Consular:**\n\n{guia.get('consulado', 'Consultar online')}")
            cs2.success(f"🏥 **Salud y Emergencias:**\n\n{guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            puntos = guia.get('puntos', [])
            for i, p in enumerate(puntos):
                nombre = str(p.get('nombre', 'Lugar Turístico'))
                
                st.markdown(f"""
                <div class="punto-card">
                    <h2 style="margin:0; color:#00838f;">{nombre}</h2>
                    <p style="margin:15px 0; font-size:1.1rem; line-height:1.6; color:#444;">{p.get('resenia', '')}</p>
                    <div style="margin-top: 15px;">
                        <span class="info-tag">⏰ {p.get('horario', 'Consultar')}</span>
                        <span class="info-tag">💰 {p.get('precio', 'Variable')}</span>
                    </div>
                    <br>
                    <a href="https://www.google.com/maps/search/{nombre.replace(' ', '+')}+{dest.replace(' ', '+')}" 
                       target="_blank" class="map-btn">🗺️ VER EN MAPA</a>
                </div>
                """, unsafe_allow_html=True)