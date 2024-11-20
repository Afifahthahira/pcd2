from flask import Flask, send_file, request, render_template
import cv2
import numpy as np

app = Flask(__name__)

# Serve the home page
@app.route('/')
def home():
        return render_template('index.html')

@app.route('/add_product')
def add():
        return render_template('tambah-produk.html')

if __name__ == '__main__':
    app.run(debug=True)
