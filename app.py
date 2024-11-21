from flask import Flask, render_template, jsonify, request
import mysql.connector
from mysql.connector import Error
import pymysql

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
    # Koneksi ke database
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Query untuk mendapatkan data
    cursor.execute("SELECT id, barcode, image, name, stock FROM products")
    products = cursor.fetchall()

    # Tutup koneksi
    cursor.close()
    connection.close()

    # Kirim data ke template
    return render_template('index.html', products=products)

# Serve the "add product" page
@app.route('/add_product')
def add():
    return render_template('tambah-produk.html')

# API untuk menambahkan produk
@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    try:
        # Ambil data dari form
        barcode = request.form.get('barcode')
        name = request.form.get('nama')
        stock = request.form.get('stok')

        # # Ambil file gambar
        # image = request.files.get('gambar')
        # if not image:
        #     return jsonify({'error': 'File gambar wajib diunggah.'}), 400

        # Simpan gambar ke folder lokal (opsional, jika ingin menyimpan file)
        # image_path = f"uploads/{image.filename}"
        # image.save(image_path)

        # Simpan data ke database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            query = "INSERT INTO products (barcode, name, stock) VALUES (%s, %s, %s)"
            cursor.execute(query, (barcode, name, stock))
            conn.commit()
            return jsonify({'message': 'Produk berhasil ditambahkan!'}), 201
        else:
            return jsonify({'error': 'Database connection failed.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
