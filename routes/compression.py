# pyrefly: ignore [missing-import]
from flask import Blueprint, request, jsonify
# pyrefly: ignore [missing-import]
import cv2
import numpy as np
import base64
from .image_io import get_current_image, set_current_image
from .utils import send_image_binary

compression_bp = Blueprint('compression', __name__)


@compression_bp.route('/compress', methods=['POST'])
def compress():
    """
    Simulasi kompresi JPEG dengan kualitas berbeda
    Body JSON: { "quality": int (1-100, default 50) }
    Makin rendah quality = makin terkompresi = makin blur/pecah
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    quality = int(data.get('quality', 50))
    quality = max(1, min(100, quality))  # clamp 1-100

    # Encode ke JPEG dengan quality tertentu, lalu decode balik
    # Ini mensimulasikan lossy compression JPEG
    encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
    _, buffer = cv2.imencode('.jpg', img, encode_params)
    result = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    set_current_image(result)

    # Hitung ukuran file sebelum dan sesudah (bytes)
    _, orig_buf = cv2.imencode('.png', img)
    original_size = len(orig_buf)
    compressed_size = len(buffer)

    return send_image_binary(result, extra_headers={
        'X-Original-Size-KB': round(original_size / 1024, 2),
        'X-Compressed-Size-KB': round(compressed_size / 1024, 2),
        'X-Quality': quality
    })
