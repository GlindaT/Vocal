import streamlit as st
from streamlit_mic_recorder import mic_recorder
import librosa
import numpy as np
import io
from pydub import AudioSegment

# Configuración de la página
st.set_page_config(page_title="Karaoke AI", layout="wide")

# Título y Navegación
st.title("🎤 Mi App de Karaoke Pro")
tabs = st.tabs(["🎯 Afinador", "✂️ Separador", "🎼 Preparación", "🎙️ Estudio", "⚙️ Config"])

# --- PESTAÑA 1: AFINADOR (REEMPLAZA TODO EL CONTENIDO DE ESTA PESTAÑA) ---
with tabs[0]:
    st.header("🎯 Afinador de Precisión")
    
    # 1. Diccionario de frecuencias
    frecuencias_notas = {
        "C (Do)": 261.63, "D (Re)": 293.66, "E (Mi)": 329.63, 
        "F (Fa)": 349.23, "G (Sol)": 392.00, "A (La)": 440.00, "B (Si)": 493.88
    }
    
    col_sel, col_mic = st.columns([1, 2])
    with col_sel:
        nota_ref = st.selectbox("Nota objetivo", list(frecuencias_notas.keys()))
        hz_objetivo = frecuencias_notas[nota_ref]
    
    with col_mic:
        audio = mic_recorder(start_prompt="🎤 Grabar nota", stop_prompt="🛑 Detener", key='afinador')

    if audio:
        try:
            # Procesamiento de audio
            audio_seg = AudioSegment.from_file(io.BytesIO(audio['bytes']))
            samples = np.array(audio_seg.get_array_of_samples()).astype(np.float32)
            sr = audio_seg.frame_rate
            y = samples / (2**15) 

            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            index = magnitudes.argmax()
            pitch_detectado = pitches.flatten()[index]

            if pitch_detectado > 40:
                diferencia = pitch_detectado - hz_objetivo
                
                # --- MÉTRICAS ---
                c1, c2 = st.columns(2)
                c1.metric("Detectado", f"{pitch_detectado:.2f} Hz")
                c2.metric("Objetivo", f"{hz_objetivo:.2f} Hz", f"{diferencia:.2f} Hz")

                # --- GRÁFICO DE AGUJA (BARRA) ---
                st.write("### Indicador de afinación")
                # Rango de +- 20 Hz para que el movimiento sea sensible
                rango = 20 
                progreso = np.clip((diferencia + rango) / (rango * 2), 0.0, 1.0)
                
                # Visualización visual
                st.progress(float(progreso))
                
                if 0.48 <= progreso <= 0.52:
                    st.success("🎯 ¡AFINADO! Perfecto.")
                    st.balloons()
                elif progreso < 0.48:
                    st.warning("🔽 MÁS AGUDO (Tensa la cuerda/voz)")
                else:
                    st.warning("🔼 MÁS GRAVE (Afloja la cuerda/voz)")
            else:
                st.error("No se detectó sonido. Intenta de nuevo.")
                
            st.audio(audio['bytes'])
            
        except Exception as e:
            st.error(f"Error técnico: {e}")
# --- PESTAÑA 2: SEPARADOR ---
with tabs[1]:
    st.header("Separador de Voz (AI)")
    archivo = st.file_uploader("Sube tu canción", type=['mp3', 'wav'])
    if archivo:
        st.info("Procesando separación... (Nota: Esto requiere mucha CPU)")

# --- PESTAÑA 3: PREPARACIÓN ---
with tabs[2]:
    st.header("Modo Práctica")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🎵 Letra de la canción")
        st.code("La la la... (Visualización de pentagrama aquí)")
    with col2:
        st.write("Informe de afinación")

# --- PESTAÑA 4: ESTUDIO ---
with tabs[3]:
    st.header("Grabación de Estudio")
    st.button("🔴 Iniciar Grabación Maestra")

# --- PESTAÑA 5: CONFIGURACIONES ---
with tabs[4]:
    st.header("Ajustes")
    st.slider("Dificultad", 1, 10, 5)
    st.color_picker("Color de letra", "#00FFAA")
