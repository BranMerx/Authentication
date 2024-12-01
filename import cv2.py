import cv2
import os

file_path = "C:/Users/brand/AppData/Local/Packages/PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0/LocalCache/local-packages/Python311/site-packages/cv2/data/haarcascade_frontalface_default.xml"

print("File path exists:", os.path.exists(file_path))

# Load the cascade
face_cascade = cv2.CascadeClassifier(file_path)
if face_cascade.empty():
    print("Failed to load the cascade. Check the file or permissions.")
else:
    print("Cascade loaded successfully!")
