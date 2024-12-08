import cv2
import numpy as np
from PIL import Image
import os

# Path ke folder dataset
dataset_path = 'H:\SEMESTER 5\Prak. Pengolahan Citra Digital\pcd2\Additional Features\dataset'

# Inisialisasi recognizer LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load Haar Cascade untuk deteksi wajah
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def get_images_and_labels(dataset_path):
    face_samples = []
    ids = []
    labels = []
    label_to_id = {}
    current_id = 0

    for folder_name in os.listdir(dataset_path):
        folder_path = os.path.join(dataset_path, folder_name)
        if os.path.isdir(folder_path):
            # Tetapkan ID untuk setiap label (subfolder)
            label_to_id[folder_name] = current_id
            current_id += 1

            # Baca semua gambar dalam subfolder
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if file_name.endswith('.jpg') or file_name.endswith('.png'):
                    # Buka gambar dan konversi ke grayscale
                    pil_img = Image.open(file_path).convert('L')
                    img_numpy = np.array(pil_img, 'uint8')

                    # Deteksi wajah dalam gambar
                    faces = detector.detectMultiScale(img_numpy)
                    for (x, y, w, h) in faces:
                        face_samples.append(img_numpy[y:y+h, x:x+w])
                        ids.append(label_to_id[folder_name])
                        labels.append(folder_name)
    return face_samples, ids, label_to_id

# Dapatkan data wajah dan label dari dataset
faces, ids, label_to_id = get_images_and_labels(dataset_path)

# Latih model
recognizer.train(faces, np.array(ids))

# Simpan model dan peta label
recognizer.write('trainer.yml')  # Simpan model hasil training
with open('labels.txt', 'w') as f:
    for label, idx in label_to_id.items():
        f.write(f"{idx},{label}\n")

print(f"[INFO] Training selesai. {len(label_to_id)} label unik telah dilatih.")
