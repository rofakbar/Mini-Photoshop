from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from .utils import send_image_binary
from .image_io import get_current_image, set_current_image

enhancement_bp = Blueprint('enhancement', __name__)


@enhancement_bp.route('/enhance/brightness-contrast', methods=['POST'])
def brightness_contrast():
    """
    Brightness & Contrast adjustment
    Body JSON: { "brightness": int (-100 ~ 100), "contrast": int (-100 ~ 100) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    brightness = int(data.get('brightness', 0))
    contrast = int(data.get('contrast', 0))

    # Rumus: output = contrast * input + brightness
    alpha = (contrast + 100) / 100.0  # contrast: 0.0 ~ 2.0
    beta = brightness                  # brightness: -100 ~ 100

    result = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    set_current_image(result)
    return send_image_binary(result)


@enhancement_bp.route('/enhance/histogram-eq', methods=['POST'])
def histogram_eq():
    """Histogram Equalization"""
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    # Convert ke YUV, equalize channel Y (luminance), convert balik
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    result = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    set_current_image(result)
    return send_image_binary(result)


@enhancement_bp.route('/enhance/sharpen', methods=['POST'])
def sharpen():
    """Sharpening menggunakan kernel"""
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    kernel = np.array([
        [ 0, -1,  0],
        [-1,  5, -1],
        [ 0, -1,  0]
    ])
    result = cv2.filter2D(img, -1, kernel)

    set_current_image(result)
    return send_image_binary(result)


@enhancement_bp.route('/enhance/blur', methods=['POST'])
def blur():
    """
    Smoothing / Blur
    Body JSON: { "kernel_size": int (harus ganjil, default 5) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    k = int(data.get('kernel_size', 5))
    if k % 2 == 0:
        k += 1  # pastikan ganjil

    result = cv2.blur(img, (k, k))
    set_current_image(result)
    return send_image_binary(result)
