import os
import shutil
from flask import Flask, render_template, request, send_from_directory
import cv2
import numpy as np
import tensorflow as tf
from test_code.cartoonize import cartoonize  # cartoonize expects a folder of images

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
TEMP_INPUT_FOLDER = 'temp_input'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(TEMP_INPUT_FOLDER, exist_ok=True)

# === Sketch Generation Function ===
def generate_sketch(image_path, sketch_output_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"[SKETCH ERROR] Could not read image at: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256.0)
    cv2.imwrite(sketch_output_path, sketch)

# === Main Index Route ===
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = file.filename
            name_only = os.path.splitext(filename)[0]

            # Save uploaded image
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_path)

            # Reset temp_input folder
            if os.path.exists(TEMP_INPUT_FOLDER):
                shutil.rmtree(TEMP_INPUT_FOLDER)
            os.makedirs(TEMP_INPUT_FOLDER, exist_ok=True)
            shutil.copy(input_path, os.path.join(TEMP_INPUT_FOLDER, filename))

            # Reset cartoonized output folder
            cartoon_output_folder = os.path.join(RESULT_FOLDER, 'cartoonized')
            if os.path.exists(cartoon_output_folder):
                try:
                    shutil.rmtree(cartoon_output_folder)
                except PermissionError:
                    print("⚠️ Permission denied: Close any image viewer using the folder.")
            os.makedirs(cartoon_output_folder, exist_ok=True)

            # Run cartoonization
            model_path = 'test_code/saved_models'
            cartoonize(TEMP_INPUT_FOLDER, cartoon_output_folder, model_path)

            # Find output cartoon image
            cartoon_image = None
            for f in os.listdir(cartoon_output_folder):
                if f.lower() == filename.lower():
                    cartoon_image = f"results/cartoonized/{f}"
                    break

            # Generate sketch
            sketch_filename = f"sketch_{name_only}.png"
            sketch_path = os.path.join(RESULT_FOLDER, sketch_filename)
            try:
                generate_sketch(input_path, sketch_path)
                sketch_image = f"results/{sketch_filename}"
            except:
                sketch_image = None

            return render_template('result.html',
                                   cartoon_image=cartoon_image,
                                   sketch_image=sketch_image)

    return render_template('index.html')

# === Download Route ===
@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
