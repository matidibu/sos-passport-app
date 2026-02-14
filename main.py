import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO "VIDA Y ALEGRÍA" (TURQUESA, NARANJA Y BLANCO)
st.set_page_config(page_title="SOS Passport", page_icon="🏖️", layout="wide")

st.markdown("""
    <style>
    /* Fondo que evoca el mar y el cielo */
    .stApp { 
        background: linear-gradient(135deg, #e0f7fa 0%, #ffffff 100%); 
    }

    /* Header con degradado alegre */
    .header-container {
        background: linear-gradient(90deg, #00bcd4, #00acc1);
        padding: 40px;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0, 188, 212, 0.2);
    }

    /* Contenedor de búsqueda con diseño 'Cloud' */
    [data-testid="stVerticalBlock"] > div:has(div.stContainer) {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #b2ebf2;
    }

    /* Botón Principal INTENSO */
    .stButton > button {
        background: linear-gradient(90deg, #ff9800, #f57c00); /* Naranja vibrante */
        color: white;
        font-weight: 800;
        font-size: 1.2rem;
        padding: 15px 30px;
        border-radius: 50px;
        border: none;
        box-shadow: 0 8px 20px rgba(255, 152, 0, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 25px rgba(255, 152, 0, 0.5);
        color: white;
    }

    /* Cards de Imperdibles (Limpio y Sólido) */
    .punto-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
        border-bottom: 6px solid #00bcd4;
        transition: all 0.3s ease;
    }
    .punto-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 188, 212, 0.15);
    }

    /* Títulos de las cards */
    .punto-card h3 { 
        color: #00838f; 
        font-size: 1.5rem;
        margin-top: 0;
    }

    /* Tags de info */
    .info-tag {
        background: #f1f8e9;
        color: #388e3c;
        padding: 6px 15px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-right: 10px;
        display: inline-block;
        border: 1px solid #c5e1a5;
    }
    .tag-blue { background: #e1f5fe; color: #0288d1; border: 1px solid #b3e5fc; }

    /* Botones de acción HTML */
    .btn-html {
        display: inline-block;
        padding: 12px 20px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.9rem;
        margin-top: 20px;
        margin-right: 12px;
        text-align: center;
        transition: 0.3s;
    }
    .btn-map { background: #00bcd4; color: white !important; }
    .btn-tkt { background: #ff5722; color: white !important; }
    .btn-html:hover { opacity: 0.9; transform: translateY(-2px); }

    /* Inputs y Labels */
    label { color: #00796b !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error en configuración. Verificá tus Secrets.")
    st.stop()

# Header Principal
st.markdown("""
    <div class="header-container">
        <h1 style="margin:0; font-size: 3.5rem; letter-spacing: -1px;">SOS Passport 🏖️</h1>
        <p style="font-size: 1.3rem; opacity: 0.9; font-weight: 500;">Tu compañero de confianza para descubrir el mundo</p>
    </div>
    """, unsafe_allow_html=True)

# 3. INTERFAZ DE BÚSQUEDA
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Tu Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 Destino Soñado", placeholder="Ej: París, Francia")
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
            with st.spinner("¡Buscando las mejores experiencias para vos!..."):
                prompt = f"Genera guía JSON para viajero {nac} en {dest} en {lang}: consulado, hospital y 7 puntos imperdibles (nombre, resenia, horario, precio, url_ticket)."
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()

        if guia:
            st.write(" ")
            # SECCIÓN SEGURIDAD
            st.markdown('<h2 style="color: #00796b; text-align: center;">🛡️ Información de Confianza</h2>', unsafe_allow_html=True)
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.info(f"🏛️ **Consulado:**\n\n{guia.get('consulado', 'Consultar online')}")
            with col_s2:
                st.success(f"🏥 **Hospital Recomendado:**\n\n{guia.get('hospital', 'Consultar online')}")

            st.markdown('<br><h2 style="color: #00796b; text-align: center;">📍 Imperdibles en ' + dest.title() + '</h2>', unsafe_allow_html=True)
            
            puntos = []
            for k, v in guia.items():
                if isinstance(v, list): puntos = v; break
            
            for p in puntos:
                nombre = str(p.get('nombre', 'Lugar'))
                precio = str(p.get('precio', 'Variable'))
                tkt = str(p.get('url_ticket', ''))
                
                # Link de Mapa
                q_map = urllib.parse.quote(f"{nombre} {dest}")
                map_url = f"https://www.google.com/maps/search/?api=1&query={q_map}"
                
                # Lógica de Botón de Ticket (Solo si no es gratis)
                btn_ticket_html = ""
                if "gratis" not in precio.lower() and "free" not in precio.lower():
                    if "http" not in tkt:
                        tkt = f"https://www.google.com/search?q=tickets+oficial+{urllib.parse.quote(nombre)}+{urllib.parse.quote(dest)}"
                    btn_ticket_html = f'<a href="{tkt}" target="_blank" class="btn-html btn-tkt">🎟️ COMPRAR TICKETS</a>'
                else:
                    btn_ticket_html = '<span class="info-tag" style="background:#e8f5e9; color:#2e7d32; border-color:#a5d6a7;">✨ ENTRADA GRATUITA</span>'

                st.markdown(f"""
                <div class="punto-card">
                    <h3>{nombre}</h3>
                    <p style="color:#555; line-height:1.6;">{p.get('resenia', '')}</p>
                    <div>
                        <span class="info-tag tag-blue">⏰ {p.get('horario')}</span>
                        <span class="info-tag">💰 {precio}</span>
                    </div>
                    <a href="{map_url}" target="_blank" class="btn-html btn-map">🗺️ VER EN MAPA</a>
                    {btn_ticket_html}
                </div>
                """, unsafe_allow_html=True)