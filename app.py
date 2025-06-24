from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from main import load_vendor_codes, wb_get_all_parts as wb_get_all, dump_filtered
from flask import Flask, request, render_template, redirect, url_for, jsonify
from main import run_transfer, log_message, LOG_STORE
from threading import Thread

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            from threading import Thread
            Thread(target=run_transfer, args=(filepath,)).start()

            log = f"🚀 Импорт запущен. Логи появятся ниже."

    return render_template("index.html", log=log, logs=LOG_STORE)

@app.route("/logs")
def logs():
    return "\n".join(LOG_STORE)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
