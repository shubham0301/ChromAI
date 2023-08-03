from flask import Flask, request, render_template, flash, send_file
from werkzeug.utils import secure_filename
import os
import cv2  # opencv python library

# upload file settings
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"webp", "png", "jpg", "jpeg", "gif"}

# base dir
basedir = os.path.abspath(os.path.dirname(__file__))

# init flask app
app = Flask(__name__)
app.secret_key = "super secret key"

# apps upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# limiting allowed files
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# processing image
def processImage(filename, operation):
    img = cv2.imread(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    if operation == "cgray":
        imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        imgProcessed = img
    processed_filename = f"{filename.split('.')[0]}_processed.{filename.split('.')[-1]}"
    cv2.imwrite(os.path.join(app.static_folder, processed_filename), imgProcessed)
    return processed_filename


# first web page
@app.route("/")
def home():
    return render_template("index.html", processed_image=None)


# image editing
@app.route("/edit", methods=["POST"])
def edit():
    operation = request.form.get("operation")
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file Submission")
            return render_template("index.html", processed_image=None)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return render_template("index.html", processed_image=None)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            # Image processing
            processed_filename = processImage(filename, operation)

            # flashing success message with the link to the processed image
            flash(
                f"Your image has been processed and is available <a href='/static/{processed_filename}' target ='_blank'> here</a> "
            )
            return render_template("index.html", processed_image=processed_filename)

    return render_template("index.html", processed_image=None)


# download processed image
@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(app.static_folder, filename), as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
