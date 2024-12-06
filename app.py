import os
import hashlib
import random
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, send_from_directory, session, redirect, url_for, Response
import mysql.connector
from mysql.connector import Error
import pymysql
import cv2
import easyocr

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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




# Fungsi untuk membuat hash dari password menggunakan SHA-256
def hash_password(password: str) -> str:
    """Menghasilkan hash dari password menggunakan SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Load model LBPH yang sudah dilatih
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer.yml')

# Load peta label dari file
id_to_label = {}
with open('labels.txt', 'r') as f:
    for line in f:
        idx, label = line.strip().split(',')
        id_to_label[int(idx)] = label

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Variabel global untuk menyimpan username aktif dan status autentikasi wajah
active_username = None
authenticated_face = False

def gen_frames():
    global active_username, authenticated_face
    cap = cv2.VideoCapture(0)  # Buka kamera
    while True:
        success, frame = cap.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            id_num, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            if confidence < 50:
                label = id_to_label.get(id_num, "Unknown")
                if label == active_username:  # Cocokkan dengan username aktif
                    authenticated_face = True  # Set status autentikasi wajah
                    # Jangan set session di sini
                    cap.release()
                    return
                text = f"{label} ({100 - confidence:.2f}%)"
            else:
                text = "Unknown"

            # Gambar kotak dan teks
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, text, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def login():
    if 'username' in session and 'authenticated_face' in session and session['authenticated_face']:
        # Jika sudah login dan sudah terautentikasi wajah, arahkan ke dashboard
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    global active_username, authenticated_face
    username = request.form['username']
    password = request.form['password']

    # Cek apakah username dan password valid di database
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user[2] == hash_password(password):  # Bandingkan hash password
            session['username'] = username
            active_username = username  # Simpan username ke variabel global
            authenticated_face = False  # Reset status autentikasi wajah
            return redirect(url_for('face_login'))  # Redirect ke face login untuk autentikasi wajah
        else:
            return render_template('login.html', error="Invalid credentials")
    else:
        return render_template('login.html', error="Database connection failed")

@app.route('/face_login')
def face_login():
    if 'username' not in session:  # Jika belum login, arahkan ke halaman login
        return redirect(url_for('login'))
    if 'authenticated_face' in session and session['authenticated_face']:
        return redirect(url_for('home'))  # Jika sudah terautentikasi wajah, arahkan ke dashboard
    return render_template('face_login.html')

@app.route('/video_feed')
def video_feed():
    if 'username' not in session:  # Jika belum login, arahkan ke halaman login
        return redirect(url_for('login'))
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/success')
def success():
    global authenticated_face
    if 'username' in session and authenticated_face:  # Pastikan pengguna sudah login dan wajah sudah terdeteksi
        session['authenticated_face'] = True  # Set session untuk autentikasi wajah
        return redirect(url_for('home')) 
    return redirect(url_for('login')) 

@app.route('/homee')
def home():
    if 'username' not in session or 'authenticated_face' not in session or not session['authenticated_face']:
        # Jika belum login atau belum terautentikasi wajah, arahkan ke halaman face login
        return redirect(url_for('face_login'))
    
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
    return render_template('index.html', products=products, username=session['username'])

# Serve the "add product" page
@app.route('/tambah_produk')
def add():
    if 'username' not in session or 'authenticated_face' not in session or not session['authenticated_face']:
        # Jika belum login atau belum terautentikasi wajah, arahkan ke halaman face login
        return redirect(url_for('face_login'))
    return render_template('tambah-produk.html', username=session['username'])

# produk keluar
@app.route('/produk_keluar', methods=['GET', 'POST'])
def produk_keluar():
    if 'username' not in session or 'authenticated_face' not in session or not session['authenticated_face']:
        # Jika belum login atau belum terautentikasi wajah, arahkan ke halaman face login
        return redirect(url_for('face_login'))
    return render_template('produk_keluar.html', username=session['username'])

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

# Updated API to count "HERBALIFE" in the image with random file name
@app.route('/api/count_herbalife', methods=['POST'])
def count_herbalife():
    if 'gambar_produk' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files['gambar_produk']
    if image_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Menentukan nama file baru dengan angka acak 4 digit
        filename, ext = os.path.splitext(image_file.filename)
        random_number = random.randint(1000, 9999)
        new_filename = f"{filename}_{random_number}{ext}"

        # Simpan gambar yang diunggah dengan nama baru
        image_path = os.path.join(UPLOAD_FOLDER, new_filename)
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
    
@app.route('/logout')
def logout():
    session.pop('username', None)  # Hapus session pengguna
    session.pop('authenticated_face', None)  # Hapus session autentikasi wajah
    return redirect(url_for('login'))
    
@app.route('/check_authentication')
def check_authentication():
    global authenticated_face
    if authenticated_face:
        return {'authenticated': True}
    return {'authenticated': False}

if __name__ == '__main__':
    app.run(debug=True)
