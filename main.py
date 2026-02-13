import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# CONFIGURACIÓN VIBRANTE
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0f7fa 0%, #ffffff 100%); }
    .main-title { color: #00838f; font-weight: 800; font-size: 3rem !important; }
    .punto-card {
        background: white; border-radius: 20px; padding: 25px;
        box-shadow: 0px 10px 30px rgba(0, 131, 143, 0.1);
        margin-bottom: 25px; border-top: 8px solid #00acc1;
    }
    </style>
    """, unsafe_allow_html=True)

# CONEXIONES SEGURAS
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Falta configurar los Secrets de Streamlit.")
    st.stop()

st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía de confianza para explorar y descansar.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Roma, Italia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR MI DESTINO!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{lang.lower()}"
        guia = None
        
        # 1. BUSCAR EN DB
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        # 2. GENERAR SI NO EXISTE
        if not guia:
            with st.spinner("Creando tu experiencia ideal..."):
                prompt = f"Genera guía JSON alegre para {nac} en {dest} en {lang}. 8 puntos de interés. Incluye: nombre, resenia, ranking, horario, precio, link_ticket, consulado_info, hospital_info."
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        # 3. MOSTRAR (SOLUCIONA ERRORES DE FOTOS ANTERIORES)
        if guia:
            st.divider()
            # Seguridad limpia
            st.subheader("🛡️ Seguridad y Salud")
            col_e1, col_e2 = st.columns(2)
            col_e1.info(f"🏛️ **Consulado:** {guia.get('consulado_info', 'Consultar online')}")
            col_e2.success(f"🏥 **Hospital:** {guia.get('hospital_info', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            puntos = guia.get('puntos', [])
            for i, p in enumerate(puntos):
                nombre_lugar = str(p.get('nombre', 'Lugar Turístico')) # Evita TypeError
                st.markdown(f"""
                <div class="punto-card">
                    <h2 style="margin:0; color:#00838f;">{nombre_lugar}</h2>
                    <p style="font-size:1.1rem; margin-top:10px;">{p.get('resenia', p.get('reseña', ''))}</p>
                    <p><b>⏰ Horario:</b> {p.get('horario')} | <b>💰 Entrada:</b> {p.get('precio')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botones con Keys únicas (Evita error d0725a)
                b1, b2 = st.columns(2)
                with b1:
                    q_seguro = urllib.parse.quote(f"{nombre_lugar} {dest}")
                    st.link_button("🗺️ MAPA", f"https://www.google.com/maps/search/?api=1&query={q_seguro}", use_container_width=True, key=f"m_{i}")
                with b2:
                    link = p.get('link_ticket', 'No requiere')
                    if "http" in str(link):
                        st.link_button("🎟️ TICKETS", link, use_container_width=True, key=f"t_{i}")
                    else:
                        st.button(f"✨ {link}", disabled=True, use_container_width=True, key=f"d_{i}")