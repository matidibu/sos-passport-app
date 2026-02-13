import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
from datetime import datetime
import urllib.parse

# 1. ESTILO "CLARIDAD SOS" (CSS)
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    /* Fondo Blanco y texto oscuro para máxima legibilidad */
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    
    /* Título con fuerza en Rojo */
    .main-title { 
        color: #ff4b4b; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-weight: 900; 
        font-size: 3.5rem !important;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }
    
    /* Tarjetas Blancas con sombra suave (Efecto Papel) */
    .info-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #e9ecef;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.02);
    }
    
    /* Inputs y botones adaptados */
    .stTextInput>div>div>input {
        background-color: #ffffff;
        border: 1px solid #ced4da;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 18px;
        font-weight: bold;
        border-radius: 5px;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #e63946;
        box-shadow: 0px 5px 15px rgba(255, 75, 75, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión con el servidor.")
    st.stop()

# 3. INTERFAZ LIMPIA
st.markdown('<h1 class="main-title">SOS PASSPORT</h1>', unsafe_allow_html=True)
st.write("🌍 **ASISTENCIA GLOBAL AL VIAJERO** | PROTOCOLO DE SEGURIDAD")
st.write("---")

col_in1, col_in2 = st.columns(2)
with col_in1:
    ciudad_input = st.text_input("📍 CIUDAD DE DESTINO", placeholder="Ej: Río de Janeiro")
with col_in2:
    nacionalidad = st.text_input("🌎 TU NACIONALIDAD", value="Argentina")

if st.button("DESPLEGAR GUÍA DE ASISTENCIA"):
    if ciudad_input:
        search_key = f"{ciudad_input.lower().strip()}-{nacionalidad.lower().strip()}"
        guia_final = None
        
        # BUSCAR EN DB
        try:
            query = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
            if query.data:
                guia_final = query.data[0]['datos_jsonb']
        except: pass
        
        # GENERAR CON IA SI NO EXISTE
        if not guia_final:
            with st.spinner("Sincronizando datos de seguridad..."):
                prompt = f"""
                Genera una guía técnica y turística para un {nacionalidad} en {ciudad_input}.
                Idioma: Español.
                JSON con campos: 'consulado', 'hospital', 'puntos' (lista de 10 lugares con nombre, descripcion, ranking y tip).
                """
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia_final = json.loads(completion.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia_final}).execute()

        # 4. DESPLIEGUE DE RESULTADOS (DISEÑO LUMINOSO)
        if guia_final:
            st.divider()
            
            # Bloque de Emergencia
            st.subheader(f"🚨 Información Crítica: {ciudad_input.upper()}")
            ce1, ce2 = st.columns(2)
            with ce1:
                st.markdown(f"""
                <div style="background:#fff5f5; padding:15px; border-radius:8px; border:1px solid #ffcccc;">
                    <b style="color:#ff4b4b;">🏛️ CONSULADO DE {nacionalidad.upper()}</b><br>
                    {guia_final.get('consulado')}
                </div>
                """, unsafe_allow_html=True)
            with ce2:
                st.markdown(f"""
                <div style="background:#fff5f5; padding:15px; border-radius:8px; border:1px solid #ffcccc;">
                    <b style="color:#ff4b4b;">🏥 HOSPITAL DE REFERENCIA</b><br>
                    {guia_final.get('hospital')}
                </div>
                """, unsafe_allow_html=True)

            st.write("---")
            st.subheader("📍 Puntos Estratégicos Recomendados")
            
            # Imagen destacada
            st.image(f"https://source.unsplash.com/1200x400/?{ciudad_input},city", use_container_width=True)

            # Tarjetas de lugares
            for p in guia_final.get('puntos', []):
                nombre = p.get('nombre', 'Lugar')
                desc = p.get('descripcion', p.get('reseña', p.get('resenia', 'Información no disponible')))
                ranking = p.get('ranking', '⭐⭐⭐⭐')
                tip = p.get('tip', 'Recomendado.')

                st.markdown(f"""
                <div class="info-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#1a1a1a;">{nombre}</h3>
                        <span style="color:#ff4b4b; font-weight:bold;">{ranking}</span>
                    </div>
                    <p style="margin-top:10px; color:#444;">{desc}</p>
                    <p style="font-size:0.9rem; color:#666; border-top:1px solid #eee; padding-top:10px; margin-top:10px;">
                        <b>💡 TIP SOS:</b> {tip}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                q_map = urllib.parse.quote(f"{nombre} {ciudad_input}")
                st.link_button(f"📍 VER MAPA DE {nombre.upper()}", f"https://www.google.com/maps/search/{q_map}")