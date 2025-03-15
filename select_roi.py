import cv2
import os

INPUT_FOLDER = "testing images"
OUTPUT_FOLDER = "converted_images"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Ensure output folder exists

def convert_to_jpg(image_path):
    """Convert image to JPG format and return new path."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"ERROR: Could not read {image_path}. Skipping...")
        return None
    
    new_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(os.path.basename(image_path))[0] + ".jpg")
    cv2.imwrite(new_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    return new_path

def select_roi(image_path, note_label):
    """Manually select ROI and save coordinates."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"ERROR: Could not read {image_path}. Skipping...")
        return

    image = cv2.resize(image, (600, 300))  # Resize for consistency
    roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    if sum(roi) == 0:
        print(f"No ROI selected for {note_label}. Skipping...")
        return

    x, y, w, h = roi
    print(f"ROI for {note_label}: x={x}, y={y}, w={w}, h={h}")

    # Save ROI coordinates
    with open("roi_coordinates.txt", "a") as f:
        f.write(f"{note_label},{x},{y},{w},{h}\n")

# Convert images and select ROI
image_files = os.listdir(INPUT_FOLDER)
for image_file in image_files:
    image_path = os.path.join(INPUT_FOLDER, image_file)
    jpg_path = convert_to_jpg(image_path)
    if jpg_path:
        select_roi(jpg_path, os.path.splitext(image_file)[0])

print("ROI selection completed! Coordinates saved in roi_coordinates.txt")
