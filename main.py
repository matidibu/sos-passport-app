import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="SOS Passport AI", page_icon="🆘", layout="centered")

# --- CONFIGURACIÓN DE IA ---
API_KEY = "AIzaSyBp_8YN50oicqeuBltOT-WHB2Fh2yWSuhg" 

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Error de configuración inicial.")