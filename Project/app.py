import os
import cv2
import numpy as np
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Function to check if a file has an allowed extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]

    if file.filename == "":
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filename)

        # Load the uploaded image
        input_image = cv2.imread(filename)

        # Define image dimensions
        height, width, channels = input_image.shape

        # Scaling Transformation
        scaling_factor = 0.5
        scaled_image = cv2.resize(
            input_image, None, fx=scaling_factor, fy=scaling_factor
        )

        # Rotation Transformation
        angle = 45
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
        rotated_image = cv2.warpAffine(input_image, rotation_matrix, (width, height))

        # Translation Transformation
        tx, ty = 50, 30
        translation_matrix = np.float32([[1, 0, tx], [0, 1, ty]])
        translated_image = cv2.warpAffine(
            input_image, translation_matrix, (width, height)
        )

        # Shearing Transformation
        shear_factor = 0.2
        shear_matrix = np.float32([[1, shear_factor, 0], [0, 1, 0]])
        sheared_image = cv2.warpAffine(input_image, shear_matrix, (width, height))

        # Save the transformed images
        scaled_filename = os.path.join(
            app.config["UPLOAD_FOLDER"], "scaled_" + file.filename
        )
        rotated_filename = os.path.join(
            app.config["UPLOAD_FOLDER"], "rotated_" + file.filename
        )
        translated_filename = os.path.join(
            app.config["UPLOAD_FOLDER"], "translated_" + file.filename
        )
        sheared_filename = os.path.join(
            app.config["UPLOAD_FOLDER"], "sheared_" + file.filename
        )

        cv2.imwrite(scaled_filename, scaled_image)
        cv2.imwrite(rotated_filename, rotated_image)
        cv2.imwrite(translated_filename, translated_image)
        cv2.imwrite(sheared_filename, sheared_image)

        return render_template(
            "result.html",
            input_image=filename,
            scaled_image=scaled_filename,
            rotated_image=rotated_filename,
            translated_image=translated_filename,
            sheared_image=sheared_filename,
        )

    return "Invalid file format"


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
