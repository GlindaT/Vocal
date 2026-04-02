import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import librosa
import plotly.graph_objects as go

st.set_page_config(page_title="Afinador Pro En Vivo")

# --- LÓGICA DE PROCESAMIENTO ---
if "pitch" not in st.session_state:
    st.session_state["pitch"] = 0

class AfinadorVivo(AudioProcessorBase):
    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        raw_samples = frame.to_ndarray()
        # Convertir a mono y normalizar
        y = raw_samples.astype(np.float32).flatten() / 32768.0
        sr = frame.sample_rate
        
        # Detección rápida de pitch
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
        if magnitudes.max() > 0.2: # Umbral de ruido
            pitch = pitches.flatten()[magnitudes.argmax()]
            if pitch > 0:
                st.session_state["pitch"] = float(pitch)
        return frame

# --- INTERFAZ ---
st.title("🎤 Afinador en Tiempo Real")
frecuencias = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.0, "A": 440.0, "B": 493.88}
nota_obj = st.selectbox("Nota Objetivo", list(frecuencias.keys()))
hz_obj = frecuencias[nota_obj]

# El componente que conecta el micro en vivo
ctx = webrtc_streamer(
    key="afinador-realtime",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=512,
    media_stream_constraints={"video": False, "audio": True},
    processor_factory=AfinadorVivo,
    async_processing=True,
)

# --- DIBUJO DE LA AGUJA ---
pitch_actual = st.session_state["pitch"]

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = pitch_actual,
    title = {'text': f"Buscando {nota_obj} ({hz_obj} Hz)"},
    gauge = {
        'axis': {'range': [hz_obj - 50, hz_obj + 50]},
        'bar': {'color': "black"},
        'steps': [
            {'range': [hz_obj-2, hz_obj+2], 'color': "green"} # Zona de afinado
        ],
        'threshold': {'line': {'color': "red", 'width': 5}, 'value': hz_obj}
    }
))

# Contenedor para que el gráfico no parpadee al refrescar
placeholder = st.empty()
with placeholder:
    st.plotly_chart(fig, use_container_width=True)

# El truco final: Si el micro está encendido, forzamos el refresco constante
if ctx.state.playing:
    st.write("🎤 Analizando audio en vivo...")
    st.rerun() # ESTO HACE QUE LA AGUJA SE MUEVA EN VIVO

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
