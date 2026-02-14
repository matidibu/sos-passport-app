import streamlit as st
from groq import Groq
from supabase import create_client
import json
import urllib.parse
import time

# 1. CONFIGURACIÓN BÁSICA (Sin adornos que rompan el renderizado)
st.set_page_config(page_title="SOS Passport", page_icon="✈️", layout="wide")

# 2. INICIALIZACIÓN DE CLIENTES
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Error crítico de llaves/conexión: {e}")
    st.stop()

st.title("SOS PASSPORT ✈️")
st.caption("Logística de viaje oficial y tickets")

# 3. ENTRADAS
col_in = st.columns([1, 1, 1])
with col_in[0]: nac = st.text_input("Nacionalidad", "Argentina")
with col_in[1]: dest = st.text_input("Ciudad de Destino", placeholder="Ej: Roma")
with col_in[2]: lng = st.selectbox("Idioma", ["Español", "English", "Português"])

if st.button("GENERAR GUÍA", use_container_width=True):
    if not dest:
        st.warning("Ingresa un destino")
    else:
        search_key = f"{dest.lower()}-{nac.lower()}-{lng.lower()}"
        guia = None

        # Intento recuperar de DB
        try:
            res = supabase.table("guias").select("datos_jsonb").eq("clave_busqueda", search_key).execute()
            if res.data: guia = res.data[0]['datos_jsonb']
        except: pass

        # Si no hay, pido a IA
        if not guia:
            with st.spinner("La IA está redactando tu guía..."):
                try:
                    prompt = f"Genera un JSON para un viajero {nac} en {dest} en idioma {lng}. Debe tener: 'resenia' (str), 'puntos' (lista de objetos con n, d, h, p), 'hospital' (str), 'cambio' (str), 'alojamiento' (str)."
                    resp = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    guia = json.loads(resp.choices[0].message.content)
                    # Guardar para la próxima
                    try: supabase.table("guias").upsert({"clave_busqueda": search_key, "datos_jsonb": guia}).execute()
                    except: pass
                except Exception as e:
                    st.error(f"La IA falló: {e}")

        # 4. RENDERIZADO (Usando componentes nativos de Streamlit, mucho más estables)
        if guia:
            # Foto Principal
            st.image(f"https://loremflickr.com/1200/450/{urllib.parse.quote(dest)},city/all", use_container_width=True)
            
            # Reseña
            st.subheader(f"Sobre {dest.title()}")
            st.write(guia.get('resenia', 'No disponible'))

            st.divider()

            # Itinerario en Columnas
            st.subheader("📍 Lugares imperdibles")
            puntos = guia.get('puntos', [])
            if puntos:
                # Mostramos de a 2 lugares por fila
                cols_p = st.columns(2)
                for i, p in enumerate(puntos):
                    with cols_p[i % 2]:
                        with st.container(border=True):
                            nombre = p.get('n', 'Lugar')
                            # Foto del lugar específico
                            st.image(f"https://loremflickr.com/600/400/{urllib.parse.quote(nombre)},{urllib.parse.quote(dest)}/all?lock={i}")
                            st.subheader(nombre)
                            st.write(p.get('d', ''))
                            st.caption(f"⏰ {p.get('h')} | 💰 {p.get('p')}")
                            
                            # Botones nativos
                            q = urllib.parse.quote(f"{nombre} {dest}")
                            st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/{q}")
                            st.link_button("🎟️ Buscar Tickets", f"https://www.google.com/search?q=official+tickets+{q}")

            st.divider()

            # Logística
            st.subheader("📊 Logística y Seguridad")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(f"🏥 **Salud**\n\n{guia.get('hospital')}")
            with c2:
                st.warning(f"💰 **Dinero**\n\n{guia.get('cambio')}")
            with c3:
                st.success(f"🏨 **Alojamiento**\n\n{guia.get('alojamiento')}")

        else:
            st.error("No se pudo obtener información. Por favor, intenta de nuevo.")