import cv2
from matplotlib import pyplot as plt

# Baca gambar
image = cv2.imread("test.jpg")

# Ubah gambar ke grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Terapkan thresholding untuk segmentasi
_, thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

# Temukan kontur objek
contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter kontur berdasarkan ukuran untuk mengabaikan noise
filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 1000]

# Gambarkan kontur pada gambar asli
output_image = image.copy()
for i, contour in enumerate(filtered_contours):
    cv2.drawContours(output_image, [contour], -1, (0, 255, 0), 2)

    # Tambahkan nomor urut pada setiap objek
    x, y, w, h = cv2.boundingRect(contour)
    cv2.putText(output_image, f"Objek {i+1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Tampilkan hasil deteksi
print(f"Jumlah objek yang terdeteksi: {len(filtered_contours)}")

# Konversi BGR ke RGB untuk Matplotlib
output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)

# Tampilkan gambar menggunakan matplotlib
plt.imshow(output_image)
plt.title("Deteksi Objek")
plt.axis("off")
plt.show()
