# tuner_js.py
import streamlit.components.v1 as components

def render_tuner_js():
    html_code = """
    <div style="text-align:center; padding:20px; font-family:sans-serif;">
        <button id="btn" style="padding:15px 30px; font-size:20px; background-color:#ff4b4b; color:white; border:none; border-radius:5px; cursor:pointer;">
            Iniciar Afinador
        </button>
        <h2 id="note" style="margin-top:20px;">Pulsa para empezar</h2>
        <div style="width:100%; height:30px; background:#ddd; border-radius:5px; margin-top:10px;">
            <div id="bar" style="width:0%; height:100%; background:linear-gradient(to right, red, green, red); transition:0.1s;"></div>
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
            const buffer = new Uint8Array(analyser.frequencyBinCount);

            function detect() {
                analyser.getByteFrequencyData(buffer);
                let max = 0;
                let index = 0;
                for(let i=0; i<buffer.length; i++) {
                    if(buffer[i] > max) { max = buffer[i]; index = i; }
                }
                const freq = index * (audioCtx.sampleRate / analyser.fftSize);
                document.getElementById('note').innerText = "Frecuencia: " + Math.round(freq) + " Hz";
                document.getElementById('bar').style.width = Math.min(max/2, 100) + "%";
                requestAnimationFrame(detect);
            }
            detect();
        };
    </script>
    """
    components.html(html_code, height=250)
