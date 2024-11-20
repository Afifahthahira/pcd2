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


if __name__ == '__main__':
    app.run(debug=True)
