
from flask import Flask, render_template_string, request, send_from_directory
import subprocess
import os

app = Flask(__name__)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Catalog Webapp</title>
</head>
<body>
    <h2>Run Gemini Catalog Script</h2>
    <form method="post">
        Image Directory: <input type="text" name="image_dir" value="Pictures/Test"><br>
        <input type="submit" value="Run">
    </form>
    <h3>Output:</h3>
    <pre style="max-width:600px; white-space:pre-wrap; word-break:break-word; overflow-x:auto;">{{ output }}</pre>
    {% if images %}
    <h3>Processed Images:</h3>
    {% for img in images %}
        <img src="/images/{{ img }}" style="max-width:300px; margin:5px;">
    {% endfor %}
    {% endif %}
</body>
</html>
"""


# Route to serve images from any directory
@app.route('/images/<path:filename>')
def images(filename):
    # Find the directory from the filename
    # Only allow serving from Pictures/ and subfolders for security
    base_dir = os.path.abspath("Pictures")
    abs_path = os.path.abspath(os.path.join(base_dir, filename))
    if not abs_path.startswith(base_dir):
        return "Forbidden", 403
    dir_name = os.path.dirname(abs_path)
    file_name = os.path.basename(abs_path)
    return send_from_directory(dir_name, file_name)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    images = []
    if request.method == "POST":
        image_dir = request.form.get("image_dir", "Pictures/Test")
        # Run the geminiScript.py and capture output
        try:
            result = subprocess.run(
                ["python3", "extendedPipelineGemini.py", "--image-dir", image_dir],
                capture_output=True, text=True, timeout=120
            )
            output = result.stdout + "\n" + result.stderr
            # Extrahiere die verarbeiteten Bildnamen aus dem Output
            # Annahme: Die Bildnamen stehen im Output als 'files': [ ... ]
            import re, ast
            match = re.search(r'"files":\s*\[(.*?)\]', output, re.DOTALL)
            if match:
                files_str = match.group(1)
                # Split und säubere die Dateinamen
                files = [f.strip().strip('"') for f in files_str.split(',') if f.strip()]
                # Erzeuge relative Pfade für die Bilder
                images = [os.path.join(image_dir, f) for f in files]
        except Exception as e:
            output = str(e)
    return render_template_string(HTML, output=output, images=images)

if __name__ == "__main__":
    app.run(debug=True)