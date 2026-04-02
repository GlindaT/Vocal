import streamlit as st
from streamlit_mic_recorder import mic_recorder
import librosa
import numpy as np
import io

# Configuración de la página
st.set_page_config(page_title="Karaoke AI", layout="wide")

# Título y Navegación
st.title("🎤 Mi App de Karaoke Pro")
tabs = st.tabs(["🎯 Afinador", "✂️ Separador", "🎼 Preparación", "🎙️ Estudio", "⚙️ Config"])

# --- PESTAÑA 1: AFINADOR ---
with tabs[0]:
    st.header("Afinador")
    nota_ref = st.selectbox("Nota objetivo", ["C", "D", "E", "F", "G", "A", "B"])
    
    audio = mic_recorder(start_prompt="Grabar nota", stop_prompt="Detener", key='afinador')
    
    if audio:
        # 1. Convertir bytes a formato que Librosa entienda
        audio_bytes = io.BytesIO(audio['bytes'])
        y, sr = librosa.load(audio_bytes, sr=None) # sr=None mantiene el sample rate original
        
        # 2. Algoritmo de detección de frecuencia (Pitch)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Extraer la frecuencia más prominente
        index = magnitudes.argmax()
        pitch_detectado = pitches.flatten()[index]
        
        if pitch_detectado > 0:
            st.metric("Frecuencia Detectada", f"{pitch_detectado:.2f} Hz")
            # Aquí podrías comparar pitch_detectado con la nota_ref
            st.success(f"¡Nota capturada! Frecuencia: {int(pitch_detectado)} Hz")
        else:
            st.warning("No se detectó un sonido claro. Prueba grabar más cerca.")
            
        st.audio(audio['bytes'])
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
