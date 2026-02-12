# ... (Todo el código anterior de conexión y búsqueda igual)

if ciudad_buscada:
    if st.button(f"Generar Guía para {ciudad_buscada}"):
        with st.spinner(f"Construyendo kit para {ciudad_buscada}..."):
            try:
                # Ajustamos el Prompt para que la IA nos de texto limpio
                prompt = f"""
                Genera una ficha de emergencia para {ciudad_buscada} en JSON.
                IMPORTANTE: No uses etiquetas como 'nombre' o 'dirección' dentro de los valores.
                Solo pon la información directa.
                Ejemplo de valor: 'Calle Falsa 123, Tel: +54 11...'
                
                Estructura:
                "consulado": "info del consulado argentino",
                "hospital": "info del hospital principal",
                "seguridad": "un consejo corto",
                "puntos_interes": "los 3 lugares más importantes con una breve descripción"
                """
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                res = json.loads(chat_completion.choices[0].message.content)
                
                st.success(f"📍 {ciudad_buscada.upper()}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 🏛️ Consulado")
                    # Mostramos solo el texto, sin etiquetas
                    st.write(res['consulado'])
                    st.link_button("🗺️ Ver Mapa", f"https://www.google.com/maps/search/Consulado+Argentino+{ciudad_buscada}")

                with col2:
                    st.markdown("### 🏥 Hospital")
                    st.write(res['hospital'])
                    st.link_button("🚑 Emergencias", f"https://www.google.com/maps/search/Hospitales+{ciudad_buscada}")

                with col3:
                    st.markdown("### 🌟 Imperdibles")
                    st.write(res['puntos_interes'])
                    st.markdown(f"**🛡️ Seguridad:** {res['seguridad']}")
            
            except Exception as e:
                st.error("Hubo un problema al procesar los datos.")