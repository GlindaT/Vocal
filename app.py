import streamlit as st
import os
import json
from datetime import datetime
# Importante: Esta línea debe ir al principio, no dentro de las tabs
from tuner_ui import render_tuner_gauge

# -----------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------
st.set_page_config(page_title="Karaoke App", layout="wide")

# Crear carpetas si no existen
os.makedirs("data", exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/separated", exist_ok=True)
os.makedirs("data/recordings", exist_ok=True)

LIBRARY_FILE = "data/library.json"

# Si no existe library.json, crearlo vacío
if not os.path.exists(LIBRARY_FILE):
    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------
def load_library():
    with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_library(data):
    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_song_to_library(title, artist, original_path, vocals_path, instrumental_path, lyrics=""):
    library = load_library()
    song_id = f"song_{len(library) + 1:03d}"
    new_song = {
        "id": song_id,
        "title": title,
        "artist": artist,
        "original_path": original_path,
        "vocals_path": vocals_path,
        "instrumental_path": instrumental_path,
        "lyrics": lyrics,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    library.append(new_song)
    save_library(library)

def get_song_options():
    library = load_library()
    return [f"{song['id']} - {song['title']} / {song['artist']}" for song in library]

def get_song_by_option(option_text):
    library = load_library()
    for song in library:
        label = f"{song['id']} - {song['title']} / {song['artist']}"
        if label == option_text:
            return song
    return None

# -----------------------------
# SESSION STATE
# -----------------------------
if "num_mics" not in st.session_state:
    st.session_state.num_mics = 1
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medio"
if "lyric_color" not in st.session_state:
    st.session_state.lyric_color = "#FFFFFF"

# -----------------------------
# INTERFAZ PRINCIPAL
# -----------------------------
st.title("🎤 Karaoke App")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Afinador",
    "Separador",
    "Preparación",
    "Estudio",
    "Configuraciones"
])

# -----------------------------
# PESTAÑA 1: AFINADOR (CORREGIDA)
# -----------------------------
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import io
import librosa
import numpy as np
from pydub import AudioSegment
import plotly.graph_objects as go

