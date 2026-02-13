import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime
import urllib.parse

# 1. ESTILO PERSONALIZADO (CSS) - Aquí es donde le damos identidad
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        border-radius: 20px;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 25px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff1a1a;
        box-shadow: 0px 0px 15px #ff4b4b;
    }
    .puntos-card {
        background-color: #1a1c24;
        border-radius: 15px;
        padding: 20px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    h1 { color: #ff4b4b !important; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error de configuración de seguridad.")
    st.stop()

# 3. INTERFAZ DE COMANDO
st.title("🆘 SOS PASSPORT : COMMAND CENTER")
st.write("---")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/826/826070.png", width=100)
    st.header("Configuración de Misión")
    nacionalidad = st.text_input("🌎 Nacionalidad", value="Argentina")
    idioma = st.selectbox("🗣️ Idioma", ["Español", "English", "Português"])
    experiencia = st.multiselect("🎭 Perfil de Viaje", ["Educación", "Entretenimiento", "Relax", "Aventura"], default=["Aventura"])

ciudad_input = st.text_input("📍 DESTINO ESTRATÉGICO", placeholder="Ej: Río de Janeiro, Brasil")

if ciudad_input:
    search_key = f"{ciudad_input.lower()}-{nacionalidad.lower()}"
    
    if st.button("DESPLEGAR GUÍA DE CAMPO"):
        guia_final = None
        
        # BUSCAR EN DB
        query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
        if query.data:
            guia_final = query.data[0]['datos_jsonb']
        
        if not guia_final:
            with st.spinner("Sincronizando con satélites de información..."):
                prompt = f"""
                Genera una guía de élite para un {nacionalidad} en {ciudad_input}. Idioma: {idioma}.
                Incluye 10 puntos de interés con ranking y categoría.
                Formato JSON estricto.
                """
                # (Aquí iría el llamado a Groq que ya tenemos funcionando...)
                # Para ahorrarte tokens en la prueba, supongamos que ya lo trajo:
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia_final = json.loads(completion.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia_final}).execute()

        # 4. MOSTRAR RESULTADOS CON IDENTIDAD
        if guia_final:
            st.subheader(f"🛡️ PROTOCOLO {ciudad_input.upper()}")
            
            # CARRUSEL DE IMÁGENES (Simulado con st.image para evitar errores de librerías externas)
            # Buscamos imágenes reales de la ciudad
            fotos_ciudad = [
                f"https://source.unsplash.com/800x400/?{ciudad_input},landmark",
                f"https://source.unsplash.com/800x400/?{ciudad_input},city",
                f"https://source.unsplash.com/800x400/?{ciudad_input},street"
            ]
            st.image(fotos_ciudad, caption=[f"{ciudad_input} 01", f"{ciudad_input} 02", f"{ciudad_input} 03"], use_container_width=True)

            st.divider()

            # Puntos de interés en formato Tarjeta
            for p in guia_final.get('puntos_interes', []):
                if not experiencia or p.get('categoria') in experiencia:
                    st.markdown(f"""
                    <div class="puntos-card">
                        <h3 style="margin:0;">{p['nombre']} {p.get('ranking', '⭐')}</h3>
                        <p style="color:#ff4b4b; font-size: 0.8em;">CATEGORÍA: {p.get('categoria', 'General')}</p>
                        <p>{p['reseña']}</p>
                        <p style="font-style: italic; color: #888;">💡 Tip: {p.get('tip_viajero', 'Disfruta el lugar.')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    q = urllib.parse.quote(f"{p['nombre']} {ciudad_input}")
                    st.link_button(f"📍 GPS: {p['nombre']}", f"https://www.google.com/maps/search/{q}")