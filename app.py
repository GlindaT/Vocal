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

# --- EN TU PESTAÑA 1 ---
with tabs[0]:
    st.header("🎯 Afinador en Tiempo Real")
    
    # Iniciamos el streaming
    ctx = webrtc_streamer(
        key="afinador-live",
        audio_receiver_size=512,
        rtc_configuration={"iceServers": [{"urls": ["stun:://google.com"]}]},
        media_stream_constraints={"video": False, "audio": True},
        processor_factory=AfinadorProcessor,
    )

    # Si el micro está encendido, mostramos la aguja
    if ctx.audio_processor:
        pitch_vivo = ctx.audio_processor.pitch_actual
        
        # Aquí va tu código del gráfico de Plotly (go.Figure) 
        # usando 'value = pitch_vivo'
        
        # TRUCO: Para que Streamlit se refresque solo y la aguja se mueva:
        st.empty() # Limpia el contenedor
        # (Aquí pondrías el fig.show o st.plotly_chart)
        st.plotly_chart(tu_figura_de_antes, use_container_width=True)
        
        # Forzar refresco cada 0.1 segundos
        st.rerun() 

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
