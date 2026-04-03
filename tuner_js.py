import streamlit.components.v1 as components

def render_tuner_js():
    html_code = """
    <div style="text-align:center; font-family: Arial, sans-serif; background: #1e1e1e; color: white; padding: 20px; border-radius: 15px;">
        <div style="margin-bottom: 20px;">
            <label>Nota Objetivo: </label>
            <select id="noteSelect" style="padding: 5px; border-radius: 5px;">
                <option value="261.63">C4 (Do)</option>
                <option value="277.18">C#4 (Do#)</option>
                <option value="293.66">D4 (Re)</option>
                <option value="311.13">D#4 (Re#)</option>
                <option value="329.63">E4 (Mi)</option>
                <option value="349.23">F4 (Fa)</option>
                <option value="369.99">F#4 (Fa#)</option>
                <option value="392.00">G4 (Sol)</option>
                <option value="415.30">G#4 (Sol#)</option>
                <option value="440.00" selected>A4 (La)</option>
                <option value="466.16">A#4 (La#)</option>
                <option value="493.88">B4 (Si)</option>
            </select>
        </div>

        <div style="position: relative; width: 300px; height: 150px; margin: 0 auto; border: 2px solid #555; border-radius: 150px 150px 0 0; overflow: hidden; background: #222;">
            <div id="needle" style="position: absolute; bottom: 0; left: 50%; width: 4px; height: 130px; background: #ff4b4b; transform-origin: bottom center; transform: rotate(0deg); transition: transform 0.1s ease-out; margin-left: -2px; z-index: 2;"></div>
        </div>
        <h2 id="freqDisplay" style="margin-top: 10px; color: #00ff00;">--- Hz</h2>
        <button id="startBtn" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px;">Iniciar</button>
        <button id="stopBtn" style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 5px;" disabled>Parar</button>
    </div>

    <script>
        let audioCtx, analyser, animationId;
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const needle = document.getElementById('needle');
        const freqDisplay = document.getElementById('freqDisplay');
        const noteSelect = document.getElementById('noteSelect');

        startBtn.onclick = async () => {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 2048;
            source = audioCtx.createMediaStreamSource(stream);
            source.connect(analyser);
            startBtn.disabled = true;
            stopBtn.disabled = false;
            update();
        };

        stopBtn.onclick = () => {
            cancelAnimationFrame(animationId);
            if(audioCtx) audioCtx.close();
            startBtn.disabled = false;
            stopBtn.disabled = true;
        };

        function update() {
            const buffer = new Float32Array(analyser.fftSize);
            analyser.getFloatTimeDomainData(buffer);
            let rms = 0;
            for(let i=0; i<buffer.length; i++) rms += buffer[i]*buffer[i];
            rms = Math.sqrt(rms/buffer.length);
            
            if(rms > 0.01) {
                // Autocorrelación simple para pitch
                let best_offset = 0;
                let max_corr = 0;
                for(let offset=10; offset<200; offset++) {
                    let corr = 0;
                    for(let i=0; i<100; i++) corr += buffer[i] * buffer[i+offset];
                    if(corr > max_corr) { max_corr = corr; best_offset = offset; }
                }
                const freq = audioCtx.sampleRate / best_offset;
                freqDisplay.innerText = Math.round(freq) + " Hz";
                const cents = 1200 * Math.log2(freq / parseFloat(noteSelect.value));
                needle.style.transform = `rotate(${Math.max(Math.min(cents, 50), -50)}deg)`;
            }
            animationId = requestAnimationFrame(update);
        }
    </script>
    """
    components.html(html_code, height=450)
