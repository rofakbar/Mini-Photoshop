import cv2
import numpy as np
import base64
import io
from flask import send_file, make_response

def decode_image(file_storage):
    """Terima file dari request.files, return numpy array (BGR)"""
    file_bytes = np.frombuffer(file_storage.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img

def encode_image(img):
    """(Deprecated) Ubah numpy array jadi base64 string"""
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    _, buffer = cv2.imencode('.png', img)
    b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64}"

def send_image_binary(img, extra_headers=None):
    """Kirim numpy array langsung sebagai binary file (JPEG)"""
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    io_buf = io.BytesIO(buffer)
    
    response = make_response(send_file(io_buf, mimetype='image/jpeg'))
    
    # Add CORS headers if necessary, though Flask-CORS might handle it.
    response.headers['Access-Control-Expose-Headers'] = 'X-Original-Size-KB, X-Compressed-Size-KB'
    
    if extra_headers:
        for k, v in extra_headers.items():
            response.headers[k] = str(v)
            
    return response
