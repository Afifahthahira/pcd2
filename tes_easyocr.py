import easyocr
import cv2

image_path = 'test.jpg'  # Ganti dengan path gambar
image = cv2.imread(image_path)

reader = easyocr.Reader(['en'], gpu=True)  # Tambahkan bahasa sesuai kebutuhan

result = reader.readtext(image_path)

# Variabel untuk menghitung jumlah kemunculan kata "HERBALIFE"
herbalife_count = 0

for (bbox, text, confidence) in result:
    # Cek apakah kata 'HERBALIFE' ada dalam teks yang terdeteksi
    if 'HERBALIFE' in text.upper():  # Menggunakan .upper() agar pencarian tidak case-sensitive
        herbalife_count += 1

# Menampilkan jumlah kemunculan kata "HERBALIFE"
print(f'Jumlah kemunculan "HERBALIFE": {herbalife_count}')
