import cv2

# Load model LBPH yang sudah dilatih
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer.yml')

# Load peta label dari file
id_to_label = {}
with open('labels.txt', 'r') as f:
    for line in f:
        idx, label = line.strip().split(',')
        id_to_label[int(idx)] = label

# Load Haar Cascade untuk deteksi wajah
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Buka kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        # Prediksi ID berdasarkan wajah yang terdeteksi
        id_num, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        if confidence < 50:  # Jika confidence rendah, berarti cocok
            label = id_to_label.get(id_num, "Unknown")
            text = f"{label} ({100 - confidence:.2f}%)"
        else:
            text = "Unknown"

        # Gambar kotak di wajah dan label
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, text, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Face Recognition', frame)
    if cv2.waitKey(1) == 27:  # Tekan ESC untuk keluar
        break

cap.release()
cv2.destroyAllWindows()
