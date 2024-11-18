from flask import Flask, request, jsonify
import cv2
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__)

@app.route('/scan-barcode', methods=['POST'])
def scan_barcode():
    # Simulasi hasil barcode untuk testing
    # Bisa diganti dengan proses capture gambar menggunakan kamera
    sample_barcode = "123456789012"
    return jsonify({"barcode": sample_barcode})

@app.route('/add-product', methods=['POST'])
def add_product():
    nama = request.form.get('nama')
    stok = request.form.get('stok')
    barcode = request.form.get('barcode')
    file = request.files.get('gambar')

    if not nama or not stok or not barcode or not file:
        return jsonify({"message": "Data tidak lengkap."}), 400

    # Simpan data ke database atau file system (simulasi saja)
    filename = file.filename
    file.save(f'./uploads/{filename}')
    return jsonify({"message": "Produk berhasil ditambahkan!"})

if __name__ == '__main__':
    app.run(debug=True)
