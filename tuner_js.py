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

        <!-- El "Reloj" del Afinador -->
        <div style="position: relative; width: 300px; height: 150px; margin: 0 auto; border: 2px solid #555; border-radius: 150px 150px 0 0; overflow: hidden; background: #222;">
            <div id="needle" style="position: absolute; bottom: 0; left: 50%; width: 4px; height: 130px; background: #ff4b4b; transform-origin: bottom center; transform: rotate(0deg); transition: transform 0.1s ease-out; margin-left: -2px; z-index: 2;"></div>
            <div style="position: absolute; bottom: 0; left: 50%; width: 10px; height: 10px; background: white; border-radius: 50%; margin-left: -5px; z-index: 3;"></div>
            <div style="position: absolute; top: 10px; left: 10%; color: #888;">-50</div>
            <div style="position: absolute; top: 10px; right: 10%; color: #888;">+50</div>
            <div style="position: absolute; top: 5px; left: 50%; color: #00ff00; transform: translateX(-50%);">OK</div>
        </div>

        <h2 id="freqDisplay" style="margin-top: 10px; color: #00ff00;">--- Hz</h2>
        <p id="status">Presiona Iniciar para afinar</p>

        <button id="startBtn" style="padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; margin-right: 10px;">Iniciar</button>
        <button id="stopBtn" style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;" disabled>Parar</button>
    </div>

    <script>
        let audioCtx;
        let analyser;
        let source;
        let animationId;

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
            needle.style.transform = 'rotate(0deg)';
            freqDisplay.innerText = "--- Hz";
        };

        function autoCorrelate(buffer, sampleRate) {
            let n = buffer.length;
            let best_offset = -1;
            let best_correlation = 0;
            let rms = 0;

            for (let i=0; i<n; i++) { rms += buffer[i]*buffer[i]; }
            rms = Math.sqrt(rms/n);
            if (rms < 0.01) return -1; // Silencio

            for (let offset = 0; offset < n; offset++) {
                let correlation = 0;
                for (let i=0; i<n-offset; i++) {
                    correlation += buffer[i] * buffer[i+offset];
                }
                if (correlation > best_correlation) {
                    best_correlation = correlation;
                    best_offset = offset;
                }
                if (correlation > 0.9 && correlation > best_correlation) break;
            }
            if (best_correlation > 0.01) return sampleRate / best_offset;
            return -1;
        }

        function update() {
            const buffer = new Float32Array(analyser.fftSize);
            analyser.getFloatTimeDomainData(buffer);
            const freq = autoCorrelate(buffer, audioCtx.sampleRate);

            if (freq !== -1 && freq < 1000) {
                freqDisplay.innerText = Math.round(freq) + " Hz";
                const targetFreq = parseFloat(noteSelect.value);
                
                // Cálculo de Cents (desviación)
                const cents = 1200 * Math.log2(freq / targetFreq);
                
                // Mover la aguja (limitado a +/- 45 grados)
                let angle = Math.max(Math.min(cents, 50), -50);
                needle.style.transform = `rotate(${angle}deg)`;
                
                if (Math.abs(cents) < 5) freqDisplay.style.color = "#00ff00"; // Afinado
                else freqDisplay.style.color = "#ff4b4b"; // Desafinado
            }
            animationId = requestAnimationFrame(update);
        }
    </script>
    """
    components.html(html_code, height=450)
