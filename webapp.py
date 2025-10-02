

from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for
import subprocess
import os
import tempfile
import shutil

app = Flask(__name__)




HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Catalog Webapp</title>
    <style>
        .spinner {
            display: inline-block;
            width: 28px;
            height: 28px;
            position: relative;
            vertical-align: middle;
        }
        .spinner-dot {
            width: 6px;
            height: 6px;
            background: #3498db;
            border-radius: 50%;
            position: absolute;
            animation: spinner-dot 1.2s linear infinite;
        }
        @keyframes spinner-dot {
            0% { transform: scale(1); }
            50% { transform: scale(1.5); }
            100% { transform: scale(1); }
        }
        .spinner-dot:nth-child(1) { top: 2px; left: 11px; animation-delay: 0s; }
        .spinner-dot:nth-child(2) { top: 7px; left: 20px; animation-delay: 0.15s; }
        .spinner-dot:nth-child(3) { top: 15px; left: 20px; animation-delay: 0.3s; }
        .spinner-dot:nth-child(4) { top: 20px; left: 11px; animation-delay: 0.45s; }
        .spinner-dot:nth-child(5) { top: 15px; left: 2px; animation-delay: 0.6s; }
        .spinner-dot:nth-child(6) { top: 7px; left: 2px; animation-delay: 0.75s; }
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 0; padding: 0; }
        .container { max-width: 800px; margin: 30px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #ccc; padding: 30px; }
        h2 { color: #2c3e50; }
        .step { background: #eaf6ff; border-left: 5px solid #3498db; margin: 10px 0; padding: 10px 15px; border-radius: 4px; font-weight: bold; }
        .images-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
        .images-row img { border-radius: 4px; box-shadow: 0 1px 4px #aaa; }
        .description-box { border: 2px solid #3498db; background: #f0f8ff; border-radius: 8px; padding: 18px; margin-top: 25px; font-size: 1.1em; }
        .loader { color: #3498db; font-weight: bold; }
        .run-btn { background: #3498db; color: #fff; border: none; padding: 10px 18px; border-radius: 4px; font-size: 1em; cursor: pointer; margin-top: 10px; }
        .run-btn:hover { background: #217dbb; }
        .upload-btn { background: #2ecc71; color: #fff; border: none; padding: 8px 16px; border-radius: 4px; font-size: 1em; cursor: pointer; }
        .upload-btn:hover { background: #27ae60; }
    </style>
    <script>
    function runGeminiLive(uploadDir) {
        var outputDiv = document.getElementById('liveoutput');
        var spinner = document.getElementById('spinner');
        outputDiv.innerHTML = '<span class="loader" id="loader">Loading...</span>';
        spinner.style.display = 'inline-block';
        var evtSource = new EventSource('/stream?upload_dir=' + encodeURIComponent(uploadDir));
        let itemLine = "";
        let descriptionText = "";
        let queue = [];
        let processing = false;

        function processQueue() {
            if (queue.length === 0) {
                processing = false;
                return;
            }
            processing = true;
            let data = queue.shift();
            document.getElementById('loader').style.display = 'none';
            if (data.match(/^\[\d\]/)) {
                outputDiv.innerHTML += '<div class="step">' + data + '</div>';
            } else if (data.startsWith('<item>')) {
                itemLine = data.replace('<item>', '').replace('</item>', '');
            } else if (itemLine && descriptionText === "") {
                // Erste Beschreibung nach Item-Zeile
                descriptionText = data;
                outputDiv.innerHTML += '<div class="description-box"><div style="font-weight:bold; font-size:1.2em; margin-bottom:8px;">' + itemLine + '</div>' + descriptionText + '</div>';
            } else if (descriptionText !== "") {
                // Weitere Beschreibungstexte (falls mehrzeilig)
                descriptionText += '<br>' + data;
                // Ersetze die Box mit aktualisiertem Text
                let boxHtml = '<div class="description-box"><div style="font-weight:bold; font-size:1.2em; margin-bottom:8px;">' + itemLine + '</div>' + descriptionText + '</div>';
                // Entferne vorherige Box und füge neue hinzu
                outputDiv.innerHTML = outputDiv.innerHTML.replace(/<div class="description-box">[\s\S]*?<\/div>/, boxHtml);
            } else {
                outputDiv.innerHTML += data + '<br>';
            }
            setTimeout(processQueue, 500);
        }

        evtSource.onmessage = function(e) {
            queue.push(e.data);
            if (!processing) {
                processQueue();
            }
        };
        evtSource.onerror = function() {
            evtSource.close();
            spinner.style.display = 'none';
        };
        evtSource.addEventListener('end', function() {
            spinner.style.display = 'none';
        });
    }
    </script>
</head>
<body>
<div class="container">
    <h2>Gemini Catalog Webapp</h2>
    <form method="post" enctype="multipart/form-data" action="/upload" style="display: flex; flex-direction: column; align-items: flex-start; gap: 8px;">
        <input type="file" name="images" multiple>
        <input type="submit" value="Upload Images" class="upload-btn" style="margin-top:8px;">
    </form>
    {% if uploaded_images %}
    <h3>Uploaded Images:</h3>
    <div class="images-row">
    {% for img in uploaded_images %}
        <img src="/uploaded/{{ img }}" style="max-width:120px; margin:5px;">
    {% endfor %}
    </div>
    <form onsubmit="event.preventDefault(); runGeminiLive('{{ upload_dir }}');" style="display: flex; align-items: center; gap: 12px;">
        <input type="hidden" name="upload_dir" value="{{ upload_dir }}">
        <input type="submit" value="Identify items" class="run-btn">
        <span id="spinner" class="spinner" style="display:none;">
            <span class="spinner-dot"></span>
            <span class="spinner-dot"></span>
            <span class="spinner-dot"></span>
            <span class="spinner-dot"></span>
            <span class="spinner-dot"></span>
            <span class="spinner-dot"></span>
        </span>
    </form>
    <div id="liveoutput" style="max-width:600px; white-space:pre-wrap; word-break:break-word; overflow-x:auto; margin-top:20px;"></div>
    {% endif %}
    {% if output %}
    <h3>Output:</h3>
    <pre style="max-width:600px; white-space:pre-wrap; word-break:break-word; overflow-x:auto;">{{ output }}</pre>
    {% endif %}
    {% if images %}
    <h3>Processed Images:</h3>
    <div class="images-row">
    {% for img in images %}
        <img src="/uploaded/{{ img }}" style="max-width:300px; margin:5px;">
    {% endfor %}
    </div>
    {% endif %}
</div>
</body>
</html>
"""



# Route to serve uploaded images
@app.route('/uploaded/<path:filename>')
def uploaded_images(filename):
    upload_base = os.path.abspath("uploads")
    abs_path = os.path.abspath(os.path.join(upload_base, filename))
    if not abs_path.startswith(upload_base):
        return "Forbidden", 403
    dir_name = os.path.dirname(abs_path)
    file_name = os.path.basename(abs_path)
    return send_from_directory(dir_name, file_name)


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, output=None, images=None, uploaded_images=None, upload_dir=None)

# Upload-Route: Bilder aus Ordner empfangen und speichern
@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("images")
    if not files:
        return redirect(url_for('index'))
    # Temporäres Upload-Verzeichnis anlegen
    upload_dir = os.path.join("uploads", next(tempfile._get_candidate_names()))
    os.makedirs(upload_dir, exist_ok=True)
    uploaded_images = []
    for file in files:
        filename = file.filename.split("/")[-1]  # Nur Dateiname, kein Pfad
        save_path = os.path.join(upload_dir, filename)
        file.save(save_path)
        uploaded_images.append(os.path.join(os.path.basename(upload_dir), filename))
    return render_template_string(HTML, uploaded_images=uploaded_images, upload_dir=upload_dir, output=None, images=None)


# Run-Route: Skript ausführen mit Upload-Verzeichnis

# Live-Stream-Route: Skript ausführen und Output live senden
from flask import Response
@app.route("/stream")
def stream():
    upload_dir = request.args.get("upload_dir")
    if not upload_dir:
        return "Missing upload_dir", 400
    abs_upload_dir = os.path.abspath(upload_dir)
    def generate():
        process = subprocess.Popen(
            ["python3", "extendedPipelineGemini.py", "--image-dir", abs_upload_dir],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in iter(process.stdout.readline, ''):
            yield f"data: {line.rstrip()}\n\n"
        process.stdout.close()
        process.wait()
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)