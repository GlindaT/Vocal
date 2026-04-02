# audio_analyzer.py
import librosa
import numpy as np
import io

def get_pitch_from_bytes(audio_bytes):
    # Convertimos los bytes del grabador a un formato que librosa entienda
    audio_data, sr = librosa.load(io.BytesIO(audio_bytes), sr=22050)
    
    # Usamos una técnica llamada 'piptrack' para detectar la frecuencia fundamental
    pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
    
    # Obtenemos la frecuencia más dominante
    index = np.argmax(magnitudes)
    pitch = pitches.ravel()[index]
    
    return pitch
