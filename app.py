# pyrefly: ignore [missing-import]
from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from routes.image_io import image_io_bp
from routes.enhancement import enhancement_bp
from routes.transformation import transformation_bp
from routes.restoration import restoration_bp
from routes.edge_binary import edge_binary_bp
from routes.color import color_bp
from routes.segmentation import segmentation_bp
from routes.compression import compression_bp

# Serve frontend dari folder 'frontend'
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

app.register_blueprint(image_io_bp)
app.register_blueprint(enhancement_bp)
app.register_blueprint(transformation_bp)
app.register_blueprint(restoration_bp)
app.register_blueprint(edge_binary_bp)
app.register_blueprint(color_bp)
app.register_blueprint(segmentation_bp)
app.register_blueprint(compression_bp)


@app.route('/')
def serve_frontend():
    """Serve halaman utama frontend"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


if __name__ == '__main__':
    print("=== Mini Photoshop Backend ===")
    print("Buka browser: http://localhost:5000")
    app.run(debug=True, port=5000)
