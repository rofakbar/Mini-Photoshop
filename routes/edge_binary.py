from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from .utils import send_image_binary
from .image_io import get_current_image, set_current_image

edge_binary_bp = Blueprint('edge_binary', __name__)


@edge_binary_bp.route('/binary/threshold', methods=['POST'])
def threshold():
    """
    Thresholding (binary image)
    Body JSON: { "value": int (0-255, default 127) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    thresh_val = int(data.get('value', 127))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, result = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)

    set_current_image(result)
    return send_image_binary(result)


@edge_binary_bp.route('/edge/detect', methods=['POST'])
def edge_detect():
    """
    Edge Detection
    Body JSON: { "method": "canny"|"sobel"|"prewitt"|"robert"|"laplacian"|"log" }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    method = data.get('method', 'canny').lower()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if method == 'canny':
        result = cv2.Canny(gray, 100, 200)

    elif method == 'sobel':
        sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        result = cv2.convertScaleAbs(np.sqrt(sx**2 + sy**2))

    elif method == 'prewitt':
        kernel_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
        kernel_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
        px = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
        py = cv2.filter2D(gray, cv2.CV_64F, kernel_y)
        result = cv2.convertScaleAbs(np.sqrt(px**2 + py**2))

    elif method == 'robert':
        kernel_x = np.array([[1, 0], [0, -1]], dtype=np.float32)
        kernel_y = np.array([[0, 1], [-1, 0]], dtype=np.float32)
        rx = cv2.filter2D(gray, cv2.CV_64F, kernel_x)
        ry = cv2.filter2D(gray, cv2.CV_64F, kernel_y)
        result = cv2.convertScaleAbs(np.sqrt(rx**2 + ry**2))

    elif method == 'laplacian':
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        result = cv2.convertScaleAbs(lap)

    elif method == 'log':
        # Laplacian of Gaussian
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        lap = cv2.Laplacian(blurred, cv2.CV_64F)
        result = cv2.convertScaleAbs(lap)

    else:
        return jsonify({'error': f'Method tidak dikenal: {method}'}), 400

    set_current_image(result)
    return send_image_binary(result)


@edge_binary_bp.route('/morphology', methods=['POST'])
def morphology():
    """
    Morphology (Erosion / Dilation)
    Body JSON: { "operation": "erosion"|"dilation", "kernel_size": int (default 5) }
    """
    img = get_current_image()
    if img is None:
        return jsonify({'error': 'Belum ada gambar'}), 400

    data = request.get_json()
    operation = data.get('operation', 'erosion').lower()
    k = int(data.get('kernel_size', 5))

    kernel = np.ones((k, k), np.uint8)

    if operation == 'erosion':
        result = cv2.erode(img, kernel, iterations=1)
    elif operation == 'dilation':
        result = cv2.dilate(img, kernel, iterations=1)
    else:
        return jsonify({'error': f'Operation tidak dikenal: {operation}'}), 400

    set_current_image(result)
    return send_image_binary(result)
