import streamlit as st
from streamlit_mic_recorder import mic_recorder
import io
import librosa
import numpy as np
import plotly.graph_objects as go
from pydub import AudioSegment

# 1. Configuración inicial
st.set_page_config(page_title="Karaoke AI", layout="wide")

# 2. Título y Navegación
st.title("🎤 Mi App de Karaoke Pro")
tabs = st.tabs(["🎯 Afinador", "✂️ Separador", "🎼 Preparación", "🎙️ Estudio", "⚙️ Config"])

# --- PESTAÑA 1: AFINADOR ---
with tabs[0]:
    st.header("🎯 Afinador de Precisión")
    
    # Diccionario de notas estándar
    frecuencias = {
        "C (Do)": 261.63, "D (Re)": 293.66, "E (Mi)": 329.63, 
        "F (Fa)": 349.23, "G (Sol)": 392.00, "A (La)": 440.00, "B (Si)": 493.88
    }
    
    col_sel, col_mic = st.columns([1, 1])
    with col_sel:
        nota_sel = st.selectbox("Nota Objetivo", list(frecuencias.keys()), key="nota_afin")
        hz_obj = frecuencias[nota_sel]
    
    with col_mic:
        st.write("Graba una nota para analizar:")
        audio = mic_recorder(start_prompt="🎤 Empezar a Grabar", stop_prompt="⏹️ Detener y Analizar", key='afinador_v3')

    pitch_detectado = 0.0
    
    # Procesamiento si hay audio grabado
    if audio:
        try:
            # Convertir bytes a audio procesable
            audio_bytes = io.BytesIO(audio['bytes'])
            audio_seg = AudioSegment.from_file(audio_bytes)
            
            # Convertir a array de numpy para librosa
            samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
            y = samples / (2**15) # Normalizar
            sr = audio_seg.frame_rate
            
            # Detectar la frecuencia principal
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
            if magnitudes.max() > 0:
                pitch_detectado = float(pitches.flatten()[magnitudes.argmax()])
        except Exception as e:
            st.error(f"Error al procesar el audio: {e}")

    # --- GRÁFICO DE AGUJA ---
    # Rango dinámico para que la aguja siempre sea visible
    r_min = min(hz_obj, pitch_detectado) - 40 if pitch_detectado > 0 else hz_obj - 40
    r_max = max(hz_obj, pitch_detectado) + 40 if pitch_detectado > 0 else hz_obj + 40

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = pitch_detectado,
        title = {'text': f"Afinando: {nota_sel}"},
        delta = {'reference': hz_obj},
        gauge = {
            'axis': {'range': [r_min, r_max]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [hz_obj - 2, hz_obj + 2], 'color': "#00cc96"} # Franja verde de afinado
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': hz_obj}
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)

    # Mensajes de guía
    if pitch_detectado > 0:
        diff = pitch_detectado - hz_obj
        if abs(diff) < 2:
            st.success("🎯 ¡AFINADO! Lo lograste.")
            st.balloons()
        elif diff < 0:
            st.info("🔼 Sube un poco el tono (más agudo)")
        else:
            st.warning("🔽 Baja un poco el tono (más grave)")

# --- PESTAÑA 2: SEPARADOR ---
with tabs[1]:
    st.header("✂️ Separador de Voz (AI)")
    archivo = st.file_uploader("Sube tu canción", type=['mp3', 'wav'])
    if archivo:
        st.info("Archivo cargado. Preparando motores de IA...")

# --- PESTAÑA 3: PREPARACIÓN ---
with tabs[2]:
    st.header("🎼 Modo Práctica")
    st.write("Visualización de letra y métricas de práctica.")

# --- PESTAÑA 4: ESTUDIO ---
with tabs[3]:
    st.header("🎙️ Grabación de Estudio")
    st.button("🔴 Iniciar Grabación Maestra")

# --- PESTAÑA 5: CONFIGURACIONES ---
with tabs[4]:
    st.header("⚙️ Ajustes")
    st.slider("Dificultad de afinación", 1, 10, 5)
