# realtime_tuner.py
from streamlit_webrtc import AudioProcessorBase, WebRtcMode, webrtc_streamer
import av
import librosa
import numpy as np
import streamlit as st

class PitchDetector(AudioProcessorBase):
    def __init__(self):
        self.current_pitch = 0.0
        self.note = "--"
    
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convertir el frame de audio a numpy array
        raw_samples = frame.to_ndarray()
        
        # Convertir a mono si es estéreo
        if raw_samples.ndim > 1:
            samples = raw_samples.mean(axis=0)
        else:
            samples = raw_samples
            
        # Normalizar a float32 [-1.0, 1.0]
        samples = samples.astype(np.float32) / 32768.0
        
        # Procesar solo si tenemos suficientes muestras
        if len(samples) > 1024:
            try:
                # Usamos el algoritmo YIN de librosa para detectar pitch
                f0, voiced_flag, voiced_probs = librosa.pyin(
                    samples,
                    fmin=librosa.note_to_hz('C2'),  # 65 Hz
                    fmax=librosa.note_to_hz('C7'),  # 2093 Hz (rango vocal)
                    sr=frame.sample_rate
                )
                
                # Filtrar valores válidos (no NaN)
                valid_pitches = f0[~np.isnan(f0)]
                if len(valid_pitches) > 0:
                    pitch = np.median(valid_pitches)
                    if pitch > 0:
                        self.current_pitch = pitch
                        # Convertir frecuencia a nombre de nota
                        try:
                            self.note = librosa.hz_to_note(pitch)
                        except:
                            self.note = "--"
            except Exception:
                pass
                
        return frame

def render_realtime_tuner():
    st.write("### 🎤 Activa tu micrófono y empieza a cantar")
    st.write("El analizador se actualiza automáticamente mientras cantas.")
    
    # Iniciar el streamer de WebRTC
    ctx = webrtc_streamer(
        key="pitch-detector",
        mode=WebRtcMode.SENDONLY,  # Solo enviamos audio (micrófono), no recibimos video
        audio_processor_factory=PitchDetector,
        media_stream_constraints={"audio": True, "video": False},
        async_processing=True,
    )
    
    # Mostrar resultados si el procesador está activo
    if ctx.audio_processor:
        # Usamos st.empty() para actualizar sin parpadear
        pitch_placeholder = st.empty()
        gauge_placeholder = st.empty()
        note_placeholder = st.empty()
        
        # Leer valores actuales
        pitch = ctx.audio_processor.current_pitch
        note = ctx.audio_processor.note
        
        if pitch > 0:
            # Mostramos métricas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Frecuencia", f"{pitch:.1f} Hz")
            with col2:
                st.metric("Nota detectada", note)
            
            # Mostrar el gauge (importa tu función de tuner_ui aquí)
            from tuner_ui import render_tuner_gauge
            render_tuner_gauge(pitch)
            
            # Feedback visual de afinación
            target = 440.0  # Podrías hacer esto dinámico según la nota seleccionada
            diff = abs(pitch - target)
            
            if diff < 5:
                st.success("🎯 ¡Afinado perfecto!")
            elif pitch < target:
                st.warning("⬆️ Sube un poco el tono")
            else:
                st.warning("⬇️ Baja un poco el tono")
        else:
            st.info("Esperando sonido... canta cerca del micrófono")
    
    return ctx
