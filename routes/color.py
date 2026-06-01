from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from .utils import send_image_binary
from .image_io import get_current_image, set_current_image

color_bp = Blueprint('color', __name__)


@color_bp.route('/color/grayscale', methods=['POST'])
def to_grayscale():
    """Convert RGB ke Grayscale"""
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    set_current_image(result)
    return send_image_binary(result)


@color_bp.route('/color/split-channel', methods=['POST'])
def split_channel():
    """
    Split channel R, G, atau B
    Body JSON: { "channel": "r"|"g"|"b" }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    channel = data.get('channel', 'r').lower()

    # OpenCV format: BGR
    b, g, r = cv2.split(img)
    zeros = np.zeros_like(b)

    if channel == 'r':
        result = cv2.merge([zeros, zeros, r])
    elif channel == 'g':
        result = cv2.merge([zeros, g, zeros])
    elif channel == 'b':
        result = cv2.merge([b, zeros, zeros])
    else:
        return jsonify({'error': 'Channel tidak valid. Gunakan r, g, atau b'}), 400

    set_current_image(result)
    return send_image_binary(result)


@color_bp.route('/color/adjust-hue-saturation', methods=['POST'])
def adjust_hue_saturation():
    """
    Adjust Hue dan Saturation
    Body JSON: { "hue": int (-180 ~ 180), "saturation": int (0 ~ 200) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    hue_shift = int(data.get('hue', 0))
    sat_scale = int(data.get('saturation', 100))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.int32)

    # Shift hue (channel 0), range 0-179 di OpenCV
    hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180

    # Scale saturation (channel 1), range 0-255
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat_scale / 100, 0, 255)

    hsv = hsv.astype(np.uint8)
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    set_current_image(result)
    return send_image_binary(result)
