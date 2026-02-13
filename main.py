import streamlit as st
from groq import Groq
from supabase import create_client, Client
import json
import urllib.parse

# 1. ESTILO PROPIO (LIMPIO Y RECONOCIBLE)
st.set_page_config(page_title="SOS Passport", page_icon="🆘", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    .main-title { color: #ff4b4b; font-weight: 900; font-size: 3.5rem !important; margin-bottom: 0px; }
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        margin-bottom: 20px;
    }
    .tag {
        background: #ff4b4b;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIONES
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Error de conexión.")
    st.stop()

# 3. INTERFAZ: SOS PASSPORT
st.markdown('<h1 class="main-title">SOS PASSPORT</h1>', unsafe_allow_html=True)
st.write("### Tu Asistente Integral de Viaje")

# Buscador de Experiencias (Lo que me pediste)
with st.container():
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        ciudad = st.text_input("📍 ¿A dónde vas?", placeholder="Ej: Río de Janeiro")
    with col2:
        nacionalidad = st.text_input("🌎 Nacionalidad", value="Argentina")
    with col3:
        filtro_exp = st.multiselect(
            "🎭 Personalizá tu experiencia", 
            ["Educativa", "Entretenimiento", "Relax", "Aventura", "Gastronomía"],
            default=["Educativa", "Relax"]
        )

if st.button("GENERAR GUÍA INTEGRAL"):
    if ciudad:
        search_key = f"{ciudad.lower().strip()}-{nacionalidad.lower().strip()}"
        guia_final = None
        
        # BUSCAR EN SUPABASE
        res = supabase.table("guias").select("*").eq("clave_busqueda", search_key).execute()
        if res.data:
            guia_final = res.data[0]['datos_jsonb']
        
        # SI NO ESTÁ, PEDIR 10+ PUNTOS A LA IA
        if not guia_final:
            with st.spinner("Construyendo guía con más de 10 puntos de interés..."):
                prompt = f"""
                Crea una guía para un {nacionalidad} en {ciudad}. 
                Incluye obligatoriamente: 
                1. Consulado y Hospital.
                2. Una lista de al menos 12 puntos de interés.
                Cada punto debe tener: nombre, categoria (Educativa, Entretenimiento, Relax, Aventura, Gastronomía), ranking (1 a 5 estrellas), descripcion corta y un tip.
                Responde solo JSON.
                """
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                guia_final = json.loads(chat.choices[0].message.content)
                supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia_final}).execute()

        # 4. MOSTRAR RESULTADOS
        if guia_final:
            st.divider()
            # Info Crítica
            st.subheader("🚨 Información Esencial")
            c1, c2 = st.columns(2)
            with c1: st.info(f"🏛️ **Consulado:** {guia_final.get('consulado')}")
            with c2: st.warning(f"🏥 **Hospital:** {guia_final.get('hospital')}")

            # Buscador/Filtro Visual
            st.subheader(f"📍 Destacados en {ciudad}")
            
            puntos = guia_final.get('puntos', [])
            
            # Aquí es donde ocurre la magia del filtrado que querías
            for p in puntos:
                # Si el usuario eligió categorías, filtramos. Si no eligió nada, mostramos todo.
                if not filtro_exp or p.get('categoria') in filtro_exp:
                    with st.container():
                        st.markdown(f"""
                        <div class="card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <h3 style="margin:0;">{p['nombre']}</h3>
                                <span style="color:#ffb400; font-size:1.2rem;">{'⭐' * int(str(p.get('ranking','4'))[0])}</span>
                            </div>
                            <span class="tag">{p.get('categoria', 'General')}</span>
                            <p style="margin-top:10px;">{p.get('descripcion', 'Sin descripción')}</p>
                            <p style="font-size:0.9rem; color:#666;"><b>💡 Tip:</b> {p.get('tip', 'Disfrútalo.')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        q_map = urllib.parse.quote(f"{p['nombre']} {ciudad}")
                        st.link_button(f"Ver {p['nombre']} en Mapa", f"https://www.google.com/maps/search/?api=1&query={q_map}")