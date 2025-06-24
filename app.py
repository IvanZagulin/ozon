from flask import Flask, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from threading import Thread
from main import run_transfer, log_message, LOG_STORE
import os
from flask import send_file
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


@app.route("/history")
def history_list():
    files = sorted(glob.glob("logs_data/history_*.txt"), reverse=True)
    links = [f"<li><a href='/history/view?file={os.path.basename(f)}'>{os.path.basename(f)}</a></li>" for f in files]
    return f"<h2>История логов:</h2><ul>{''.join(links)}</ul>"

@app.route("/history/view")
def view_log():
    file = request.args.get("file")
    if not file or not os.path.exists(os.path.join("logs_data", file)):
        return "Файл не найден", 404
    return send_file(os.path.join("logs_data", file), mimetype="text/plain")

@app.route("/")
def home():
    return redirect(url_for("upload_page"))

@app.route("/upload", methods=["GET", "POST"])
def upload_page():
    # логика загрузки файла и run_transfer
    return render_template("upload.html", logs=LOG_STORE)

@app.route("/logs")
def logs_page():
    # просмотр history_*.txt
    history_files = sorted(os.listdir(LOG_DIR), reverse=True)
    return render_template("logs.html", files=history_files)

@app.route("/logs/<filename>")
def log_detail(filename):
    path = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(path):
        return "Файл не найден", 404
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return render_template("log_detail.html", content=content, filename=filename)

@app.route("/settings")
def settings_page():
    return render_template("settings.html")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
