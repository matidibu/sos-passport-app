import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO "WHITE LABEL" (Identidad propia y limpia)
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    .main-title { color: #ff4b4b; font-weight: 900; font-size: 3.5rem !important; letter-spacing: -2px; }
    .punto-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #f0f0f0;
        border-left: 6px solid #ff4b4b;
        margin-bottom: 25px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.05);
    }
    .emergencia-box {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #eee;
    }
    .label { font-weight: bold; color: #ff4b4b; text-transform: uppercase; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de configuración.")
    st.stop()

# 3. CABECERA
st.markdown('<h1 class="main-title">SOS PASSPORT</h1>', unsafe_allow_html=True)

with st.container(border=True):
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Estocolmo, Suecia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("DESPLEGAR GUÍA INTEGRAL", use_container_width=True):
    if dest and nac:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        # BUSCAR EN DB
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        # GENERAR SI NO EXISTE
        if not guia:
            with st.spinner("Sincronizando con satélites de información..."):
                prompt = f"""
                Genera una guía de 12 puntos para un {nac} en {dest} en {lang}.
                JSON con campos: 
                'consulado' (objeto: nombre, direccion, tel),
                'hospital' (objeto: nombre, direccion, tel),
                'puntos' (lista de 12 objetos: nombre, resenia, ranking, horario, precio, link_compra).
                """
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        # 4. RESULTADOS (Limpieza de datos de las fotos)
        if guia:
            st.divider()
            st.subheader("🚨 Protocolo de Emergencia")
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                con = guia.get('consulado', {})
                st.markdown(f"""<div class="emergencia-box" style="background:#f0f7ff;">
                    <span class="label">🏛️ Consulado</span><br>
                    <b>{con.get('nombre', 'No disponible')}</b><br>
                    📍 {con.get('direccion', '')}<br>📞 {con.get('tel', '')}
                </div>""", unsafe_allow_html=True)
                
            with col_e2:
                hosp = guia.get('hospital', {})
                st.markdown(f"""<div class="emergencia-box" style="background:#fff5f5;">
                    <span class="label">🏥 Salud</span><br>
                    <b>{hosp.get('nombre', 'No disponible')}</b><br>
                    📍 {hosp.get('direccion', '')}<br>📞 {hosp.get('tel', '')}
                </div>""", unsafe_allow_html=True)

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            # Carrusel
            st.image([f"https://source.unsplash.com/1200x400/?{dest}", 
                      f"https://source.unsplash.com/1200x400/?{dest},architecture"], use_container_width=True)

            for i, p in enumerate(guia.get('puntos', [])):
                nombre = p.get('nombre', 'Lugar')
                st.markdown(f"""
                <div class="punto-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#ff4b4b;">{nombre}</h3>
                        <span style="font-size:1.2rem;">{p.get('ranking', '⭐⭐⭐⭐')}</span>
                    </div>
                    <p style="margin-top:15px; font-size:1.1rem; color:#444;">{p.get('resenia', '')}</p>
                    <div style="display:flex; gap:30px; margin-top:15px; border-top:1px solid #eee; padding-top:15px;">
                        <div><span class="label">⏰ Horario</span><br>{p.get('horario', 'N/A')}</div>
                        <div><span class="label">💰 Precio</span><br>{p.get('precio', 'Consultar')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # BOTONES CON KEY ÚNICA (Soluciona foto d0725a.jpg)
                b1, b2 = st.columns(2)
                with b1:
                    q = urllib.parse.quote(f"{nombre} {dest}")
                    st.link_button("🗺️ VER MAPA", f"https://www.google.com/maps/search/{q}", use_container_width=True, key=f"map_{i}")
                with b2:
                    link = p.get('link_compra', 'No requiere link')
                    if "http" in str(link):
                        st.link_button("🎟️ TICKETS", link, use_container_width=True, key=f"tix_{i}")
                    else:
                        st.button(f"🏷️ {link}", disabled=True, use_container_width=True, key=f"info_{i}")