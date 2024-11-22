import easyocr
import cv2
import matplotlib.pyplot as plt

image_path = 'image.jpg'  # Ganti dengan path gambar
image = cv2.imread(image_path)

reader = easyocr.Reader(['en', 'id'])  # Tambahkan bahasa sesuai kebutuhan

result = reader.readtext(image_path)

for (bbox, text, confidence) in result:
    print(f"Text: {text}, Confidence: {confidence}")

for (bbox, text, confidence) in result:
    # Koordinat bounding box
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    
    # Gambarkan bounding box
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    
    # Tambahkan teks
    cv2.putText(image, text, (top_left[0], top_left[1] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Tampilkan gambar dengan bounding box
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()
