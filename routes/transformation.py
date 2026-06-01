from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from .utils import send_image_binary
from .image_io import get_current_image, set_current_image

transformation_bp = Blueprint('transformation', __name__)


@transformation_bp.route('/transform/rotate', methods=['POST'])
def rotate():
    """
    Rotate gambar
    Body JSON: { "angle": float (0-360) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    angle = float(data.get('angle', 90))

    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)

    # Hitung bounding box baru supaya gambar tidak terpotong
    cos = np.abs(matrix[0, 0])
    sin = np.abs(matrix[0, 1])
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)

    # Sesuaikan translasi ke center baru
    matrix[0, 2] += (new_w - w) / 2
    matrix[1, 2] += (new_h - h) / 2

    result = cv2.warpAffine(img, matrix, (new_w, new_h))

    set_current_image(result)
    return send_image_binary(result)


@transformation_bp.route('/transform/flip', methods=['POST'])
def flip():
    """
    Flip gambar
    Body JSON: { "direction": "horizontal" | "vertical" }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    direction = data.get('direction', 'horizontal')

    flip_code = 1 if direction == 'horizontal' else 0
    result = cv2.flip(img, flip_code)

    set_current_image(result)
    return send_image_binary(result)


@transformation_bp.route('/transform/crop', methods=['POST'])
def crop():
    """
    Crop gambar
    Body JSON: { "x": int, "y": int, "width": int, "height": int }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    x = int(data.get('x', 0))
    y = int(data.get('y', 0))
    w = int(data.get('width', img.shape[1]))
    h = int(data.get('height', img.shape[0]))

    # Clamp supaya tidak keluar batas gambar
    x = max(0, x)
    y = max(0, y)
    w = min(w, img.shape[1] - x)
    h = min(h, img.shape[0] - y)

    result = img[y:y+h, x:x+w]

    set_current_image(result)
    return send_image_binary(result)


@transformation_bp.route('/transform/resize', methods=['POST'])
def resize():
    """
    Resize gambar
    Body JSON: { "width": int, "height": int, "interpolation": "nearest"|"bilinear" }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    w = int(data.get('width', img.shape[1]))
    h = int(data.get('height', img.shape[0]))
    interp_mode = data.get('interpolation', 'bilinear')

    interp = cv2.INTER_LINEAR if interp_mode == 'bilinear' else cv2.INTER_NEAREST
    result = cv2.resize(img, (w, h), interpolation=interp)

    set_current_image(result)
    return send_image_binary(result)


@transformation_bp.route('/transform/translate', methods=['POST'])
def translate():
    """
    Translation (geser posisi)
    Body JSON: { "tx": int, "ty": int }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    tx = int(data.get('tx', 0))
    ty = int(data.get('ty', 0))

    h, w = img.shape[:2]
    matrix = np.float32([[1, 0, tx], [0, 1, ty]])
    result = cv2.warpAffine(img, matrix, (w, h))

    set_current_image(result)
    return send_image_binary(result)
