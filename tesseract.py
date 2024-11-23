import pytesseract
import cv2

# Path ke gambar
image_path = 'image2.jpg'  # Ganti dengan path gambar
image = cv2.imread(image_path)

# Menggunakan pytesseract untuk membaca teks dari gambar
# Pastikan Tesseract terinstall dan pathnya sudah benar
# Jika tidak, tentukan path tesseract secara eksplisit seperti ini:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Menjalankan OCR pada gambar
text = pytesseract.image_to_string(image)

# Variabel untuk menghitung jumlah kemunculan kata "HERBALIFE"
herbalife_count = text.upper().count('HERBALIFE')

# Menampilkan jumlah kemunculan kata "HERBALIFE"
print(f'Jumlah kemunculan "HERBALIFE": {herbalife_count}')
