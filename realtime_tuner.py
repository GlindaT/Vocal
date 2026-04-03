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
        
        # Filtro de ruido más flexible
        if np.max(np.abs(audio)) > 0.0001: 
            try:
                f0 = librosa.yin(audio.astype(np.float32), fmin=50, fmax=1000, sr=frame.sample_rate)
                pitch_val = float(np.nanmedian(f0))
                if pitch_val > 50:
                    self.pitch = pitch_val
                else:
                    self.pitch = 0.0
            except:
                self.pitch = 0.0
        else:
            self.pitch = 0.0
        return frame

def render_realtime_tuner():
    # Usamos st.empty para que el componente "refresque" el estado
    placeholder = st.empty()
    
    with placeholder.container():
        st.write("### 🎤 Afinador en tiempo real")
        webrtc_ctx = webrtc_streamer(
            key="tuner",
            mode=WebRtcMode.SENDONLY,
            audio_processor_factory=PitchProcessor,
            media_stream_constraints={"audio": True, "video": False},
        )

        if webrtc_ctx.audio_processor:
            pitch = webrtc_ctx.audio_processor.pitch
            
            # Forzamos la actualización visual
            st.write(f"Frecuencia detectada: {pitch:.1f} Hz")
            if pitch > 0:
                st.success("¡Audio recibido! Cantando...")
            else:
                st.info("Esperando sonido...")
