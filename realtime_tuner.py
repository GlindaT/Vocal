import streamlit as st
import librosa
import numpy as np
from streamlit_webrtc import AudioProcessorBase, webrtc_streamer, WebRtcMode
import av

class PitchProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0.0
    
        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            audio = frame.to_ndarray().mean(axis=0)
        
        # CAMBIA EL 0.05 POR UN VALOR MÁS PEQUEÑO COMO 0.005
        if np.max(np.abs(audio)) > 0.005: 
            # El resto del código se queda igual...
            # Algoritmo ligero de detección de tono
            f0 = librosa.yin(audio.astype(np.float32), fmin=50, fmax=1000)
            self.pitch = np.nanmedian(f0)
        return frame

def render_realtime_tuner():
    # 1. Selector de Nota Objetivo
    notas = ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4']
    nota_obj = st.selectbox("Elige la nota objetivo para afinar:", notas, index=9) # A4 por defecto
    target_hz = librosa.note_to_hz(nota_obj)
    
    st.write(f"### Objetivo: {nota_obj} ({target_hz:.1f} Hz)")
    
    webrtc_ctx = webrtc_streamer(
        key="tuner",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=PitchProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    # Dentro de render_realtime_tuner
if webrtc_ctx.audio_processor:
    # Añadimos un pequeño debug visual
    volumen_debug = np.max(np.abs(webrtc_ctx.audio_processor.pitch)) # Solo para ver si llega algo
    st.write(f"Nivel de señal detectada: {volumen_debug}") 
        # 2. Lógica de la Aguja
    pitch = webrtc_ctx.audio_processor.pitch
    if pitch > 0:
            # Calculamos la diferencia porcentual para la aguja
            # -50 = muy bajo, 0 = perfecto, +50 = muy alto
            diff = (pitch - target_hz) / target_hz * 100
            
            # Gauge para mostrar qué tan cerca estamos
            st.metric("Tu frecuencia", f"{pitch:.1f} Hz")
            
            # Barra visual de afinación
            st.progress(min(max((diff + 5) / 10, 0), 1))
            
            if abs(diff) < 2:
                st.success("¡AFINADO!")
            elif diff < 0:
                st.warning("Estás BAJO de tono. ¡Sube un poco!")
            else:
                st.warning("Estás ALTO de tono. ¡Baja un poco!")
