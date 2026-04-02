import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import librosa
import plotly.graph_objects as go

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

# --- EN LA PESTAÑA 1 ---
with tabs[0]:
    st.header("🎯 Afinador en Vivo")
    
    # Inicializar el estado si no existe
    if "pitch_vivo" not in st.session_state:
        st.session_state["pitch_vivo"] = 0.0

    # Selector de nota objetivo
    frecuencias = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.0, "A": 440.0, "B": 493.88}
    nota_sel = st.selectbox("Nota Objetivo", list(frecuencias.keys()))
    hz_obj = frecuencias[nota_sel]

    # COMPONENTE DE MICRO EN VIVO
    webrtc_ctx = webrtc_streamer(
        key="afinador-live",
        mode=WebRtcMode.SENDRECV,
        audio_receiver_size=256,
        webrtc_ctx = webrtc_streamer(
        key="afinador-live",
        mode=WebRtcMode.SENDRECV,
        audio_receiver_size=256,
        # Eliminamos la línea compleja de iceServers para usar la de defecto
        rtc_configuration={ 
            "iceServers": [{"urls": ["stun:://google.com"]}] 
        },
        media_stream_constraints={"video": False, "audio": True},
        async_processing=True,
    )
        media_stream_constraints={"video": False, "audio": True},
        async_processing=True,
    )

    # Mostrar la aguja con el valor en vivo
    actual = st.session_state["pitch_vivo"]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = actual,
        gauge = {
            'axis': {'range': [hz_obj - 50, hz_obj + 50]},
            'steps': [{'range': [hz_obj-2, hz_obj+2], 'color': "green"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': hz_obj}
        }
    ))
    
    # El truco: Mostrar el gráfico y forzar el refresco
    st.plotly_chart(fig, use_container_width=True)
    
    if webrtc_ctx.state.playing:
        st.write("🎤 Escuchando...")
        st.rerun() # Esto hace que la aguja se mueva constantemente
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
