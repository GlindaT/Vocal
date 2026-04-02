import streamlit as st
from streamlit_mic_recorder import mic_recorder
import librosa
import numpy as np
import io
from pydub import AudioSegment
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Karaoke AI", layout="wide")

# Título y Navegación
st.title("🎤 Mi App de Karaoke Pro")
tabs = st.tabs(["🎯 Afinador", "✂️ Separador", "🎼 Preparación", "🎙️ Estudio", "⚙️ Config"])

# --- PESTAÑA 1: AFINADOR (REEMPLAZA TODO EL CONTENIDO DE ESTA PESTAÑA) ---
with tabs[0]:
    st.header("🎯 Afinador de Precisión")
    
    # 1. Diccionario de frecuencias
    frecuencias_notas = {
        "C (Do)": 261.63, "D (Re)": 293.66, "E (Mi)": 329.63, 
        "F (Fa)": 349.23, "G (Sol)": 392.00, "A (La)": 440.00, "B (Si)": 493.88
    }
    
    col_sel, col_mic = st.columns([1, 2])
    with col_sel:
        nota_ref = st.selectbox("Nota objetivo", list(frecuencias_notas.keys()))
        hz_objetivo = frecuencias_notas[nota_ref]
    
    with col_mic:
        audio = mic_recorder(start_prompt="🎤 Grabar nota", stop_prompt="🛑 Detener", key='afinador')

    if audio:
        try:
            # Procesamiento de audio
            audio_seg = AudioSegment.from_file(io.BytesIO(audio['bytes']))
            samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
            sr = audio_seg.frame_rate
            y = samples / (2**15) 

            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            index = magnitudes.argmax()
            pitch_detectado = pitches.flatten()[index]

            if pitch_detectado > 40:
                diferencia = pitch_detectado - hz_objetivo
                
                # --- 1. MÉTRICAS (Texto arriba) ---
                c1, c2 = st.columns(2)
                c1.metric("Frecuencia Real", f"{pitch_detectado:.2f} Hz")
                c2.metric("Objetivo", f"{hz_objetivo:.2f} Hz", f"{diferencia:.2f} Hz")

                # --- 2. GRÁFICO CIRCULAR (Debajo de métricas) ---
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = pitch_detectado,
                    title = {'text': f"Afinación: {nota_ref}", 'font': {'size': 24}},
                    gauge = {
                        'axis': {'range': [hz_objetivo - 30, hz_objetivo + 30], 'tickwidth': 1},
                        'bar': {'color': "#1f77b4"}, # Color de la aguja
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "#444",
                        'steps': [
                            {'range': [hz_objetivo - 30, hz_objetivo - 2], 'color': '#ff4b4b'}, # Rojo (Bajo)
                            {'range': [hz_objetivo - 2, hz_objetivo + 2], 'color': '#00cc96'}, # VERDE (Afinado)
                            {'range': [hz_objetivo + 2, hz_objetivo + 30], 'color': '#ff4b4b'}  # Rojo (Alto)
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': hz_objetivo
                        }
                    }
                ))

                # Ajuste estético del gráfico
                fig.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20))
                
                # Renderizar el medidor
                st.plotly_chart(fig, use_container_width=True)

                # --- 3. MENSAJE FINAL ---
                if abs(diferencia) < 2:
                    st.success("🎯 ¡ESTÁS AFINADO!")
                    st.balloons()
                elif diferencia < 0:
                    st.warning("🔽 Sube un poco el tono (más agudo)")
                else:
                    st.warning("🔼 Baja un poco el tono (más grave)")
                    except Exception as e:
            st.error(f"Error técnico: {e}") 

# --- PESTAÑA 2: SEPARADOR ---
with tabs[1]:
    st.header("Separador de Voz (AI)")
    archivo = st.file_uploader("Sube tu canción", type=['mp3', 'wav'])
    if archivo:
        st.info("Procesando separación... (Nota: Esto requiere mucha CPU)")

# --- PESTAÑA 3: PREPARACIÓN ---
with tabs[2]:
    st.header("Modo Práctica")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🎵 Letra de la canción")
        st.code("La la la... (Visualización de pentagrama aquí)")
    with col2:
        st.write("Informe de afinación")

# --- PESTAÑA 4: ESTUDIO ---
with tabs[3]:
    st.header("Grabación de Estudio")
    st.button("🔴 Iniciar Grabación Maestra")

# --- PESTAÑA 5: CONFIGURACIONES ---
with tabs[4]:
    st.header("Ajustes")
    st.slider("Dificultad", 1, 10, 5)
    st.color_picker("Color de letra", "#00FFAA")
