from flask import Flask, render_template, request
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load ROI coordinates from file
def load_roi_coordinates():
    roi_dict = {}
    try:
        with open("roi_coordinates.txt", "r") as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 5:
                    note_type, x, y, w, h = parts
                    roi_dict[note_type] = (int(x), int(y), int(w), int(h))
    except FileNotFoundError:
        print("roi_coordinates.txt not found.")
    return roi_dict

roi_coordinates = load_roi_coordinates()

def process_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (600, 300))  # Resize image for consistency
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Determine note type based on filename
    note_type = os.path.basename(image_path).split('.')[0]
    
    if note_type in roi_coordinates:
        x, y, w, h = roi_coordinates[note_type]
    else:
        return "Unknown Note Type", None

    roi = gray[y:y+h, x:x+w]  # Extract the selected ROI

    # Save the ROI for debugging
    roi_filename = f"roi_{os.path.basename(image_path)}"
    cv2.imwrite(os.path.join("static/uploads/", roi_filename), roi)
    print(f"ROI saved as {roi_filename}")

    # Calculate variance
    variance = np.var(roi)
    print(f"Variance for {image_path}: {variance}")

    # Adjust variance threshold based on actual values
    if "500" in note_type:
        variance_threshold = 100  # Adjust as per ₹500 notes
    elif "2000" in note_type:
        variance_threshold = 30  # Adjust as per ₹2000 notes (Real: 52, Fake: 11)
    else:
        variance_threshold = 200  # Default threshold

    result = "Fake" if variance < variance_threshold else "Real"
    return result, variance

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result, variance = process_image(filepath)
            return render_template('index.html', filename=filename, result=result, variance=variance)
    return render_template('index.html', filename=None, result=None, variance=None)

if __name__ == '__main__':
    app.run(debug=True)
