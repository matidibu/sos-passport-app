# C. PUNTOS (Con fotos individuales)
            st.subheader("📍 Itinerario Sugerido")
            puntos = guia.get('puntos', [])
            if isinstance(puntos, list):
                for p in puntos:
                    n_p = seguro(p.get('n'))
                    # Link de imagen específico para el punto de interés
                    img_punto = f"https://loremflickr.com/800/450/{urllib.parse.quote(n_p)},{urllib.parse.quote(destino)}/all"
                    
                    link_mapa = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{n_p} {destino}')}"
                    link_tkt = f"https://www.google.com/search?q=official+tickets+{urllib.parse.quote(f'{n_p} {destino}')}"
                    
                    # Estructura de la tarjeta con imagen
                    st.markdown(f"""
                    <div class="punto-card">
                        <img src="{img_punto}" style="width:100%; border-radius:15px; margin-bottom:15px; height:250px; object-fit:cover;" alt="{n_p}">
                        <h3>{n_p}</h3>
                        <p>{p.get('d', '')}</p>
                        <small><b>⏰ Horario:</b> {p.get('h', 'Consultar')} | <b>💰 Precio:</b> {p.get('p', 'Consultar')}</small><br>
                        <div style="margin-top:15px;">
                            <a href="{link_mapa}" target="_blank" class="btn-action btn-primary">🗺️ MAPA</a>
                            <a href="{link_tkt}" target="_blank" class="btn-action btn-secondary">🎟️ TICKETS</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)