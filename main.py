import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE Y LIMPIO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fdff; }
    .header-box { 
        background: linear-gradient(90deg, #00acc1, #00838f); 
        padding: 30px; border-radius: 15px; 
        color: white; text-align: center; margin-bottom: 20px;
    }
    .punto-card {
        background: white; border-radius: 15px; padding: 25px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px; border-left: 8px solid #00acc1;
    }
    .tag { background: #e0f7fa; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #006064; font-weight: bold; margin-right: 5px; }
    .btn-action {
        display: inline-block; padding: 10px 15px; border-radius: 10px; 
        text-decoration: none; font-weight: bold; font-size: 0.85rem;
        margin-top: 15px; margin-right: 10px; text-align: center;
    }
    .btn-map { background: #00838f; color: white !important; }
    .btn-tkt { background: #ff9800; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en Secrets. Verificá las credenciales en Streamlit Cloud.")
    st.stop()

st.markdown('<div class="header-box"><h1>SOS Passport 🏖️</h1><p>Tu guía de confianza para explorar el mundo</p></div>', unsafe_allow_html=True)

# 3. INTERFAZ
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", value="París, Francia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Conectando con guías locales..."):
                prompt = f"""Genera una guía para un {nac} en {dest} en {lang}. 
                Incluye: consulado, hospital y puntos turísticos con nombre, reseña, horario, precio y url_oficial_tickets.
                Responde ÚNICAMENTE en formato JSON."""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # 4. SEGURIDAD
            st.subheader("🛡️ Seguridad y Salud")
            st.info(f"🏛️ **Asistencia Consular:** {guia.get('consulado', 'Consultar online')}")
            st.success(f"🏥 **Hospital Recomendado:** {guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest}")
            
            # 5. RENDERIZADO FLEXIBLE
            puntos_list = []
            for k, v in guia.items():
                if isinstance(v, list):
                    puntos_list = v
                    break
            
            for p in puntos_list:
                n = p.get('nombre', 'Lugar Turístico')
                r = p.get('resenia', p.get('reseña', 'Sin descripción'))
                h = p.get('horario', 'Consultar')
                pr = p.get('precio', 'Variable')
                tkt = p.get('url_oficial_tickets', p.get('url_ticket', ''))
                
                # Link de mapa
                q_map = urllib.parse.quote(f"{n} {dest}")
                map_url = f"https://www.google.com/maps/search/?api=1&query={q_map}"
                
                # Lógica de tickets: si no hay link real, armamos uno de búsqueda oficial
                if "http" not in str(tkt):
                    q_tkt = urllib.parse.quote(f"tickets oficiales {n} {dest}")
                    tkt_url = f"https://www.google.com/search?q={q_tkt}"
                else:
                    tkt_url = tkt
                
                # Tarjeta con botones HTML (Inmunes al error de Streamlit)
                st.markdown(f"""
                <div class="punto-card">
                    <h3 style="margin:0; color:#00838f;">{n}</h3>
                    <p style="margin:10px 0; color:#444; font-size:1rem;">{r}</p>
                    <span class="tag">⏰ {h}</span>
                    <span class="tag">💰 {pr}</span>
                    <br>
                    <a href="{map_url}" target="_blank" class="btn-action btn-map">🗺️ VER MAPA</a>
                    <a href="{tkt_url}" target="_blank" class="btn-action btn-tkt">🎟️ COMPRAR TICKETS</a>
                </div>
                """, unsafe_allow_html=True)