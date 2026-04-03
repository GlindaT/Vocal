import streamlit as st
import librosa
import numpy as np
from streamlit_webrtc import AudioProcessorBase, webrtc_streamer, WebRtcMode
import av

class PitchProcessor(AudioProcessorBase):
    def __init__(self):
        self.pitch = 0.0
    
    # AQUÍ VA EL MÉTODO QUE ME PREGUNTAS:
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # 1. Convertimos el frame a formato que numpy pueda leer
        audio = frame.to_ndarray().mean(axis=0)
        
        # 2. Análisis de frecuencia
        max_val = np.max(np.abs(audio))
        if max_val > 0.001: 
            audio = audio / max_val
            try:
                # Usamos frame.sample_rate para que coincida con tu micro
                f0 = librosa.yin(audio.astype(np.float32), fmin=50, fmax=1000, sr=frame.sample_rate)
                pitch_val = float(np.nanmedian(f0))
                if pitch_val > 50:
                    self.pitch = pitch_val
            except:
                self.pitch = 0.0
        else:
            self.pitch = 0.0
            
        # 3. MUY IMPORTANTE: Devolvemos el frame para que el stream no se congele
        return frame 

# ... luego sigue tu función render_realtime_tuner() ...
