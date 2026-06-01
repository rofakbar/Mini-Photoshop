from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from .utils import send_image_binary
from .image_io import get_current_image, set_current_image

segmentation_bp = Blueprint('segmentation', __name__)


@segmentation_bp.route('/segment', methods=['POST'])
def segment():
    """
    Image Segmentation
    Body JSON: { "method": "threshold"|"edge"|"region" }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    method = data.get('method', 'threshold').lower()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if method == 'threshold':
        # Otsu thresholding otomatis
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    elif method == 'edge':
        # Edge-based segmentation pakai Canny
        result = cv2.Canny(gray, 50, 150)

    elif method == 'region':
        # Region-based: adaptive thresholding
        result = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

    else:
        return jsonify({'error': f'Method tidak dikenal: {method}'}), 400

    set_current_image(result)
    return send_image_binary(result)
