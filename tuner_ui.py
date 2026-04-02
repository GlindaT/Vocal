# tuner_ui.py
try:
    from streamlit_echarts import st_echarts
    ECHARTS_AVAILABLE = True
except ImportError:
    ECHARTS_AVAILABLE = False
    import streamlit as st

def render_tuner_gauge(frecuencia_actual):
    if not ECHARTS_AVAILABLE:
        st.error("Falta instalar: pip install streamlit-echarts")
        st.metric("Frecuencia", f"{frecuencia_actual} Hz")
        return
        
    options = {
        "tooltip": {"formatter": "{a} <br/>{b} : {c}"},
        "series": [
            {
                "name": "Afinación",
                "type": "gauge",
                "detail": {"formatter": "{value} Hz", "fontSize": 20},
                "data": [{"value": frecuencia_actual, "name": "Frecuencia"}],
                "min": 80,
                "max": 1000,
                "splitNumber": 10,
                "axisLine": {
                    "lineStyle": {
                        "color": [[0.3, "#ff4500"], [0.7, "#00ff00"], [1, "#ff4500"]],
                        "width": 10
                    }
                },
            }
        ],
    }
    st_echarts(options=options, height="400px")
