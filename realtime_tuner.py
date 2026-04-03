import streamlit as st
import librosa
import numpy as np
from streamlit_webrtc import AudioProcessorBase, webrtc_streamer, WebRtcMode
import av

class PitchProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0.0
    
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convertir a formato numpy
        audio = frame.to_ndarray().mean(axis=0)
        
        # Evitar división por cero
        max_val = np.max(np.abs(audio))
        if max_val > 0.001: 
            audio = audio / max_val
            
            # Detectar pitch (Yin es preciso pero requiere señal clara)
            try:
                # Usamos una muestra más pequeña para procesar en tiempo real
                f0 = librosa.yin(audio.astype(np.float32), fmin=50, fmax=1000, sr=48000)
                pitch_val = float(np.nanmedian(f0))
                if pitch_val > 50: # Filtro de ruido
                    self.pitch = pitch_val
            except:
                self.pitch = 0.0
        else:
            self.pitch = 0.0
            
        return frame

def render_realtime_tuner():
    # 1. Selector de Nota
    notas = ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4']
    nota_obj = st.selectbox("Elige la nota objetivo:", notas, index=9)
    target_hz = librosa.note_to_hz(nota_obj)
    
    st.write(f"### Objetivo: {nota_obj} ({target_hz:.1f} Hz)")
    
    # 2. Configuración del Streamer
    webrtc_ctx = webrtc_streamer(
        key="tuner",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=PitchProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    # 3. Lógica de visualización
    if webrtc_ctx.audio_processor:
        pitch = webrtc_ctx.audio_processor.pitch
        
        # DEBUG: Si el pitch es 0, el micro no está detectando nada o el volumen es muy bajo
        if pitch > 0:
            st.metric("Tu frecuencia actual", f"{pitch:.1f} Hz")
            
            # Cálculo de afinación
            diff = (pitch - target_hz) / target_hz * 100
            
            # Barra visual de afinación
            # Convertimos la diferencia porcentual en una posición de barra
            bar_value = (diff + 10) / 20 # Centrado en 0, rango de +/- 10%
            st.progress(min(max(bar_value, 0), 1))
            
            if abs(diff) < 1.5:
                st.success("¡AFINADO!")
            elif diff < 0:
                st.warning("Estás BAJO de tono. ¡Sube un poco!")
            else:
                st.warning("Estás ALTO de tono. ¡Baja un poco!")
        else:
            st.info("🎤 Cantando... esperando tono claro...")

