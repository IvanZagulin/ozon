from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from threading import Thread
from main import run_transfer, LOG_STORE
import os

UPLOAD_FOLDER = "uploads"
LOG_DIR = "logs_data"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Главная — редирект на страницу загрузки
@app.route("/")
def home():
    return redirect(url_for("upload_page"))

# Загрузка карточек
@app.route("/upload", methods=["GET", "POST"])
def upload_page():
    log = ""
    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            log = "❗ Файл не выбран."
        else:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            Thread(target=run_transfer, args=(filepath,)).start()
            log = "🚀 Импорт запущен. Логи появятся ниже."
    return render_template("upload.html", log=log, logs=LOG_STORE)

# Поток обновления логов (для JS)
@app.route("/logs_stream")
def logs_stream():
    return "\n".join(LOG_STORE), 200, {"Cache-Control": "no-cache"}

# История логов (список логов)
@app.route("/logs")
def logs_page():
    history_files = sorted(os.listdir(LOG_DIR), reverse=True)
    return render_template("logs.html", files=history_files)

# Детальный просмотр отдельного лога
@app.route("/logs/<filename>")
def log_detail(filename):
    path = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(path):
        return "Файл не найден", 404
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return render_template("log_detail.html", content=content, filename=filename)

# Настройки (пока заглушка)
@app.route("/settings")
def settings_page():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
