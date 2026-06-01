from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from .utils import send_image_binary
from .image_io import get_current_image, set_current_image

restoration_bp = Blueprint('restoration', __name__)


@restoration_bp.route('/filter/gaussian', methods=['POST'])
def gaussian_blur():
    """
    Gaussian Blur
    Body JSON: { "kernel_size": int (ganjil, default 5), "sigma": float (default 0) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    k = int(data.get('kernel_size', 5))
    sigma = float(data.get('sigma', 0))
    if k % 2 == 0:
        k += 1

    result = cv2.GaussianBlur(img, (k, k), sigma)
    set_current_image(result)
    return send_image_binary(result)


@restoration_bp.route('/filter/median', methods=['POST'])
def median_filter():
    """
    Median Filter
    Body JSON: { "kernel_size": int (ganjil, default 5) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    k = int(data.get('kernel_size', 5))
    if k % 2 == 0:
        k += 1

    result = cv2.medianBlur(img, k)
    set_current_image(result)
    return send_image_binary(result)


@restoration_bp.route('/filter/denoise', methods=['POST'])
def denoise():
    """
    Noise Removal (Salt & Pepper) pakai Median Filter
    Body JSON: { "kernel_size": int (default 3) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    k = int(data.get('kernel_size', 3))
    if k % 2 == 0:
        k += 1

    # Median filter efektif untuk salt & pepper noise
    result = cv2.medianBlur(img, k)
    set_current_image(result)
    return send_image_binary(result)
