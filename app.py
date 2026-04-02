import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import librosa
import plotly.graph_objects as go

# 1. Configuración de página
st.set_page_config(page_title="Afinador Pro En Vivo", layout="wide")

# --- PROCESADOR DE AUDIO ---
class AfinadorProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0.0

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        raw_samples = frame.to_ndarray()
        y = raw_samples.astype(np.float32).flatten() / 32768.0
        sr = frame.sample_rate
        
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
        if magnitudes.max() > 0.1:
            pitch = pitches.flatten()[magnitudes.argmax()]
            if pitch > 0:
                st.session_state["pitch_vivo"] = float(pitch)
        return frame

# --- INTERFAZ ---
st.title("🎤 Afinador en Tiempo Real")

if "pitch_vivo" not in st.session_state:
    st.session_state["pitch_vivo"] = 0.0

frecuencias = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.00, "A": 440.00, "B": 493.88}
nota_obj = st.selectbox("Nota Objetivo", list(frecuencias.keys()))
hz_obj = frecuencias[nota_obj]

# EL COMPONENTE DE MICRO (Aquí definimos 'ctx')
ctx = webrtc_streamer(
    key="afinador-final-v1",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:19302//google.com"]}]
    },
    media_stream_constraints={"video": False, "audio": True},
    audio_processor_factory=AfinadorProcessor,
    async_processing=True,
)

# --- DIBUJO DE LA AGUJA ---
actual = st.session_state["pitch_vivo"]

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = actual,
    title = {'text': f"Buscando {nota_obj} ({hz_obj} Hz)"},
    gauge = {
        'axis': {'range': [hz_obj - 50, hz_obj + 50]},
        'bar': {'color': "black"},
        'steps': [{'range': [hz_obj-2, hz_obj+2], 'color': "green"}],
        'threshold': {'line': {'color': "red", 'width': 5}, 'value': hz_obj}
    }
))

placeholder = st.empty()
with placeholder:
    st.plotly_chart(fig, use_container_width=True)

# MOTOR DE MOVIMIENTO (Aquí usamos 'ctx')
if ctx.state.playing:
    st.rerun()
