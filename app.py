from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from threading import Thread
from main import run_transfer, log_message, LOG_STORE
import os

UPLOAD_FOLDER = "uploads"
LOG_DIR = "logs_data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    log = ""
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            log = "❗ Файл не выбран."
        else:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Асинхронный запуск импорта
            Thread(target=run_transfer, args=(filepath,)).start()

            log = f"🚀 Импорт запущен. Логи появятся ниже."

    return render_template("index.html", log=log, logs=LOG_STORE)

@app.route("/logs")
def logs():
    return "\n".join(LOG_STORE), 200, {"Cache-Control": "no-cache"}

@app.route("/history")
def history():
    entries = []
    for fname in sorted(os.listdir(LOG_DIR), reverse=True):
        if fname.startswith("history_") and fname.endswith(".txt"):
            entries.append(fname)
    return render_template("history.html", files=entries)

@app.route("/history/<filename>")
def view_history(filename):
    full_path = os.path.join(LOG_DIR, filename)
    if os.path.exists(full_path):
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        return f"<pre style='white-space: pre-wrap; font-family: monospace'>{content}</pre>"
    return "Файл не найден", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
