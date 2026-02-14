import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0faff 0%, #ffffff 100%); }
    .main-title { color: #00838f; font-weight: 800; font-size: 3.5rem !important; margin-bottom: 0; }
    .punto-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0px 10px 30px rgba(0, 131, 143, 0.1);
        margin-bottom: 15px; border-left: 10px solid #00acc1;
    }
    .header-img { 
        width: 100%; height: 380px; object-fit: cover; 
        border-radius: 25px; margin-bottom: 25px; 
        box-shadow: 0px 10px 25px rgba(0,0,0,0.15);
        border: 4px solid white;
    }
    .info-tag { background: #e0f7fa; padding: 5px 12px; border-radius: 10px; font-size: 0.85rem; color: #006064; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en Secrets. Verificá la conexión.")
    st.stop()

st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)

# 3. INTERFAZ
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 ¿A dónde vas?", placeholder="Ej: París, Francia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡GENERAR MI EXPERIENCIA!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Preparando todo para {dest}..."):
                prompt = f"""Genera una guía de viaje para un {nac} en {dest} en {lang}.
                Responde ÚNICAMENTE un JSON con esta estructura exacta:
                {{
                    "consulado": "info",
                    "hospital": "info",
                    "puntos": [{{ "nombre": "Lugar", "resenia": "Breve descripción", "horario": "Info", "precio": "Info", "url_ticket": "link" }}]
                }}"""
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # 4. IMAGEN (La que ya te funcionaba)
            img_dest = dest.replace(' ', ',')
            st.markdown(f'<img src="https://loremflickr.com/1200/500/{img_dest},landmark,city/all" class="header-img">', unsafe_allow_html=True)
            
            # 5. SEGURIDAD
            st.subheader("🛡️ Seguridad y Salud")
            s1, s2 = st.columns(2)
            s1.info(f"🏛️ **Asistencia Consular:**\n\n{guia.get('consulado', 'Consultar online')}")
            s2.success(f"🏥 **Hospital Recomendado:**\n\n{guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            # 6. RENDERIZADO ROBUSTO DE PUNTOS
            # Buscamos la lista de puntos sin importar cómo la llame la IA
            lista_puntos = guia.get('puntos', [])
            if not lista_puntos:
                # Si no está en 'puntos', buscamos la primera lista que aparezca en el JSON
                for k, v in guia.items():
                    if isinstance(v, list):
                        lista_puntos = v
                        break

            for i, p in enumerate(lista_puntos):
                nombre = p.get('nombre', 'Lugar Turístico')
                
                # Usamos una sola columna para evitar el error de renderizado de los botones
                st.markdown(f"""
                <div class="punto-card">
                    <h3 style="margin:0; color:#00838f;">{nombre}</h3>
                    <p style="margin:10px 0; font-size:1.05rem; color:#444;">{p.get('resenia', '')}</p>
                    <span class="info-tag">⏰ {p.get('horario')}</span>
                    <span class="info-tag">💰 {p.get('precio')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Botones debajo de la tarjeta
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    q_map = urllib.parse.quote(f"{nombre} {dest}")
                    st.link_button("🗺️ VER MAPA", f"https://www.google.com/maps/search/?api=1&query={q_map}", use_container_width=True, key=f"map_{i}")
                with col_btn2:
                    t_url = p.get('url_ticket', '')
                    if "http" not in str(t_url):
                        q_tkt = urllib.parse.quote(f"tickets oficiales {nombre} {dest}")
                        t_url = f"https://www.google.com/search?q={q_tkt}"
                    st.link_button("🎟️ TICKETS / PAGOS", t_url, use_container_width=True, key=f"tkt_{i}")