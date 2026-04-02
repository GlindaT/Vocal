# api_utils.py
from google.cloud import storage

def subir_a_gcs(archivo_local, nombre_destino):
    """Sube el audio a un bucket de Google Cloud para ser procesado."""
    storage_client = storage.Client()
    bucket = storage_client.bucket("nombre-de-tu-bucket") # Nombre de tu bucket
    blob = bucket.blob(nombre_destino)
    blob.upload_from_filename(archivo_local)
    return f"gs://nombre-de-tu-bucket/{nombre_destino}"
