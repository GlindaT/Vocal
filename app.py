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
frecuencias_notas = {
    "C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, 
    "G": 392.00, "A": 440.00, "B": 493.88
}

with tabs[0]:
    st.header("🎯 Afinador de Precisión")
    nota_ref = st.selectbox("Nota objetivo", list(frecuencias_notas.keys()))
    hz_objetivo = frecuencias_notas[nota_ref]

    audio = mic_recorder(start_prompt="Grabar nota", stop_prompt="Detener", key='afinador')

    if audio:
        try:
            audio_seg = AudioSegment.from_file(io.BytesIO(audio['bytes']))
            samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
            sr = audio_seg.frame_rate
            y = samples / (2**15) 

            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            index = magnitudes.argmax()
            pitch_detectado = pitches.flatten()[index]

            if pitch_detectado > 40:
                # Calcular la diferencia
                diferencia = pitch_detectado - hz_objetivo
                
                col1, col2 = st.columns(2)
                col1.metric("Detectado", f"{pitch_detectado:.2f} Hz")
                col2.metric("Objetivo", f"{hz_objetivo:.2f} Hz", f"{diferencia:.2f} Hz")

                # Lógica de guía para el usuario
                if abs(diferencia) < 2:
                    st.success(f"✅ ¡Perfecto! Estás en el clavo con {nota_ref}")
                    st.balloons()
                elif diferencia > 0:
                    st.warning(f"🔼 Demasiado agudo. ¡Baja un poco la tensión!")
                else:
                    st.info(f"🔽 Demasiado grave. ¡Sube un poco la tensión!")
            else:
                st.warning("⚠️ No se detectó un sonido claro. Intenta grabar más cerca.")
                
            st.audio(audio['bytes'])
            
        except Exception as e:
            st.error(f"Error: {e}")
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
