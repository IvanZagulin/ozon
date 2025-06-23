from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from main import load_vendor_codes, wb_get_all, dump_filtered

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

            vcodes = load_vendor_codes(filepath)
            wb_all = wb_get_all()
            wb_need = dump_filtered(wb_all, vcodes)
            log = f"Найдено {len(wb_need)} карточек"
        return render_template("index.html", log=log)
    return render_template("index.html", log=log)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
