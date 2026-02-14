import streamlit as st
from groq import Groq
from supabase import create_client
import json
import urllib.parse
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

# 2. CONEXIÓN (Blindada)
@st.cache_resource
def conectar():
    try:
        s = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        g = Groq(api_key=st.secrets["GROQ_API_KEY"])
        return s, g
    except Exception as e:
        st.error(f"Error de llaves: {e}")
        return None, None

supabase, client = conectar()

st.title("SOS PASSPORT ✈️")

# 3. ENTRADAS
c1, c2, c3 = st.columns(3)
with c1: nac = st.text_input("Nacionalidad", "Argentina")
with c2: dest = st.text_input("Destino", placeholder="Ej: Madrid")
with c3: lng = st.selectbox("Idioma", ["Español", "English", "Português"])

if st.button("GENERAR GUÍA", use_container_width=True):
    if not dest:
        st.warning("Escribe un destino.")
    else:
        search_key = f"{dest.lower()}-{nac.lower()}-{lng.lower()}"
        guia = None

        # A. BUSCAR EN DB
        if supabase:
            try:
                res = supabase.table("guias").select("datos_jsonb").eq("clave_busqueda", search_key).execute()
                if res.data: guia = res.data[0]['datos_jsonb']
            except: pass

        # B. PEDIR A IA SI NO HAY CACHÉ
        if not guia and client:
            with st.spinner("La IA está preparando los datos..."):
                try:
                    prompt = f"Genera un JSON para {nac} en {dest} ({lng}). Estructura EXACTA: {{\"resenia\":\"\", \"puntos\":[{{\"n\":\"nombre\",\"d\":\"desc\",\"h\":\"hora\",\"p\":\"precio\"}}], \"hospital\":\"\", \"cambio\":\"\", \"alojamiento\":\"\"}}"
                    resp = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    guia = json.loads(resp.choices[0].message.content)
                    if supabase:
                        supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                except Exception as e:
                    st.error(f"Error IA: {e}")

        # C. MOSTRAR RESULTADOS (A PRUEBA DE TODO)
        if guia:
            # Foto principal (ahora con palabras clave más fuertes)
            st.image(f"https://loremflickr.com/1200/450/{urllib.parse.quote(dest)},city,tourism/all", use_container_width=True)
            
            # 1. Reseña
            st.header(f"Explorando {dest.title()}")
            st.write(guia.get('resenia', 'Información general no disponible.'))

            # 2. Itinerario (Bucle protegido)
            st.subheader("📍 Lugares Recomendados")
            
            # Intentamos encontrar la lista de puntos, se llame como se llame
            lista_puntos = guia.get('puntos') or guia.get('itinerario') or guia.get('lugares') or []
            
            if lista_puntos:
                for i, p in enumerate(lista_puntos[:6]): # Máximo 6 puntos
                    with st.container(border=True):
                        col_img, col_txt = st.columns([1, 2])
                        nombre_lugar = p.get('n') or p.get('nombre') or "Lugar interesante"
                        
                        with col_img:
                            # Foto mini del lugar
                            st.image(f"https://loremflickr.com/400/300/{urllib.parse.quote(nombre_lugar)},{urllib.parse.quote(dest)}/all?lock={i}")
                        
                        with col_txt:
                            st.subheader(nombre_lugar)
                            st.write(p.get('d') or p.get('descripcion', ''))
                            st.caption(f"⏰ {p.get('h', 'Consultar')} | 💰 {p.get('p', 'Variable')}")
                            
                            # Botones de acción
                            q_map = urllib.parse.quote(f"{nombre_lugar} {dest}")
                            st.link_button("🗺️ Mapa", f"https://www.google.com/maps/search/{q_map}")

            # 3. Logística
            st.divider()
            st.subheader("📊 Información de Logística")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.info(f"🏥 **Salud**\n\n{guia.get('hospital', 'Consultar centros locales')}")
            with col_b:
                st.warning(f"💰 **Dinero**\n\n{guia.get('cambio', 'Usar casas oficiales')}")
            with col_c:
                st.success(f"🏨 **Alojamiento**\n\n{guia.get('alojamiento', 'Info de zonas')}")

        else:
            st.error("No se recibió respuesta de la IA. Intenta de nuevo.")