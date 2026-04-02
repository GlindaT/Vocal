import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import librosa
import plotly.graph_objects as go

# 1. Configuración de página
st.set_page_config(page_title="Afinador en Vivo")

# 2. Título
st.title("🎤 Afinador de Voz en Tiempo Real")

# --- PROCESADOR DE AUDIO ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0.0

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convertir audio a numpy
        raw_samples = frame.to_ndarray()
        y = raw_samples.astype(np.float32).flatten() / 32768.0
        sr = frame.sample_rate
        
        # Detección rápida de frecuencia
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=75, fmax=1000)
        if magnitudes.max() > 0.1: # Umbral de ruido
            pitch = pitches.flatten()[magnitudes.argmax()]
            if pitch > 0:
                # Guardamos en session_state para que la interfaz lo lea
                st.session_state["pitch_actual"] = float(pitch)
        
        return frame

# 3. Inicializar el estado si no existe
if "pitch_actual" not in st.session_state:
    st.session_state["pitch_actual"] = 0.0

# 4. Interfaz de usuario
frecuencias = {"C (Do)": 261.63, "D (Re)": 293.66, "E (Mi)": 329.63, "F (Fa)": 349.23, "G (Sol)": 392.00, "A (La)": 440.00, "B (Si)": 493.88}
nota_sel = st.selectbox("Elige tu nota objetivo", list(frecuencias.keys()))
hz_obj = frecuencias[nota_sel]

# --- EL COMPONENTE MÁGICO ---
ctx = webrtc_streamer(
    key="afinador-live",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=256,
    media_stream_constraints={"video": False, "audio": True},
    processor_factory=AudioProcessor, # Cambiado aquí para mayor estabilidad
    async_processing=True,
)

# 5. Dibujar la aguja
pitch_vivo = st.session_state["pitch_actual"]

fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = pitch_vivo,
    title = {'text': f"Afinando {nota_sel}"},
    gauge = {
        'axis': {'range': [hz_obj - 50, hz_obj + 50]},
        'bar': {'color': "black"},
        'steps': [{'range': [hz_obj-2, hz_obj+2], 'color': "green"}],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': hz_obj}
    }
))

# Contenedor dinámico
placeholder = st.empty()
with placeholder:
    st.plotly_chart(fig, use_container_width=True)

# EL MOTOR DEL MOVIMIENTO: Si el micro está encendido, forzamos el refresco
if ctx.state.playing:
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
