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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
