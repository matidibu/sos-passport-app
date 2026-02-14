import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE Y PROFESIONAL
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0faff 0%, #ffffff 100%); }
    .main-title { color: #00838f; font-weight: 800; font-size: 3.5rem !important; margin-bottom: 0; }
    .punto-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0px 10px 30px rgba(0, 131, 143, 0.1);
        margin-bottom: 25px; border-left: 10px solid #00acc1;
    }
    .header-img { 
        width: 100%; height: 400px; object-fit: cover; 
        border-radius: 25px; margin-bottom: 30px; 
        box-shadow: 0px 15px 30px rgba(0,0,0,0.2);
        border: 5px solid white;
    }
    .info-tag { background: #e0f7fa; padding: 6px 12px; border-radius: 12px; font-size: 0.85rem; color: #006064; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en Secrets. Verificá SUPABASE y GROQ.")
    st.stop()

st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía de confianza para explorar y descansar.")

# 3. INTERFAZ DE BÚSQUEDA
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 ¿A dónde vamos?", placeholder="Ej: París, Francia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡GENERAR MI GUÍA!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Diseñando tu viaje a {dest}..."):
                prompt = f"""Genera una guía de viaje para un {nac} en {dest} en {lang}.
                Responde ÚNICAMENTE un JSON con esta estructura:
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
            # 4. IMAGEN DINÁMICA GARANTIZADA
            # Usamos un servicio de placeholder profesional con temática de viaje si falla el específico
            img_dest = dest.replace(' ', ',')
            foto_url = f"https://images.unsplash.com/photo-1500835595367-9917d0268993?auto=format&fit=crop&w=1200&q=80" # Foto por defecto (avión)
            
            # Intentamos cargar una específica del destino
            especifica_url = f"https://loremflickr.com/1200/500/{img_dest},city,landmark/all"
            
            st.markdown(f'<img src="{especifica_url}" class="header-img" onerror="this.src=\'{foto_url}\'">', unsafe_allow_html=True)
            
            # 5. BLOQUE DE SEGURIDAD
            st.subheader("🛡️ Seguridad y Salud")
            s1, s2 = st.columns(2)
            s1.info(f"🏛️ **Asistencia Consular:**\n\n{guia.get('consulado')}")
            s2.success(f"🏥 **Hospital Recomendado:**\n\n{guia.get('hospital')}")

            st.divider()
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            # 6. RENDERIZADO DE PUNTOS
            puntos = guia.get('puntos', [])
            for i, p in enumerate(puntos):
                nombre = p.get('nombre', 'Lugar Turístico')
                
                st.markdown(f"""
                <div class="punto-card">
                    <h3 style="margin:0; color:#00838f;">{nombre}</h3>
                    <p style="margin:10px 0; font-size:1.05rem; color:#444;">{p.get('resenia', '')}</p>
                    <span class="info-tag">⏰ {p.get('horario')}</span>
                    <span class="info-tag">💰 {p.get('precio')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Botones de Acción
                b1, b2 = st.columns(2)
                with b1:
                    q_map = urllib.parse.quote(f"{nombre} {dest}")
                    st.link_button("🗺️ VER EN MAPA", f"https://www.google.com/maps/search/?api=1&query={q_map}", use_container_width=True)
                with b2:
                    t_url = p.get('url_ticket', '')
                    # Si no hay link, armamos uno de búsqueda de tickets
                    if "http" not in str(t_url):
                        q_tkt = urllib.parse.quote(f"tickets oficial {nombre} {dest}")
                        t_url = f"https://www.google.com/search?q={q_tkt}"
                    st.link_button("🎟️ TICKETS / PAGOS", t_url, use_container_width=True)