from flask import Flask, send_file, request, render_template
import cv2
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__)

# Konfigurasi database
db_config = {
    'host': 'localhost',         # Host database
    'user': 'root',              # Ganti dengan username MySQL Anda
    'password': '',              # Ganti dengan password MySQL Anda
    'database': 'herbalife'      # Nama database
}

# Fungsi untuk koneksi database
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Serve the home page
@app.route('/')
def home():
        return render_template('index.html')

# Serve the "add product" page
@app.route('/add_product')
def add():
    try:
        return send_file('tambah-produk.html')
    except FileNotFoundError:
        return "index.html file not found. Please ensure the file exists.", 404


if __name__ == '__main__':
    app.run(debug=True)
