# tuner_js.py
import streamlit.components.v1 as components

def render_tuner_js():
    html_code = """
    <div style="text-align:center; padding:20px; font-family:sans-serif;">
        <button id="btn" style="padding:10px 20px; font-size:16px;">Iniciar Afinador</button>
        <h2 id="note">Nota: ---</h2>
        <div id="meter" style="width:100%; height:30px; background:#ddd; border-radius:5px;">
            <div id="bar" style="width:50%; height:100%; background:green; transition:0.1s;"></div>
        </div>
    </div>
    <script>
        document.getElementById('btn').onclick = async () => {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const audioCtx = new AudioContext();
            const analyser = audioCtx.createAnalyser();
            const source = audioCtx.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 2048;
            const buffer = new Float32Array(analyser.fftSize);

            function update() {
                analyser.getFloatTimeDomainData(buffer);
                // Lógica simple de detección de pico (autocorrelación simple)
                let max = 0;
                for(let i=0; i<buffer.length; i++) {
                    if(Math.abs(buffer[i]) > max) max = Math.abs(buffer[i]);
                }
                const bar = document.getElementById('bar');
                bar.style.width = (max * 100) + "%";
                requestAnimationFrame(update);
            }
            update();
        };
    </script>
    """
    components.html(html_code, height=200)
