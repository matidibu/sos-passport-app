import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json

# 1. ESTILO VIBRANTE Y LIMPIO
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
    .info-tag { background: #e0f7fa; padding: 8px 12px; border-radius: 10px; font-size: 0.9rem; color: #006064; font-weight: bold; display: inline-block; margin-top: 10px; }
    .map-link { color: #00838f; font-weight: bold; text-decoration: none; border: 1px solid #00838f; padding: 5px 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en la configuración de Secrets.")
    st.stop()

st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía inteligente para explorar destinos con seguridad.")

# 3. INTERFAZ
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino", placeholder="Ej: Londres, Reino Unido")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡EXPLORAR DESTINO!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        # Intentar recuperar de base de datos
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        # Si no existe, generar con IA
        if not guia:
            with st.spinner("Generando tu guía personalizada..."):
                prompt = f"""Genera una guía de viaje para un {nac} en {dest} en {lang}.
                IMPORTANTE: Sé muy específico con los precios (ej: '25 GBP') y horarios.
                Responde EXCLUSIVAMENTE un JSON con esta estructura:
                {{
                    "consulado": "Dirección y teléfono",
                    "hospital": "Nombre y dirección",
                    "puntos": [
                        {{
                            "nombre": "Nombre del lugar",
                            "resenia": "Descripción de 2 frases",
                            "horario": "Horario detallado",
                            "precio": "Precio detallado en moneda local"
                        }}
                    ]
                }}"""
                
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.divider()
            # SECCIÓN SEGURIDAD
            st.subheader("🛡️ Seguridad y Salud")
            cs1, cs2 = st.columns(2)
            cs1.info(f"🏛️ **Consulado:** {guia.get('consulado', 'Consultar online')}")
            cs2.success(f"🏥 **Hospital:** {guia.get('hospital', 'Consultar online')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {dest.title()}")
            
            puntos = guia.get('puntos', [])
            for i, p in enumerate(puntos):
                nombre = str(p.get('nombre', 'Lugar Turístico'))
                
                # Renderizamos la tarjeta con HTML para evitar errores de widgets de Streamlit
                st.markdown(f"""
                <div class="punto-card">
                    <h2 style="margin:0; color:#00838f;">{nombre}</h2>
                    <p style="margin:15px 0; font-size:1.1rem; color:#444;">{p.get('resenia', '')}</p>
                    <div style="margin-bottom: 20px;">
                        <span class="info-tag">⏰ {p.get('horario', 'No especificado')}</span>
                        <span class="info-tag">💰 {p.get('precio', 'Consultar')}</span>
                    </div>
                    <a href="https://www.google.com/maps/search/{nombre.replace(' ', '+')}+{dest.replace(' ', '+')}" 
                       target="_blank" class="map-link">📍 VER EN GOOGLE MAPS</a>
                </div>
                """, unsafe_allow_html=True)