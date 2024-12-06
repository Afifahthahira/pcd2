# add_product.py

from werkzeug.utils import secure_filename
import os
import mysql.connector
from flask import flash, redirect, url_for

# Folder untuk menyimpan gambar
UPLOAD_FOLDER = 'static/uploads'

# Konfigurasi database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_herbalife'
}

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_new_product(product_name, product_stock, product_barcode, product_image):
    if product_image and allowed_file(product_image.filename):
        filename = secure_filename(product_image.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        product_image.save(filepath)
    else:
        return False, 'Format gambar tidak valid. Harap unggah file dengan format .jpg, .jpeg, atau .png.'

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, image, barcode, stock) VALUES (%s, %s, %s, %s)",
            (product_name, filename, product_barcode, product_stock)
        )
        conn.commit()
        return True, 'Produk berhasil ditambahkan!'
    except Exception as e:
        return False, f'Error: {str(e)}'
    finally:
        cursor.close()
        conn.close()
