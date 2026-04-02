import streamlit as st
import os
import json
from datetime import datetime
from api_utils import separar_audio_con_api

-----------------------------
CONFIGURACIÓN INICIAL
-----------------------------
st.set_page_config(page_title="Karaoke App", layout="wide")

Crear carpetas si no existen
os.makedirs("data", exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/separated", exist_ok=True)
os.makedirs("data/recordings", exist_ok=True)

LIBRARY_FILE = "data/library.json"

Si no existe library.json, crearlo vacío
if not os.path.exists(LIBRARY_FILE):
with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
json.dump([], f, ensure_ascii=False, indent=4)

-----------------------------
FUNCIONES AUXILIARES
-----------------------------
def load_library():
with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
return json.load(f)

def save_library(data):
with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
json.dump(data, f, ensure_ascii=False, indent=4)

def add_song_to_library(title, artist, original_path, vocals_path, instrumental_path, lyrics=""):
library = load_library()

text
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

-----------------------------
SESSION STATE
-----------------------------
if "num_mics" not in st.session_state:
st.session_state.num_mics = 1

if "difficulty" not in st.session_state:
st.session_state.difficulty = "Medio"

if "lyric_color" not in st.session_state:
st.session_state.lyric_color = "#FFFFFF"

-----------------------------
INTERFAZ PRINCIPAL
-----------------------------
st.title("🎤 Karaoke App")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
"Afinador",
"Separador",
"Preparación",
"Estudio",
"Configuraciones"
])

-----------------------------
PESTAÑA 1: AFINADOR
-----------------------------
with tab1:
st.header("Afinador")
st.write("Más adelante aquí pondremos el detector de afinación.")

-----------------------------
PESTAÑA 2: SEPARADOR
-----------------------------
if st.button("Procesar con API"):
    with st.spinner("Separando pistas, esto puede tardar un poco..."):
        resultado = separar_audio_con_api(original_path, st.secrets["API_KEY"])
        if resultado:
            st.success("¡Éxito! Pistas disponibles.")
            # Aquí guardarías las rutas de respuesta en tu biblioteca
text
st.write("Sube una canción para guardarla y dejarla preparada para separación.")

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

        # MVP: todavía no separa realmente, solo deja rutas preparadas
        library = load_library()
        next_id = f"song_{len(library) + 1:03d}"
        song_folder = os.path.join("data/separated", next_id)
        os.makedirs(song_folder, exist_ok=True)

        vocals_path = os.path.join(song_folder, "vocals.wav")
        instrumental_path = os.path.join(song_folder, "instrumental.wav")

        # Crear archivos vacíos simbólicos por ahora
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
        st.info("Por ahora la separación es simbólica. Más adelante haremos la separación real.")
        st.write("Archivo original:", original_path)
        st.write("Ruta voz:", vocals_path)
        st.write("Ruta instrumental:", instrumental_path)
-----------------------------
PESTAÑA 3: PREPARACIÓN
-----------------------------
with tab3:
st.header("Preparación")

text
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
        st.write("Fecha:", selected_song["created_at"])

        if selected_song["lyrics"]:
            st.markdown(
                f"<p style='color:{st.session_state.lyric_color}; font-size:22px;'>{selected_song['lyrics']}</p>",
                unsafe_allow_html=True
            )

        st.write("### Archivos asociados")
        st.write("Original:", selected_song["original_path"])
        st.write("Voz:", selected_song["vocals_path"])
        st.write("Instrumental:", selected_song["instrumental_path"])

        st.info("Más adelante aquí añadiremos grabación de prueba, pentagrama, análisis y cambio de tono.")
-----------------------------
PESTAÑA 4: ESTUDIO
-----------------------------
with tab4:
st.header("Estudio")

text
st.write("Aquí después podrás grabar tu voz final usando una pista de la biblioteca.")

song_options = get_song_options()

if len(song_options) == 0:
    st.warning("No hay pistas guardadas todavía.")
else:
    selected_song_option = st.selectbox("Selecciona una pista para grabar", song_options, key="studio_select")
    selected_song = get_song_by_option(selected_song_option)

    if selected_song:
        st.write("Pista seleccionada:", selected_song["title"], "-", selected_song["artist"])
        st.write("Instrumental:", selected_song["instrumental_path"])
        st.info("Más adelante agregaremos grabación real y guardado de voz.")
-----------------------------
PESTAÑA 5: CONFIGURACIONES
-----------------------------
with tab5:
st.header("Configuraciones")

text
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

st.write("## Biblioteca de pistas guardadas")

library = load_library()

if len(library) == 0:
    st.write("No hay canciones guardadas todavía.")
else:
    for song in library:
        with st.expander(f"{song['id']} - {song['title']} / {song['artist']}"):
            st.write("Título:", song["title"])
            st.write("Artista:", song["artist"])
            st.write("Fecha:", song["created_at"])
            st.write("Original:", song["original_path"])
            st.write("Voz:", song["vocals_path"])
            st.write("Instrumental:", song["instrumental_path"])
            if song["lyrics"]:
                st.write("Letra:", song["lyrics"])
