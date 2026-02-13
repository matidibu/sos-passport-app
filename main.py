import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO VIBRANTE Y DE DESCANSO
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    /* Fondo turquesa muy suave y limpio */
    .stApp { background: linear-gradient(135deg, #f0faff 0%, #ffffff 100%); color: #2c3e50; }
    
    .main-title { 
        color: #00838f; 
        font-weight: 800; 
        font-size: 3.5rem !important; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }

    /* Tarjetas blancas con borde turquesa */
    .punto-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 10px 30px rgba(0, 131, 143, 0.1);
        margin-bottom: 25px;
        border-top: 8px solid #00acc1;
    }

    .label-mini { 
        font-weight: bold; 
        color: #00acc1; 
        font-size: 0.75rem; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }

    /* Botones redondeados y alegres */
    .stButton>button {
        background: #00acc1;
        color: white;
        border-radius: 30px;
        border: none;
        padding: 12px 25px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Conectando con el centro de viajeros...")
    st.stop()

# 3. HOME: CONFIGURACIÓN (NACIONALIDAD, DESTINO, IDIOMA)
st.markdown('<h1 class="main-title">SOS Passport 🏖️</h1>', unsafe_allow_html=True)
st.write("### Tu guía de confianza para explorar y descansar.")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 ¿A dónde vamos?", placeholder="Ej: Positano, Italia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano", "Français"])

if st.button("¡EMPEZAR LA AVENTURA!", use_container_width=True):
    if dest and nac:
        # Clave única para evitar errores de caché
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner("Diseñando una experiencia inolvidable..."):
                prompt = f"""
                Genera una guía de viaje alegre para un {nac} en {dest} en {lang}.
                Incluye 8 puntos de interés (entre 5 y 10).
                Responde JSON:
                {{
                    "emergencia": {{
                        "consulado": {{"nombre": "Nombre", "dir": "Dirección", "tel": "Teléfono"}},
                        "hospital": {{"nombre": "Nombre", "dir": "Dirección", "tel": "Teléfono"}}
                    }},
                    "puntos": [
                        {{
                            "nombre": "Nombre",
                            "resenia": "Reseña inspiradora",
                            "ranking": "⭐⭐⭐⭐⭐",
                            "horario": "Horarios",
                            "precio": "Precio entradas",
                            "link": "URL o 'No requiere'"
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

        # 4. DESPLIEGUE (Corrigiendo errores de las fotos)
        if guia:
            st.divider()
            
            # Bloque Emergencia Limpio (como en tu foto dbd302)
            st.subheader("🛡️ Viajá con Seguridad")
            em = guia.get('emergencia', {})
            ce1, ce2 = st.columns(2)
            
            for key, col, color in [('consulado', ce1, '#e1f5fe'), ('hospital', ce2, '#f1f8e9')]:
                data = em.get(key, {})
                col.markdown(f"""
                <div style="background:{color}; padding:15px; border-radius:15px; border:1px solid #ddd;">
                    <span class="label-mini">{key.upper()}</span><br>
                    <b>{data.get('nombre', 'Consultar')}</b><br>
                    📍 {data.get('dir', 'No disponible')}<br>
                    📞 {data.get('tel', 'No disponible')}
                </div>
                """, unsafe_allow_html=True)

            st.write("---")
            st.subheader(f"📍 Lo mejor de {dest.title()}")
            
            # Puntos de interés (Arreglo del TypeError)
            puntos_lista = guia.get('puntos', [])
            
            for i, p in enumerate(puntos_lista):
                with st.container():
                    st.markdown(f"""
                    <div class="punto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h2 style="margin:0; color:#00838f;">{p.get('nombre')}</h2>
                            <span>{p.get('ranking')}</span>
                        </div>
                        <p style="margin-top:15px; font-size:1.1rem; line-height:1.6;">{p.get('resenia', p.get('reseña', ''))}</p>
                        <div style="display:flex; gap:25px; margin-top:15px; padding-top:15px; border-top:1px solid #eee;">
                            <span><b>⏰ Horario:</b> {p.get('horario')}</span>
                            <span style="color:#2e7d32;"><b>💰 Entrada:</b> {p.get('precio')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        q = urllib.parse.quote(f"{p.get('nombre')} {dest}")
                        st.link_button("🗺️ MAPA", f"https://www.google.com/maps/search/{q}", use_container_width=True, key=f"m_{i}")
                    with b2:
                        link = p.get('link', p.get('link_ticket', 'No requiere'))
                        if "http" in str(link):
                            st.link_button("🎟️ TICKETS", link, use_container_width=True, key=f"t_{i}")
                        else:
                            st.button(f"✨ {link}", disabled=True, use_container_width=True, key=f"i_{i}")