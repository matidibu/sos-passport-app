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
    .main-title { color: #00838f; font-weight: 800; font-size: 3rem !important; }
    .punto-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0px 10px 30px rgba(0, 131, 143, 0.1);
        margin-bottom: 25px; border-top: 8px solid #00acc1;
    }
    .info-tag { background: #e0f7fa; padding: 5px 12px; border-radius: 10px; font-size: 0.85rem; color: #006064; font-weight: bold; margin-right: 5px; }
    .header-img { width: 100%; height: 350px; object-fit: cover; border-radius: 25px; margin-bottom: 20px; border: 4px solid white; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en Secrets.")
    st.stop()

st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)

# 3. INTERFAZ
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", value="París, Francia")
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
            with st.spinner(f"Viajando mentalmente a {dest}..."):
                prompt = f"""Genera una guía detallada para un {nac} en {dest} en {lang}.
                Responde ÚNICAMENTE un JSON con:
                'consulado': 'info', 'hospital': 'info',
                'puntos': [{{'nombre': '..', 'resenia': '..', 'horario': '..', 'precio': '..', 'url_ticket': '..'}}]"""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # FOTO DEL DESTINO REAL (Usando Source Unsplash con keywords precisas)
            img_query = urllib.parse.quote(dest)
            st.markdown(f'<img src="https://source.unsplash.com/featured/1200x500?{img_query},landmark" class="header-img">', unsafe_allow_html=True)
            
            st.subheader("🛡️ Seguridad")
            s1, s2 = st.columns(2)
            s1.info(f"🏛️ **Consulado:** {guia.get('consulado')}")
            s2.success(f"🏥 **Hospital:** {guia.get('hospital')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest}")
            
            # Buscador de lista para asegurar que se vean
            puntos = guia.get('puntos', [])
            
            for i, p in enumerate(puntos):
                nombre = p.get('nombre', 'Lugar')
                tkt = p.get('url_ticket', '')
                
                with st.container():
                    st.markdown(f"""
                    <div class="punto-card">
                        <h3 style="margin:0; color:#00838f;">{nombre}</h3>
                        <p style="margin:10px 0;">{p.get('resenia', '')}</p>
                        <span class="info-tag">⏰ {p.get('horario')}</span>
                        <span class="info-tag">💰 {p.get('precio')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botones de acción
                    b1, b2 = st.columns(2)
                    with b1:
                        q_map = urllib.parse.quote(f"{nombre} {dest}")
                        st.link_button("🗺️ VER MAPA", f"https://www.google.com/maps/search/?api=1&query={q_map}", use_container_width=True)
                    with b2:
                        # Si no hay link, buscamos en GetYourGuide automáticamente
                        q_tkt = urllib.parse.quote(f"tickets {nombre} {dest}")
                        link_final = tkt if "http" in str(tkt) else f"https://www.getyourguide.com/s/?q={q_tkt}"
                        st.link_button("🎟️ COMPRAR TICKETS", link_final, use_container_width=True)