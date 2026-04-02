import streamlit as st
from streamlit_mic_recorder import mic_recorder
import io
import librosa
import numpy as np
import plotly.graph_objects as go
from pydub import AudioSegment

# --- PROCESADOR DE AUDIO EN VIVO ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convertir audio a numpy
        raw_samples = frame.to_ndarray()
        y = raw_samples.astype(np.float32).flatten() / 32768.0
        sr = frame.sample_rate
        
        # Detectar frecuencia rápido
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
        if magnitudes.max() > 0.1: # Si hay suficiente volumen
            pitch = pitches.flatten()[magnitudes.argmax()]
            if pitch > 0:
                st.session_state["pitch_vivo"] = float(pitch)
        
        return frame

# Configuración de la página
st.set_page_config(page_title="Karaoke AI", layout="wide")

# Título y Navegación
st.title("🎤 Mi App de Karaoke Pro")
tabs = st.tabs(["🎯 Afinador", "✂️ Separador", "🎼 Preparación", "🎙️ Estudio", "⚙️ Config"])

# --- PESTAÑA 1: AFINADOR (REEMPLAZA TODO EL CONTENIDO DE ESTA PESTAÑA) ---
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av # Asegúrate de añadir 'PyAV' al requirements.txt si da error

class AfinadorProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch_actual = 0

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # 1. Convertir el frame de audio a array de numpy
        raw_samples = frame.to_ndarray()
        # Convertir a flotantes y promediar canales si es estéreo
        y = raw_samples.astype(np.float32).flatten() / 32768.0
        sr = frame.sample_rate

        # 2. Detectar frecuencia (usamos algo más rápido que piptrack para tiempo real)
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
        index = magnitudes.argmax()
        pitch = pitches.flatten()[index]
        
        if pitch > 0:
            self.pitch_actual = pitch
            
        return frame

# --- PESTAÑA 1: AFINADOR ---
with tabs[0]:
    st.header("🎯 Afinador de Voz")
    
    frecuencias = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.00, "A": 440.00, "B": 493.88}
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        nota_sel = st.selectbox("Nota Objetivo", list(frecuencias.keys()), key="nota_afin")
        hz_obj = frecuencias[nota_sel]
    
    # Grabador automático: Al darle a Stop procesa de inmediato
    with col_b:
        audio = mic_recorder(start_prompt="🎤 Empezar a Afinar", stop_prompt="⏹️ Analizar", key='afinador_v3')

    # Si no hay audio aún, mostramos la aguja en 0
    pitch_mostrar = 0.0
    
    if audio:
        try:
            # Procesamiento flash
            audio_seg = AudioSegment.from_file(io.BytesIO(audio['bytes']))
            samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
            y = samples / (2**15)
            sr = audio_seg.frame_rate
            
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
            pitch_mostrar = float(pitches.flatten()[magnitudes.argmax()])
        except:
            pass

    # --- EL GRÁFICO CIRCULAR ---
    # Ajustamos el rango para que la aguja siempre se vea
    rango_min = min(hz_obj, pitch_mostrar) - 40 if pitch_mostrar > 0 else hz_obj - 40
    rango_max = max(hz_obj, pitch_mostrar) + 40 if pitch_mostrar > 0 else hz_obj + 40

    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = pitch_mostrar,
        title = {'text': f"Nota: {nota_sel}"},
        delta = {'reference': hz_obj},
        gauge = {
            'axis': {'range': [rango_min, rango_max]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [hz_obj-2, hz_obj+2], 'color': "lightgreen"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': hz_obj}
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)

    if pitch_mostrar > 0:
        diff = pitch_mostrar - hz_obj
        if abs(diff) < 2:
            st.success("🎯 ¡AFINADO!")
        elif diff < 0:
            st.info("🔼 Sube un poco el tono")
        else:
            st.warning("🔽 Baja un poco el tono")
        
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
