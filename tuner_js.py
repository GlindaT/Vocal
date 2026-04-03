import streamlit.components.v1 as components

def render_tuner_js():
    components.html("""
    <canvas id="visualizer" width="600" height="200" style="background:#000;"></canvas>
    <script>
        const canvas = document.getElementById('visualizer');
        const ctx = canvas.getContext('2d');
        let data = [];
        
        async function start() {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const audioCtx = new AudioContext();
            const analyser = audioCtx.createAnalyser();
            audioCtx.createMediaStreamSource(stream).connect(analyser);
            
            function draw() {
                const buffer = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(buffer);
                
                // Calculamos el centro de masa del sonido (Pitch aproximado)
                let sum = 0, weight = 0;
                for(let i=0; i<buffer.length; i++) {
                    sum += i * buffer[i];
                    weight += buffer[i];
                }
                const pitch = weight > 0 ? sum / weight : 0;
                
                // Dibujamos la gráfica
                data.push(pitch);
                if(data.length > 100) data.shift();
                
                ctx.clearRect(0,0,600,200);
                ctx.strokeStyle = '#00FF00';
                ctx.beginPath();
                data.forEach((val, i) => ctx.lineTo(i*6, 200 - val*2));
                ctx.stroke();
                requestAnimationFrame(draw);
            }
            draw();
        }
        start();
    </script>
    """, height=220)
    st.button("Iniciar") # Solo para activar el contexto de audio
    """)
