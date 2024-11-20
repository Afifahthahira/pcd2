from flask import Flask, send_file, request, jsonify
import mysql.connector
from mysql.connector import Error

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
    try:
        return send_file('index.html')
    except FileNotFoundError:
        return "index.html file not found. Please ensure the file exists.", 404

# Serve the "add product" page
@app.route('/add_product')
def add():
    try:
        return send_file('tambah-produk.html')
    except FileNotFoundError:
        return "tambah-produk.html file not found. Please ensure the file exists.", 404

# API untuk menambahkan produk
@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    data = request.form
    barcode = data.get('barcode')
    gambar = data.get('gambar')
    nama_produk = data.get('nama_produk')
    stok = data.get('stok')

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "INSERT INTO daftar_produk (barcode, gambar, nama_produk, stok) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (barcode, gambar, nama_produk, stok))
            conn.commit()
            return jsonify({'message': 'Produk berhasil ditambahkan!'}), 201
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'error': 'Database connection failed.'}), 500

# API untuk mendapatkan daftar produk
@app.route('/api/products', methods=['GET'])
def api_get_products():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM daftar_produk"
            cursor.execute(query)
            products = cursor.fetchall()
            return jsonify(products), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'error': 'Database connection failed.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
