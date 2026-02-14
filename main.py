import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO PROFESIONAL Y OSCURO (PARA INSPIRAR VIAJES)
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    /* Fondo oscuro general */
    .stApp { background: #1a1a2e; color: #e0e0e0; }

    /* Contenedor principal para la búsqueda */
    .stApp > header { background: #1a1a2e; }
    .stApp [data-testid="stHeader"] { background-color: transparent; }
    .stApp [data-testid="stToolbar"] { right: 2rem; }
    .stApp [data-testid="stSidebar"] { background-color: #2a2a4a; color: #e0e0e0; }

    /* Títulos y texto */
    h1, h2, h3, h4, h5, h6 { color: #8d8dff; font-weight: bold; }
    p { color: #d0d0d0; }

    /* Contenedor de búsqueda */
    .stContainer {
        background: #2a2a4a;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        margin-bottom: 25px;
        border: 1px solid #3a3a5a;
    }

    /* Entrada de texto */
    .stTextInput > div > div > input {
        background-color: #3a3a5a;
        color: #e0e0e0;
        border: 1px solid #5a5a7a;
        border-radius: 8px;
        padding: 10px;
    }
    .stTextInput > label { color: #8d8dff; font-weight: bold; }

    /* Selectbox */
    .stSelectbox > div > button {
        background-color: #3a3a5a;
        color: #e0e0e0;
        border: 1px solid #5a5a7a;
        border-radius: 8px;
        padding: 10px;
    }
    .stSelectbox > label { color: #8d8dff; font-weight: bold; }

    /* Botón principal */
    .stButton > button {
        background-color: #6a1b9a; /* Púrpura */
        color: white;
        font-weight: bold;
        padding: 12px 25px;
        border-radius: 10px;
        border: none;
        box-shadow: 0 5px 15px rgba(106, 27, 154, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #7b29ad;
        box-shadow: 0 7px 20px rgba(106, 27, 154, 0.6);
        transform: translateY(-2px);
    }

    /* Card de Puntos de Interés */
    .punto-card {
        background: #2a2a4a;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
        border-left: 6px solid #8d8dff; /* Borde púrpura */
        transition: transform 0.2s ease-in-out;
    }
    .punto-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
    }
    .punto-card h3 { color: #e0e0e0; margin-bottom: 10px; }
    .punto-card p { color: #c0c0d0; font-size: 0.95rem; line-height: 1.5; }

    /* Tags de información */
    .info-tag {
        background: #3a3a5a;
        color: #8d8dff;
        padding: 5px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
        margin-top: 10px;
        display: inline-block;
        border: 1px solid #5a5a7a;
    }
    .info-tag.gratis {
        background-color: #4CAF50; /* Verde para gratis */
        color: white;
        border: none;
    }

    /* Botones de acción */
    .btn-action {
        display: inline-block;
        padding: 10px 18px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 0.85rem;
        margin-top: 15px;
        margin-right: 10px;
        transition: all 0.3s ease;
    }
    .btn-map { background: #00bcd4; color: white !important; } /* Azul cian */
    .btn-map:hover { background: #00d4eb; transform: translateY(-1px); }
    .btn-ticket { background: #ff5722; color: white !important; } /* Naranja rojizo */
    .btn-ticket:hover { background: #ff6f43; transform: translateY(-1px); }

    /* Alertas */
    .stAlert { background-color: #3a3a5a; color: #e0e0e0; border-radius: 10px; border: 1px solid #5a5a7a; }
    .stAlert [data-testid="stMarkdownContainer"] { color: #e0e0e0; }
    .stAlert [data-testid="stCodeBlock"] { background-color: #4a4a6a; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Error en la configuración de Secrets. Asegurate de tener SUPABASE_URL, SUPABASE_KEY y GROQ_API_KEY. Detalles: {e}")
    st.stop()

# Logo y Título de la App
st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <img src="https://i.imgur.com/kYm3c3W.png" alt="SOS Passport Logo" style="width:100px; height:100px; margin-bottom:10px;">
        <h1 style="color: #6a1b9a; font-size: 3.5rem; margin-top: 0;">SOS Passport</h1>
        <p style="color: #b0b0b0; font-size: 1.2rem;">Tu compañero de viaje inteligente para explorar el mundo sin estrés.</p>
    </div>
    """, unsafe_allow_html=True)


# 3. INTERFAZ DE BÚSQUEDA
with st.container(border=False): # Quitamos el borde del container para que se mezcle con el fondo
    st.markdown('<h3 style="text-align: center; color: #d0d0e0;">Planifica tu próxima aventura</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: nac = st.text_input("🌎 Nacionalidad", value="Argentina")
    with c2: dest = st.text_input("📍 ¿A dónde vas?", placeholder="Ej: París, Francia")
    with c3: lang = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("¡GENERAR MI EXPERIENCIA DE VIAJE!", use_container_width=True):
    if dest:
        search_key = f"{dest.lower().strip()}-{nac.lower().strip()}-{lang.lower()}"
        guia = None
        
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass
        
        if not guia:
            with st.spinner(f"Explorando {dest} para ti..."):
                prompt = f"""Genera una guía de viaje para un {nac} en {dest} en {lang}.
                Responde ÚNICAMENTE un JSON con esta estructura:
                {{
                    "consulado": "Dirección y teléfono",
                    "hospital": "Nombre y dirección",
                    "puntos": [
                        {{
                            "nombre": "Nombre del lugar",
                            "resenia": "Breve descripción",
                            "horario": "Horario detallado (ej: 9:00 - 18:00)",
                            "precio": "Precio detallado en moneda local (ej: 25 EUR) o 'Gratis'",
                            "url_ticket": "URL_DE_COMPRA_AQUÍ_O_VACÍO_SI_NO_EXISTE"
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
            st.divider() # Línea divisoria suave

            # SECCIÓN SEGURIDAD Y SALUD
            st.markdown('<h2 style="color: #00bcd4;">🛡️ Tu Seguridad es lo Primero</h2>', unsafe_allow_html=True)
            col_seg1, col_seg2 = st.columns(2)
            with col_seg1:
                st.info(f"**Consulado/Embajada:**\n\n{guia.get('consulado', 'Información no disponible. Sugerimos buscar online.')}")
            with col_seg2:
                st.success(f"**Hospital Recomendado:**\n\n{guia.get('hospital', 'Información no disponible. Sugerimos buscar online.')}")

            st.write("---") # Otro divisor
            
            # SECCIÓN IMPERDIBLES
            st.markdown(f'<h2 style="color: #00bcd4;">📍 Imperdibles en {dest.title()}</h2>', unsafe_allow_html=True)
            
            puntos_list = []
            for k, v in guia.items():
                if isinstance(v, list):
                    puntos_list = v
                    break
            
            if not puntos_list:
                st.warning("Parece que no encontramos puntos de interés. Por favor, intentá de nuevo con un destino diferente o refresca la página.")

            for i, p in enumerate(puntos_list):
                nombre = str(p.get('nombre', 'Lugar Desconocido'))
                resenia = str(p.get('resenia', 'Sin descripción.'))
                horario = str(p.get('horario', 'Consultar horario'))
                precio = str(p.get('precio', 'Variable'))
                url_ticket = str(p.get('url_ticket', ''))

                # Limpieza de URL para Google Maps
                q_map = urllib.parse.quote(f"{nombre} {dest}")
                map_link = f"https://www.google.com/maps/search/?api=1&query={q_map}"

                ticket_html = ""
                # Mostrar botón de tickets solo si el precio no es "Gratis" y hay una URL válida
                if "gratis" not in precio.lower() and "consultar" not in precio.lower() and precio.strip() != "":
                    if "http" in url_ticket:
                        ticket_html = f'<a href="{url_ticket}" target="_blank" class="btn-action btn-ticket">🎟️ COMPRAR TICKETS</a>'
                    else:
                        # Fallback a búsqueda de Google para tickets si no hay URL directa
                        q_tkt_search = urllib.parse.quote(f"tickets oficiales {nombre} {dest}")
                        ticket_html = f'<a href="https://www.google.com/search?q={q_tkt_search}" target="_blank" class="btn-action btn-ticket">🎟️ BUSCAR TICKETS</a>'
                elif "gratis" in precio.lower():
                    ticket_html = '<span class="info-tag gratis">✨ GRATIS</span>'


                st.markdown(f"""
                <div class="punto-card">
                    <h3 style="color: #8d8dff;">{nombre}</h3>
                    <p>{resenia}</p>
                    <div style="margin-top: 15px;">
                        <span class="info-tag">⏰ {horario}</span>
                        <span class="info-tag">💰 {precio}</span>
                    </div>
                    <div style="margin-top: 15px;">
                        <a href="{map_link}" target="_blank" class="btn-action btn-map">🗺️ VER EN MAPA</a>
                        {ticket_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)