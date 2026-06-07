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
    """Buat gambar histogram dari numpy array (VERSI ESTETIK)"""
    hist_w, hist_h = 512, 256
    
    # 1. Background sama persis dengan warna div Tailwind lu (#1a1a1a = RGB 26, 26, 26)
    hist_img = np.full((hist_h, hist_w, 3), 26, dtype=np.uint8)

    # 2. Grid (Hanya garis horizontal samar biar lebih clean)
    for y in range(0, hist_h, hist_h // 4):
        cv2.line(hist_img, (0, y), (hist_w, y), (45, 45, 45), 1)

    bin_w = hist_w / 256.0

    try:
        if len(img.shape) == 2:  # Grayscale
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            cv2.normalize(hist, hist, 0, hist_h - 10, cv2.NORM_MINMAX)
            hist = hist.flatten()
            
            # Koordinat garis
            pts = np.array([[int(i * bin_w), int(hist_h - hist[i])] for i in range(256)], dtype=np.int32)
            # Koordinat area bawah kurva (ditambah titik pojok bawah)
            pts_fill = np.array([[0, hist_h]] + pts.tolist() + [[hist_w, hist_h]], dtype=np.int32)
            
            # Warnai area bawah kurva (Abu-abu transparan 30%)
            overlay = hist_img.copy()
            cv2.fillPoly(overlay, [pts_fill], (150, 150, 150))
            cv2.addWeighted(overlay, 0.3, hist_img, 0.7, 0, hist_img)
            
            # Gambar garis utama lebih tebal (ketebalan 2)
            cv2.polylines(hist_img, [pts], False, (220, 220, 220), 2, cv2.LINE_AA)

        else:  # Color BGR
            # Palet warna modern & estetik untuk OpenCV (Formatnya BGR, bukan RGB)
            colors = [
                (255, 120, 50),   # Channel Biru (Neon Blue)
                (100, 220, 100),  # Channel Hijau (Pastel Green)
                (50, 100, 255)    # Channel Merah (Coral Red)
            ]
            
            for ch, color in enumerate(colors):
                hist = cv2.calcHist([img], [ch], None, [256], [0, 256])
                cv2.normalize(hist, hist, 0, hist_h - 10, cv2.NORM_MINMAX)
                hist = hist.flatten()
                
                # Koordinat garis
                pts = np.array([[int(i * bin_w), int(hist_h - hist[i])] for i in range(256)], dtype=np.int32)
                # Koordinat area bawah kurva
                pts_fill = np.array([[0, hist_h]] + pts.tolist() + [[hist_w, hist_h]], dtype=np.int32)
                
                # Warnai area bawah kurva per warna (Transparan 20% biar kalau numpuk tetep cakep)
                overlay = hist_img.copy()
                cv2.fillPoly(overlay, [pts_fill], color)
                cv2.addWeighted(overlay, 0.2, hist_img, 0.8, 0, hist_img)
                
                # Gambar garis utama per warna
                cv2.polylines(hist_img, [pts], False, color, 2, cv2.LINE_AA)

    except Exception as e:
        print(f"ERROR SAAT BIKIN HISTOGRAM: {e}")

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
