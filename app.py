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

with tab1:
    st.header("Afinador en Tiempo Real")
    
    # Este componente es el estándar de oro en estabilidad
    audio = mic_recorder(
        start_prompt="🎤 Iniciar Afinador",
        stop_prompt="⏹️ Detener",
        just_once=False,
        use_container_width=True,
        key='tuner'
    )
    if audio:
        st.success("Audio capturado. Procesando...")
        
        import io
        import librosa
        import numpy as np
        from pydub import AudioSegment

        # 1. Convertir bytes a AudioSegment de pydub
        audio_segment = AudioSegment.from_file(io.BytesIO(audio['bytes']))
        
        # 2. Exportar a un formato que Librosa ame (RAW wav)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        # 3. Ahora sí, cargar con librosa
        y, sr = librosa.load(wav_io, sr=None)
        
        # 4. Calcular el Pitch
        f0, _, _ = librosa.pyin(y, fmin=50, fmax=1000)
        pitch = np.nanmedian(f0)
        
        if not np.isnan(pitch):
            nota = librosa.hz_to_note(pitch)
            st.metric("Nota detectada", nota)
            st.write(f"Frecuencia: {pitch:.2f} Hz")
        else:
            st.warning("No se detectó un tono claro. ¡Canta más cerca!")streamlit

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
