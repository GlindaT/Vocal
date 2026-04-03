import streamlit as st
import librosa
import numpy as np
from streamlit_webrtc import AudioProcessorBase, webrtc_streamer, WebRtcMode
import av

class PitchProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0.0
    
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convertir a numpy
        audio = frame.to_ndarray().mean(axis=0)
        
        # Procesar si hay suficiente volumen
        if np.max(np.abs(audio)) > 0.001: 
            # Asegurar que el audio tenga la forma correcta para librosa
            samples = audio.astype(np.float32)
            # Usamos Yin para detectar frecuencia fundamental
            f0 = librosa.yin(samples, fmin=50, fmax=1000, sr=48000)
            self.pitch = float(np.nanmedian(f0))
        
        return frame

def render_realtime_tuner():
    # 1. Selector de Nota
    notas = ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4']
    nota_obj = st.selectbox("Elige la nota objetivo:", notas, index=9)
    target_hz = librosa.note_to_hz(nota_obj)
    
    st.write(f"### Objetivo: {nota_obj} ({target_hz:.1f} Hz)")
    
    # 2. Streamer
    webrtc_ctx = webrtc_streamer(
        key="tuner",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=PitchProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    # 3. Lógica de visualización (DEBE ESTAR DENTRO DE LA FUNCIÓN)
    if webrtc_ctx.audio_processor:
        pitch = webrtc_ctx.audio_processor.pitch
        
        if pitch > 0:
            st.metric("Tu frecuencia actual", f"{pitch:.1f} Hz")
            
            # Cálculo de afinación
            diff = (pitch - target_hz) / target_hz * 100
            # Normalizar para la barra (de 0 a 1)
            bar_value = min(max((diff + 5) / 10, 0), 1)
            st.progress(bar_value)
            
            if abs(diff) < 2:
                st.success("¡AFINADO!")
            elif diff < 0:
                st.warning("Estás BAJO de tono. ¡Sube un poco!")
            else:
                st.warning("Estás ALTO de tono. ¡Baja un poco!")
        else:
            st.info("🎤 Cantando... esperando tono...")
