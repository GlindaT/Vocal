import streamlit as st
import plotly.graph_objects as go
import numpy as np

def render_tuner_js():
    # Inicializar el estado de la nota en la sesión
    if 'history' not in st.session_state:
        st.session_state.history = []

    # UI Minimalista
    st.markdown("""
        <style>
        .stMetric { text-align: center; }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        nota_obj = st.selectbox("Objetivo:", ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4'], index=5)
        if st.button("Limpiar gráfico"):
            st.session_state.history = []
    
    # Aquí iría tu lógica de captura (usando el código que ya te funciona)
    # Supongamos que 'current_pitch' es el valor que detectas
    # ... tu lógica de detección ...
    
    # GRÁFICO DINÁMICO
    st.session_state.history.append(current_pitch if current_pitch > 0 else None)
    if len(st.session_state.history) > 30: 
        st.session_state.history.pop(0) # Mantenemos solo los últimos 30 segundos
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=st.session_state.history, 
        mode='lines+markers', 
        line=dict(color='#00FF00', width=4)
    ))
    
    # Línea horizontal de referencia (Nota objetivo)
    fig.add_hline(y=librosa.note_to_hz(nota_obj), line_dash="dash", line_color="orange")
    
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        yaxis=dict(range=[200, 600]), # Rango vocal para C4-A4
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)
