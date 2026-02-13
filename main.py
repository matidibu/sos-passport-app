import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. IDENTIDAD VISUAL: CLARIDAD Y FOCO
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    .main-title { color: #ff4b4b; font-weight: 900; font-size: 3.5rem !important; letter-spacing: -1.5px; }
    .punto-card {
        background: #fdfdfd;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #eee;
        border-left: 6px solid #ff4b4b;
        margin-bottom: 20px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.03);
    }
    .data-label { font-weight: bold; color: #ff4b4b; text-transform: uppercase; font-size: 0.75rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión. Verifique credenciales.")
    st.stop()

# 3. INTERFAZ DE MANDO
st.markdown('<h1 class="main-title">SOS PASSPORT</h1>', unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        nacionalidad = st.text_input("🌎 Nacionalidad", value="Argentina")
    with col2:
        ciudad_input = st.text_input("📍 Ciudad de Destino", placeholder="Ej: Roma, Italia")
    with col3:
        idioma = st.selectbox("🗣️ Idioma", ["Español", "English", "Português", "Italiano"])

if st.button("DESPLEGAR GUÍA INTEGRAL", use_container_width=True):
    if ciudad_input and nacionalidad:
        # Clave única incluyendo idioma para evitar mezclas en la DB
        search_key = f"{ciudad_input.lower().strip()}-{nacionalidad.lower().strip()}-{idioma.lower()}"
        guia_final = None
        
        # BUSCAR EN SUPABASE
        try:
            res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if res.data:
                guia_final = res.data[0]['datos_jsonb']
        except: pass
        
        # SI NO EXISTE, GENERAR CON IA DETALLADA
        if not guia_final:
            with st.spinner(f"Analizando {ciudad_input}..."):
                prompt = f"""
                Genera una guía de seguridad y turismo para un {nacionalidad} en {ciudad_input} en {idioma}.
                Incluye: consulado, hospital y 12 puntos de interés.
                Para cada punto: nombre, resenia (extensa), ranking (estrellas), horario, precio_entrada, link_compra.
                Responde solo JSON.
                """
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia_final = json.loads(completion.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia_final}).execute()

        # 4. DESPLIEGUE DE LA EXPERIENCIA
        if guia_final:
            st.divider()
            # Bloque Emergencia
            st.subheader("🚨 Protocolo de Emergencia")
            c1, c2 = st.columns(2)
            with c1: st.info(f"🏛️ **Consulado:** {guia_final.get('consulado') or guia_final.get('emergencia',{}).get('consulado')}")
            with c2: st.error(f"🏥 **Salud:** {guia_final.get('hospital') or guia_final.get('emergencia',{}).get('hospital')}")

            st.write("---")
            st.subheader(f"📍 Imperdibles en {ciudad_input.title()}")
            
            # Galería Visual
            st.image([f"https://source.unsplash.com/1200x400/?{ciudad_input}", 
                      f"https://source.unsplash.com/1200x400/?{ciudad_input},art"], use_container_width=True)

            # Iteración de los 12 puntos
            puntos = guia_final.get('puntos', []) or guia_final.get('puntos_interes', [])
            for i, p in enumerate(puntos):
                nombre = p.get('nombre', 'Punto de Interés')
                with st.container():
                    st.markdown(f"""
                    <div class="punto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0; color:#ff4b4b;">{nombre}</h3>
                            <span style="font-size:1.2rem;">{p.get('ranking', '⭐⭐⭐⭐')}</span>
                        </div>
                        <p style="margin-top:10px; font-size:1.05rem; line-height:1.6; color:#333;">{p.get('resenia', p.get('reseña', ''))}</p>
                        <div style="display: flex; gap: 20px; margin-top:15px; background:#f1f1f1; padding:10px; border-radius:8px;">
                            <div><span class="data-label">⏰ Horario</span><br>{p.get('horario', 'Consultar')}</div>
                            <div><span class="data-label">💰 Entradas</span><br>{p.get('precio', p.get('precio_entrada', 'Gratis'))}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botones con Key única para evitar el DuplicateElementId
                    b1, b2 = st.columns(2)
                    with b1:
                        q_map = urllib.parse.quote(f"{nombre} {ciudad_input}")
                        st.link_button(f"🗺️ MAPA", f"https://www.google.com/maps/search/{q_map}", use_container_width=True)
                    with b2:
                        link = p.get('link_entradas', p.get('link_compra', 'No requiere'))
                        if "http" in str(link):
                            st.link_button(f"🎟️ TICKETS", link, use_container_width=True)
                        else:
                            # Agregamos la variable 'i' a la key para que sea única
                            st.button(f"🏷️ {link}", disabled=True, use_container_width=True, key=f"btn_{i}")