with tab1:
    st.header("Afinador de Precisión")
    
    # 1. EL USUARIO ELIGE LA NOTA OBJETIVO
    st.write("### 1. Elige la nota que quieres afinar")
    notas_objetivo = ['C4 (Do)', 'C#4 (Do#)', 'D4 (Re)', 'D#4 (Re#)', 'E4 (Mi)', 'F4 (Fa)', 'F#4 (Fa#)', 'G4 (Sol)', 'G#4 (Sol#)', 'A4 (La)', 'A#4 (La#)', 'B4 (Si)']
    # Extraemos solo la parte técnica (ej: 'A4')
    nota_seleccionada = st.selectbox("Nota Objetivo:", notas_objetivo, index=9).split(" ")[0] 
    
    # Calculamos la frecuencia exacta de esa nota
    target_hz = librosa.note_to_hz(nota_seleccionada)
    st.info(f"🎯 Frecuencia objetivo para {nota_seleccionada}: **{target_hz:.2f} Hz**")

    # 2. EL USUARIO GRABA SU VOZ
    st.write("### 2. Canta la nota")
    audio = mic_recorder(
        start_prompt="🎤 Iniciar Grabación",
        stop_prompt="⏹️ Analizar Afinación",
        just_once=False,
        use_container_width=True,
        key='tuner'
    )

    # 3. ANÁLISIS Y COMPARACIÓN VISUAL
    if audio:
        with st.spinner("Analizando tu voz..."):
            audio_segment = AudioSegment.from_file(io.BytesIO(audio['bytes']))
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_io.seek(0)
            
            y, sr = librosa.load(wav_io, sr=None)
            f0, _, _ = librosa.pyin(y, fmin=50, fmax=1000)
            pitch = np.nanmedian(f0)
            
            if not np.isnan(pitch):
                # Calcular la diferencia en "Cents" (medida musical)
                # 0 es perfecto. Negativo es bajo (Flat). Positivo es alto (Sharp).
                cents_diff = 1200 * np.log2(pitch / target_hz)
                
                # --- GRÁFICO DE LA AGUJA (PLOTLY GAUGE) ---
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = pitch,
                    title = {'text': f"Tu voz vs {nota_seleccionada}"},
                    delta = {'reference': target_hz, 'position': "top"},
                    gauge = {
                        'axis': {'range': [target_hz * 0.9, target_hz * 1.1]}, # Rango visual
                        'bar': {'color': "black"}, # La aguja
                        'steps': [
                            {'range': [target_hz * 0.9, target_hz * 0.98], 'color': "#ff4b4b"},  # Rojo (Bajo)
                            {'range': [target_hz * 0.98, target_hz * 1.02], 'color': "#28a745"}, # Verde (Afinado)
                            {'range': [target_hz * 1.02, target_hz * 1.1], 'color': "#ff4b4b"}   # Rojo (Alto)
                        ],
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
                
                # Feedback en texto
                st.write(f"Tu frecuencia real: **{pitch:.2f} Hz**")
                if abs(cents_diff) <= 15:
                    st.success("🎯 ¡Perfecto! Estás en el tono.")
                elif cents_diff < 0:
                    st.warning(f"📉 Estás BAJO de tono (Te faltan {abs(cents_diff):.0f} cents). ¡Sube un poco!")
                else:
                    st.warning(f"📈 Estás ALTO de tono (Te sobran {cents_diff:.0f} cents). ¡Baja un poco!")
            else:
                st.error("No detecté una nota clara. Asegúrate de cantar fuerte y claro cerca del micrófono.")
# -----------------------------
# PESTAÑA 2: SEPARADOR
# -----------------------------
with tab2:
    st.header("Separador")
    st.write("Sube una canción para guardarla en la biblioteca.")
    
    song_title = st.text_input("Nombre de la canción")
    song_artist = st.text_input("Artista")
    song_lyrics = st.text_area("Letra (opcional)", height=150)
    uploaded_song = st.file_uploader("Sube una canción", type=["mp3", "wav"], key="separator_upload")
    
    if uploaded_song is not None:
        st.audio(uploaded_song)
    
    if st.button("Guardar canción en biblioteca"):
        if uploaded_song is None:
            st.error("Debes subir una canción.")
        elif song_title.strip() == "":
            st.error("Debes escribir el nombre de la canción.")
        elif song_artist.strip() == "":
            st.error("Debes escribir el artista.")
        else:
            original_path = os.path.join("data/uploads", uploaded_song.name)
            with open(original_path, "wb") as f:
                f.write(uploaded_song.read())
            
            library = load_library()
            next_id = f"song_{len(library) + 1:03d}"
            song_folder = os.path.join("data/separated", next_id)
            os.makedirs(song_folder, exist_ok=True)
            
            vocals_path = os.path.join(song_folder, "vocals.wav")
            instrumental_path = os.path.join(song_folder, "instrumental.wav")
            
            # Por ahora archivos vacíos (placeholder)
            with open(vocals_path, "wb") as f:
                f.write(b"")
            with open(instrumental_path, "wb") as f:
                f.write(b"")
            
            add_song_to_library(
                title=song_title,
                artist=song_artist,
                original_path=original_path,
                vocals_path=vocals_path,
                instrumental_path=instrumental_path,
                lyrics=song_lyrics
            )
            st.success("Canción guardada correctamente en la biblioteca.")

# -----------------------------
# PESTAÑA 3: PREPARACIÓN
# -----------------------------
with tab3:
    st.header("Preparación")
    song_options = get_song_options()
    
    if len(song_options) == 0:
        st.warning("Todavía no hay canciones guardadas en la biblioteca.")
    else:
        selected_song_option = st.selectbox("Selecciona una pista guardada", song_options)
        selected_song = get_song_by_option(selected_song_option)
        
        if selected_song:
            st.write("### Información de la pista")
            st.write("Título:", selected_song["title"])
            st.write("Artista:", selected_song["artist"])
            
            if selected_song["lyrics"]:
                st.markdown(
                    f"<p style='color:{st.session_state.lyric_color}; font-size:22px;'>{selected_song['lyrics']}</p>",
                    unsafe_allow_html=True
                )

# -----------------------------
# PESTAÑA 4: ESTUDIO
# -----------------------------
from audio_recorder_streamlit import audio_recorder

with tab4:
    st.header("Estudio - Grabación")
    
    song_options = get_song_options()
    if len(song_options) == 0:
        st.warning("No hay pistas guardadas todavía.")
    else:
        selected_song_option = st.selectbox("Selecciona una pista para grabar", song_options, key="studio_select")
        
        # --- AQUÍ VA EL BOTÓN DE GRABAR ---
        st.write("Presiona el botón para empezar a grabar tu voz:")
        audio_bytes = audio_recorder(
            text="Haz clic para grabar",
            recording_color="#e74c3c",
            neutral_color="#96a5a6",
            icon_name="microphone",
            icon_size="2x",
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            # Guardar el archivo grabado
            if st.button("Guardar grabación"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"data/recordings/grabacion_{timestamp}.wav"
                with open(file_path, "wb") as f:
                    f.write(audio_bytes)
                st.success(f"Grabación guardada en {file_path}")
# -----------------------------
# PESTAÑA 5: CONFIGURACIONES
# -----------------------------
with tab5:
    st.header("Configuraciones")
    
    st.session_state.num_mics = st.selectbox(
        "Cantidad de micrófonos",
        [1, 2, 3, 4],
        index=[1, 2, 3, 4].index(st.session_state.num_mics)
    )
    
    st.session_state.difficulty = st.selectbox(
        "Nivel de dificultad",
        ["Fácil", "Medio", "Difícil"],
        index=["Fácil", "Medio", "Difícil"].index(st.session_state.difficulty)
    )
    
    st.session_state.lyric_color = st.color_picker(
        "Color de la letra",
        st.session_state.lyric_color
    )
    
    st.success("Configuración guardada en la sesión actual.")
