import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import librosa
import plotly.graph_objects as go

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Karaoke AI Pro", layout="wide")

# --- PROCESADOR DE AUDIO EN VIVO ---
class AfinadorProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0.0

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        raw_samples = frame.to_ndarray()
        y = raw_samples.astype(np.float32).flatten() / 32768.0
        sr = frame.sample_rate
        
        # Detección rápida
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
        if magnitudes.max() > 0.1:
            pitch = pitches.flatten()[magnitudes.argmax()]
            if pitch > 0:
                st.session_state["pitch_vivo"] = float(pitch)
        return frame

# --- INTERFAZ PRINCIPAL ---
st.title("🎤 Mi App de Karaoke Pro")

# Inicializar estado del afinador
if "pitch_vivo" not in st.session_state:
    st.session_state["pitch_vivo"] = 0.0

# Crear pestañas (ESTO CORRIGE EL NAMEERROR)
tabs = st.tabs(["🎯 Afinador", "✂️ Separador", "🎼 Preparación", "🎙️ Estudio", "⚙️ Config"])

# --- PESTAÑA 1: AFINADOR ---
with tabs[0]:
    st.header("Afinador en Tiempo Real")
    
    frecuencias = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.00, "A": 440.00, "B": 493.88}
    nota_obj = st.selectbox("Nota Objetivo", list(frecuencias.keys()), key="sel_nota")
    hz_obj = frecuencias[nota_obj]

    # Componente de Micro
    ctx = webrtc_streamer(
        key="afinador-realtime",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:19302google.com"]}]},
        media_stream_constraints={"video": False, "audio": True},
        audio_processor_factory=AfinadorProcessor,
        async_processing=True,
    )

    # Crea un espacio que se actualiza solo
    contenedor_aguja = st.empty()
    
    actual = st.session_state["pitch_vivo"]
    
    # Crear la figura (tu código de Plotly está perfecto)
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

    # Dibujar dentro del contenedor vacío
    with contenedor_aguja:
        st.plotly_chart(fig, use_container_width=True)

    # Motor de movimiento
    if ctx.state.playing:
        st.rerun()

# --- PESTAÑA 2: SEPARADOR ---
with tabs[1]:
    st.header("Separador de Voz (AI)")
    st.info("Sube un archivo para comenzar la separación.")
    archivo = st.file_uploader("Sube tu canción", type=['mp3', 'wav'])

# --- RESTO DE PESTAÑAS (Para evitar errores de índice) ---
with tabs[2]: st.header("Modo Práctica")
with tabs[3]: st.header("Grabación de Estudio")
with tabs[4]: st.header("Ajustes")
