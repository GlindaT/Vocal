import streamlit.components.v1 as components

def render_tuner_js():
    # Incluimos un selector de nota y el botón de stop dentro del HTML
    components.html("""
    <div style="font-family:sans-serif; text-align:center;">
        <select id="noteSelect">
            <option value="261.6">C4</option>
            <option value="440.0" selected>A4</option>
        </select>
        <button id="startBtn">Iniciar</button>
        <button id="stopBtn" disabled>Detener</button>
        <h2 id="note">---</h2>
        <div style="width:100%; background:#eee;"><div id="bar" style="width:0%; height:20px; background:green;"></div></div>
    </div>
    <script>
        let animationId;
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        startBtn.onclick = async () => {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const ctx = new AudioContext();
            const analyser = ctx.createAnalyser();
            source = ctx.createMediaStreamSource(stream);
            source.connect(analyser);
            
            startBtn.disabled = true;
            stopBtn.disabled = false;
            
            function update() {
                // ... lógica de detección ...
                animationId = requestAnimationFrame(update);
            }
            update();
        };

        stopBtn.onclick = () => {
            cancelAnimationFrame(animationId);
            startBtn.disabled = false;
            stopBtn.disabled = true;
            document.getElementById('bar').style.width = "0%";
        };
    </script>
    """, height=250)
