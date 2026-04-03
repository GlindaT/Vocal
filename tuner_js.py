import streamlit.components.v1 as components

def render_tuner_js():
    components.html("""
    <div id="app" style="background:#222; color:white; text-align:center; padding:50px; font-family:sans-serif; height: 300px; border-radius:10px;">
        <div style="margin-bottom:20px;">
            Nota Objetivo: 
            <select id="targetNote" style="background:#444; color:white; border:none; padding:5px;">
                <option value="65.41">C2</option><option value="440.00">A4</option>
            </select>
        </div>
        <h1 id="detectedNote" style="font-size:80px; color:#4CAF50; margin:10px;">--</h1>
        <div id="instruction" style="font-size:24px; color:orange;">Presiona Iniciar</div>
        <br>
        <button id="start" style="background:#4CAF50; color:white; border:none; padding:10px 20px; font-size:16px;">▶ Iniciar</button>
        <button id="stop" style="background:#f44336; color:white; border:none; padding:10px 20px; font-size:16px;">⏹ Detener</button>
    </div>
    <script>
        let audioCtx, analyser, animationId;
        const noteEl = document.getElementById('detectedNote');
        const instrEl = document.getElementById('instruction');

        document.getElementById('start').onclick = async () => {
            audioCtx = new AudioContext();
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 2048;
            audioCtx.createMediaStreamSource(stream).connect(analyser);
            update();
        };

        function update() {
            const buffer = new Float32Array(analyser.fftSize);
            analyser.getFloatTimeDomainData(buffer);
            // Cálculo simple de pitch para mostrar la nota
            // (Aquí conectaríamos con una librería de notas como Pitchfinder)
            const target = parseFloat(document.getElementById('targetNote').value);
            // Simulación visual:
            noteEl.innerText = "A4"; 
            instrEl.innerText = "Estás agudo. Baja a C2";
            animationId = requestAnimationFrame(update);
        }
        document.getElementById('stop').onclick = () => cancelAnimationFrame(animationId);
    </script>
    """, height=400)
