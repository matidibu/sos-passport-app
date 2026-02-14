import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO LIMPIO Y SEGURO
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
        background: white; border-radius: 15px; padding: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px; border-left: 8px solid #00acc1;
    }
    .tag { background: #e0f7fa; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; color: #006064; font-weight: bold; }
    .btn-map { background: #00838f; color: white !important; padding: 8px 15px; border-radius: 8px; text-decoration: none; display: inline-block; margin-top: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en Secrets. Verificá las credenciales.")
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
            with st.spinner("Conectando con expertos locales..."):
                prompt = f"""Genera una guía para un {nac} en {dest} en {lang}. 
                Responde ÚNICAMENTE un JSON con:
                "consulado": "info",
                "hospital": "info",
                "puntos": [{{ "nombre": "Lugar", "resenia": "Breve info", "horario": "Info", "precio": "Info" }}]"""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            # 4. SEGURIDAD (Si esto aparece, el JSON cargó bien)
            st.subheader("🛡️ Seguridad")
            st.info(f"🏛️ **Consulado:** {guia.get('consulado', 'Consultar online')}")
            st.success(f"🏥 **Hospital:** {guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest}")
            
            # 5. RENDERIZADO ULTRA-FLEXIBLE
            # Buscamos cualquier lista en el JSON por si la IA cambió el nombre 'puntos'
            puntos_list = []
            for k, v in guia.items():
                if isinstance(v, list):
                    puntos_list = v
                    break
            
            if not puntos_list:
                st.warning("No se encontraron los puntos de interés. Intentá de nuevo.")
            
            for p in puntos_list:
                # Extraemos datos con valores por defecto para que nada falle
                n = p.get('nombre', 'Lugar Turístico')
                r = p.get('resenia', p.get('reseña', 'Sin descripción'))
                h = p.get('horario', 'Consultar')
                pr = p.get('precio', 'Variable')
                
                # Link de mapa limpio
                q_map = urllib.parse.quote(f"{n} {dest}")
                map_url = f"https://www.google.com/maps/search/?api=1&query={q_map}"
                
                # Mostramos la tarjeta
                st.markdown(f"""
                <div class="punto-card">
                    <h3 style="margin:0; color:#00838f;">{n}</h3>
                    <p style="margin:10px 0; color:#444; font-size:1rem;">{r}</p>
                    <span class="tag">⏰ {h}</span>
                    <span class="tag">💰 {pr}</span>
                    <br>
                    <a href="{map_url}" target="_blank" class="btn-map">🗺️ VER EN GOOGLE MAPS</a>
                </div>
                """, unsafe_allow_html=True)