import streamlit as st
from streamlit_mic_recorder import mic_recorder
import librosa
import numpy as np
import io
from pydub import AudioSegment

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
        try:
            # 1. Convertir los bytes del micro a un array que Librosa entienda usando Pydub
            audio_seg = AudioSegment.from_file(io.BytesIO(audio['bytes']))
            
            # Convertir a mono y a los floats que espera librosa
            samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
            sr = audio_seg.frame_rate
            
            # Normalizar el audio (importante para que no de 0)
            y = samples / (2**15) 

            # 2. Detección de frecuencia
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            index = magnitudes.argmax()
            pitch_detectado = pitches.flatten()[index]
            
            if pitch_detectado > 40: # Filtramos ruidos muy bajos
                st.metric("Frecuencia Detectada", f"{pitch_detectado:.2f} Hz")
                st.success(f"¡Nota capturada!")
            else:
                st.warning("Sonido demasiado débil, intenta de nuevo.")
                
            st.audio(audio['bytes'])
            
        except Exception as e:
            st.error(f"Error procesando audio: {e}")
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
