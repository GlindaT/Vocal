# tuner_ui.py
from streamlit_echarts import st_echarts

def render_tuner_gauge(frecuencia_actual):
    # La lógica aquí es simple: 
    # 0 es "muy grave", 50 es "afinado", 100 es "muy agudo"
    options = {
        "tooltip": {"formatter": "{a} <br/>{b} : {c}"},
        "series": [
            {
                "name": "Afinación",
                "type": "gauge",
                "detail": {"formatter": "{value} Hz"},
                "data": [{"value": frecuencia_actual, "name": "Frecuencia"}],
                "min": 40,  # Frecuencia mínima
                "max": 1000 # Frecuencia máxima
            }
        ],
    }
    st_echarts(options=options, height="400px")
