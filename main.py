import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime
import urllib.parse

# 1. IDENTIDAD VISUAL ÚNICA (CSS)
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    /* Fondo oscuro profundo */
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    /* Tarjetas con efecto de cristal y borde neón */
    .puntos-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 75, 75, 0.3);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 25px;
        transition: 0.4s ease;
    }
    .puntos-card:hover {
        border: 1px solid #ff4b4b;
        box-shadow: 0px 0px 20px rgba(255, 75, 75, 0.2);
        transform: translateY(-5px);
    }
    
    /* Títulos con personalidad */
    h1, h2, h3 { 
        font-family: 'Inter', sans-serif; 
        font-weight: 800;
        letter-spacing: -1px;
    }
    .main-title { color: #ff4b4b; font-size: 3rem !important; }
    
    /* Botones SOS */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background: linear-gradient(45deg, #ff4b4b, #8b0000);
        color: white;
        border: none;
        padding: 15px;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN (Blindada)
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error en el sistema de seguridad. Contactar soporte.")
    st.stop()

# 3. INTERFAZ DE USUARIO
st.markdown('<h1 class="main-title">🆘 SOS PASSPORT</h1>', unsafe_allow_html=True)
st.write("### Sistema Inteligente de Asistencia al Viajero")

col1, col2 = st.columns([2, 1])
with col1:
    ciudad_input = st.text_input("📍 OBJETIVO / DESTINO", placeholder="Ej: Río de Janeiro, Brasil")
with col2:
    nacionalidad = st.text_input("🌎 NACIONALIDAD", value="Argentina")

experiencia = st.multiselect("🔍 FILTRAR POR INTERÉS", ["Educación", "Entretenimiento", "Relax", "Gastronomía", "Aventura"])

if ciudad_input:
    # Clave de búsqueda (sin espacios raros)
    search_key = f"{ciudad_input.lower().strip()}-{nacionalidad.lower().strip()}"
    
    if st.button("DESPLEGAR PROTOCOLO DE VIAJE"):
        guia_final = None
        
        # BUSCAR EN DB
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data:
                guia_final = query.data[0]['datos_jsonb']
                st.toast("Guía cargada desde reserva local.")
        except: pass
        
        # SI NO ESTÁ, GENERAR CON IA
        if not guia_final:
            with st.spinner("Generando inteligencia estratégica..."):
                prompt = f"""
                Genera una guía de 10 puntos para un {nacionalidad} en {ciudad_input}.
                JSON con campos: 'consulado', 'hospital', 'puntos' (lista de 10 lugares).
                Cada lugar en 'puntos' debe tener: 'nombre', 'categoria', 'descripcion', 'estrellas' (1-5), 'tip'.
                """
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia_final = json.loads(completion.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia_final}).execute()

        # 4. DESPLIEGUE CON IDENTIDAD (Aquí arreglamos el KeyError)
        if guia_final:
            st.divider()
            
            # Galería de imágenes automática
            st.image([f"https://source.unsplash.com/1200x400/?{ciudad_input}", 
                      f"https://source.unsplash.com/1200x400/?{ciudad_input},culture"], 
                     caption=f"Vistas estratégicas de {ciudad_input}", use_container_width=True)

            for p in guia_final.get('puntos', []):
                # Usamos .get() para que si la IA no manda un campo, no se rompa la app
                nombre = p.get('nombre', 'Lugar Desconocido')
                desc = p.get('descripcion', p.get('reseña', p.get('resenia', 'Información no disponible')))
                cat = p.get('categoria', 'General')
                ranking = p.get('estrellas', p.get('ranking', '⭐⭐⭐⭐'))
                tip = p.get('tip', 'Disfruta tu visita.')

                if not experiencia or cat in experiencia:
                    st.markdown(f"""
                    <div class="puntos-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0; color:#ff4b4b;">{nombre}</h3>
                            <span style="font-size:1.2em;">{ranking}</span>
                        </div>
                        <p style="color:#888; font-weight:bold; font-size:0.8em; text-transform:uppercase;">{cat}</p>
                        <p style="font-size:1.05rem;">{desc}</p>
                        <p style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; border-left: 3px solid #ff4b4b;">
                        <b>💡 CONSEJO SOS:</b> {tip}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón de mapa limpio
                    q_map = urllib.parse.quote(f"{nombre} {ciudad_input}")
                    st.link_button(f"🧭 ABRIR RUTA HACIA {nombre.upper()}", f"https://www.google.com/maps/search/{q_map}")