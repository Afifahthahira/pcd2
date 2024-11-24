import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, send_from_directory
import mysql.connector
from mysql.connector import Error
import pymysql
import cv2
import easyocr

app = Flask(__name__)

# Konfigurasi folder uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route untuk melayani file di folder uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
@app.route('/tambah_produk')
def add():
    return render_template('tambah-produk.html')

# API untuk menambahkan produk
@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    # Ambil data dari form
    barcode = request.form.get('barcode')
    name = request.form.get('nama')
    stock = request.form.get('stok')

    # Ambil file gambar
    image = request.files.get('gambar')

    # Simpan gambar ke folder lokal
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    # Simpan data ke database
    conn = get_db_connection()
    with conn.cursor() as cursor:
        query = "INSERT INTO products (barcode, image, name, stock) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (barcode, image_path, name, stock))
        conn.commit()

    # Respons setelah berhasil menambahkan produk
    response = '''
        <script>
            alert("Produk berhasil ditambahkan!");
            window.location.href = "/tambah_produk";  // Arahkan kembali ke halaman tambah produk
        </script>
    '''
    # Tutup koneksi
    conn.close()
    return response

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

# API to delete a product
@app.route('/api/delete_product', methods=['POST'])
def api_delete_product():
    # Ambil barcode dari permintaan
    barcode = request.form.get('barcode')
    conn = get_db_connection()

    # Eksekusi query untuk menghapus produk
    with conn.cursor() as cursor:
        query = "DELETE FROM products WHERE barcode = %s"
        cursor.execute(query, (barcode,))
        conn.commit()

        # Cek apakah ada baris yang terpengaruh
        if cursor.rowcount > 0:
            response = '''
                <script>
                    alert("Produk berhasil dihapus!");
                    window.location.href = "/";
                </script>
            '''
        else:
            response = '''
                <script>
                    alert("Produk tidak ditemukan.");
                    window.location.href = "/";
                </script>
            '''

    # Tutup koneksi
    conn.close()
    return response


# produk keluar
@app.route('/produk_keluar', methods=['GET', 'POST'])
def produk_keluar():
    return render_template('produk_keluar.html')


@app.route('/api/get_product_by_barcode', methods=['POST'])
def get_product_by_barcode():
    barcode = request.json.get('barcode')
    print(f"Barcode received: {barcode}")  # Debugging barcode input
    # if not barcode:
    #     return jsonify({'error': 'Barcode tidak boleh kosong.'}), 400

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT name FROM products WHERE barcode = %s"
        cursor.execute(query, (barcode,))
        product = cursor.fetchone()
        print(f"Query result: {product}")  # Debugging hasil query

        if product:
            return jsonify({'name': product['name']}), 200
        else:
            return jsonify({'error': 'Produk tidak ditemukan.'}), 404
    else:
        return jsonify({'error': 'Gagal terhubung ke database.'}), 500

@app.route('/api/product_exit', methods=['GET', 'POST'])
def out_stock():
    conn = None
    cursor = None
    if request.method == 'POST':
        # Ambil data dari form
        barcode = request.form.get('barcode')
        quantity = request.form.get('quantity')

        # Cek apakah 'quantity' ada dan dapat dikonversi ke integer
        if quantity is None or quantity == '':
            return '''
                <script>
                    alert("Quantity tidak boleh kosong.");
                    window.location.href = "/";
                </script>
            '''
        try:
            quantity = int(quantity)
        except ValueError:
            return '''
                <script>
                    alert("Quantity harus berupa angka.");
                    window.location.href = "/produk_keluar";
                </script>
            '''

        # Koneksi ke database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Mulai transaksi secara eksplisit
        conn.start_transaction()

        # Cek stok produk berdasarkan barcode
        cursor.execute("SELECT name, stock FROM products WHERE barcode = %s", (barcode,))
        product = cursor.fetchone()

        if not product:
            return '''
                <script>
                    alert("Produk tidak ditemukan.");
                    window.location.href = "/produk_keluar";
                </script>
            '''

        product_name, current_stock = product

        # Periksa apakah stok cukup
        if current_stock < quantity:
            return '''
                <script>
                    alert("Stok tidak cukup untuk produk ini.");
                    window.location.href = "/produk_keluar";
                </script>
            '''

        # Kurangi stok di tabel 'products'
        cursor.execute("UPDATE products SET stock = stock - %s WHERE barcode = %s", (quantity, barcode))

        # Simpan transaksi ke tabel 'produk_keluar'
        cursor.execute(
            "INSERT INTO produk_keluar (product_name, jumlah_keluar) VALUES (%s, %s)",
            (product_name, quantity)
        )

        # Commit transaksi
        conn.commit()

        # Tutup koneksi
        conn.close()

        # Kirimkan response pop-up dan redirect
        return '''
            <script>
                alert("Produk berhasil dikeluarkan, stok diperbarui!");
                window.location.href = "/produk_keluar";
            </script>
        '''

    return render_template('produk_keluar.html')

@app.route('/api/count_herbalife', methods=['POST'])
def count_herbalife():
    if 'gambar_produk' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['gambar_produk']
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Simpan gambar yang diunggah
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)

        # Membaca gambar dan menggunakan EasyOCR untuk mendeteksi teks
        image = cv2.imread(image_path)
        reader = easyocr.Reader(['en'], gpu=True)
        result = reader.readtext(image)

        herbalife_count = 0
        # Menentukan jumlah kemunculan kata "HERBALIFE" dalam gambar
        for (bbox, text, confidence) in result:
            if 'HERBALIFE' in text.upper():
                herbalife_count += 1
        
        os.remove(image_path)
        return jsonify({"stok_herbalife": herbalife_count}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
