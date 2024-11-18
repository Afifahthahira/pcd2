from flask import Flask, send_file, request, render_template
import cv2
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__)

# Serve the home page
@app.route('/')
def home():
    try:
        return send_file('index.html')
    except FileNotFoundError:
        return "index.html file not found. Please ensure the file exists.", 404

@app.route('/add_product')
def add():
    try:
        return send_file('tambah-produk.html')
    except FileNotFoundError:
        return "index.html file not found. Please ensure the file exists.", 404

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        # Ambil data dari form
        barcode = request.form.get('barcode')
        nama_produk = request.form.get('nama')
        stok = request.form.get('stok')

        # Simpan data ke database atau proses lebih lanjut
        print(f"Barcode: {barcode}, Nama Produk: {nama_produk}, Stok: {stok}")

        # Contoh redirect ke halaman lain setelah data disimpan
        return redirect(url_for('success'))
    return render_template('tambah_produk.html')


if __name__ == '__main__':
    app.run(debug=True)
