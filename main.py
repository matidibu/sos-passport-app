import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE (Confianza y Alegría)
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5fcfd 0%, #ffffff 100%); color: #2c3e50; }
    .main-title { color: #007d8a; font-weight: 800; font-size: 3rem !important; margin-bottom: 0px; }
    .punto-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 10px 25px rgba(0,125,138,0.08);
        margin-bottom: 25px;
        border-top: 6px solid #00acc1;
    }
    .emergencia-box { padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #e0f2f1; }
    .label-mini { font-weight: bold; color: #007d8a; font-size: 0.7rem; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión. Verifica los Secrets.")
    st.stop()

# 3. HOME (Solo 3 campos, directo)
st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("Explorá tu destino con la tranquilidad de tenerlo todo bajo control.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Madrid, España")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡GENERAR MI EXPERIENCIA!", use_container_width=True):
    if dest and nac:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Diseñando tu viaje ideal (Puntos 5-10)..."):
                prompt = f"""
                Genera una guía alegre para un {nac} en {dest} en {lang}.
                Incluye: 8 puntos de interés.
                Responde JSON:
                {{
                    "emergencia": {{"consulado_info": "Nombre, dirección y tel", "hospital_info": "Nombre y dirección"}},
                    "puntos": [
                        {{
                            "nombre": "Lugar",
                            "resenia": "Reseña vibrante",
                            "ranking": "⭐⭐⭐⭐⭐",
                            "horario": "Horarios",
                            "precio": "Precio entradas",
                            "link_ticket": "URL o 'No requiere'"
                        }}
                    ]
                }}
                """
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.divider()
            # SECCIÓN EMERGENCIAS LIMPIA (Arregla foto d07ca2)
            st.subheader("🛡️ Viajá con Confianza")
            em = guia.get('emergencia', {})
            ce1, ce2 = st.columns(2)
            with ce1: 
                st.markdown(f'<div class="emergencia-box" style="background:#e3f2fd;"><span class="label-mini">🏛️ Consulado</span><br>{em.get("consulado_info", "Consultar en destino")}</div>', unsafe_allow_html=True)
            with ce2: 
                st.markdown(f'<div class="emergencia-box" style="background:#f1f8e9;"><span class="label-mini">🏥 Hospital</span><br>{em.get("hospital_info", "Consultar en destino")}</div>', unsafe_allow_html=True)

            # PUNTOS DE INTERÉS (Arregla foto cf8ce0 y d0725a)
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            for i, p in enumerate(guia.get('puntos', [])):
                with st.container():
                    st.markdown(f"""
                    <div class="punto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="margin:0; color:#007d8a;">{p.get('nombre')}</h2>
                            <span>{p.get('ranking')}</span>
                        </div>
                        <p style="margin-top:15px; font-size:1.1rem;">{p.get('resenia', p.get('reseña', 'No hay descripción disponible.'))}</p>
                        <div style="display:flex; gap:30px; margin-top:15px; background:#f9f9f9; padding:10px; border-radius:10px;">
                            <span><b>⏰ Horario:</b> {p.get('horario')}</span>
                            <span style="color:#2e7d32;"><b>💰 Entrada:</b> {p.get('precio')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        q = urllib.parse.quote(f"{p['nombre']} {dest}")
                        st.link_button("🗺️ VER MAPA", f"https://www.google.com/maps/search/{q}", use_container_width=True, key=f"map_{i}")
                    with b2:
                        link = p.get('link_ticket', 'No requiere')
                        if "http" in str(link):
                            st.link_button("🎟️ ADQUIRIR ENTRADAS", link, use_container_width=True, key=f"tix_{i}")
                        else:
                            st.button(f"✨ {link}", disabled=True, use_container_width=True, key=f"info_{i}")