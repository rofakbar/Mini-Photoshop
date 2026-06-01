# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
import cv2
import numpy as np
from .utils import decode_image, send_image_binary

image_io_bp = Blueprint('image_io', __name__)

# Simpan gambar original di memori (supaya bisa di-reset)
stored_images = {
    'original': None,
    'current': None
}

@image_io_bp.route('/upload', methods=['POST'])
def upload():
    """Terima gambar dari frontend, simpan di memori"""
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada file gambar'}), 400

    img = decode_image(request.files['image'])
    if img is None:
        return jsonify({'error': 'Gagal membaca gambar'}), 400

    stored_images['original'] = img.copy()
    stored_images['current'] = img.copy()

    return send_image_binary(img)


@image_io_bp.route('/reset', methods=['POST'])
def reset():
    """Reset gambar ke kondisi original"""
    if stored_images['original'] is None:
        return jsonify({'error': 'Belum ada gambar yang diupload'}), 400

    stored_images['current'] = stored_images['original'].copy()
    return send_image_binary(stored_images['current'])


def get_current_image():
    """Helper: ambil gambar current dari memori (dipakai route lain)"""
    return stored_images['current']

def set_current_image(img):
    """Helper: simpan hasil edit ke current (dipakai route lain)"""
    stored_images['current'] = img.copy()


def generate_histogram(img):
    """Buat gambar histogram dari numpy array"""
    hist_w, hist_h = 512, 256
    hist_img = np.zeros((hist_h, hist_w, 3), dtype=np.uint8)
    hist_img[:] = (25, 25, 25)

    # Grid halus
    for y in range(0, hist_h, hist_h // 4):
        cv2.line(hist_img, (0, y), (hist_w, y), (45, 45, 45), 1)
    for x in range(0, hist_w, hist_w // 4):
        cv2.line(hist_img, (x, 0), (x, hist_h), (45, 45, 45), 1)

    bin_w = hist_w / 256.0

    if len(img.shape) == 2:  # Grayscale
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        cv2.normalize(hist, hist, 0, hist_h - 10, cv2.NORM_MINMAX)
        pts = np.array([[int(i * bin_w), hist_h - int(hist[i])] for i in range(256)], np.int32)
        cv2.polylines(hist_img, [pts], False, (200, 200, 200), 1, cv2.LINE_AA)
    else:  # Color BGR
        colors = [(255, 80, 80), (80, 220, 80), (80, 80, 255)]
        for ch, color in enumerate(colors):
            hist = cv2.calcHist([img], [ch], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, hist_h - 10, cv2.NORM_MINMAX)
            pts = np.array([[int(i * bin_w), hist_h - int(hist[i])] for i in range(256)], np.int32)
            cv2.polylines(hist_img, [pts], False, color, 1, cv2.LINE_AA)

    return hist_img


@image_io_bp.route('/histogram/<which>', methods=['GET'])
def histogram(which):
    """Return histogram image (original atau current)"""
    if which == 'original':
        img = stored_images['original']
    else:
        img = stored_images['current']

    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    hist_img = generate_histogram(img)
    return send_image_binary(hist_img)
