import streamlit as st
import streamlit.components.v1 as components

# Función para obtener coordenadas (vía JS)
def get_location():
    # Este script le pide al navegador la latitud y longitud
    js_code = """
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            window.parent.postMessage({type: 'location', lat: lat, lon: lon}, '*');
        }
    );
    </script>
    """
    components.html(js_code, height=0)

st.title("🆘 SOS Passport - Localizador de Emergencia")

if st.button("📍 Encontrarme y buscar ayuda cercana"):
    get_location()
    st.info("Buscando hospital y consulado más cercanos a tu posición actual...")
    
    # Aquí integraríamos la búsqueda de Google Maps con la info que ya recuperamos
    st.markdown("""
    ### 🏥 Hospital más cercano
    **Hospital Cullen** - [Abrir en Google Maps](https://www.google.com/maps/dir/?api=1&destination=-31.6485,-60.7189)
    
    ### 🏛️ Consulado más cercano
    **Viceconsulado** - [Cómo llegar](https://www.google.com/maps/dir/?api=1&destination=-31.6382,-60.7031)
    """)
    
    # Mostrar el mapa embebido
    st.components.v1.iframe("URL_DE_GOOGLE_MAPS_CON_TUS_PUNTOS", height=400)