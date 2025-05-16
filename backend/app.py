from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
from pathlib import Path

from spleeter.separator import Separator


def init_app():
    app = Flask(__name__)
    CORS(app)
   
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'output'
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    return app

app = init_app()


@app.route('/', methods=['GET'])
def index(): 
    return jsonify({'message': 'Welcome to the Spleeter API!'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filepath = Path('uploads') / file.filename
    file.save(filepath)

    # # Run spleeter
    # command = [
    #     'spleeter',
    #     'separate',
    #     '-i', filepath,
    #     '-p', 'spleeter:2stems',
    #     '-o', OUTPUT_FOLDER
    # ]
    sep = Separator('spleeter:2stems')
    sep.separate_to_file(filepath, "output")
    
    
    try:
        # subprocess.run(command, check=True)
        return jsonify({'message': 'Stem separation complete', 'filename': file.filename})
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Spleeter failed'}), 500

@app.route('/download/<filename>/<stem>')
def download_stem(filename, stem):
    filename = Path(filename)
    stem_file = Path(filename).stem + '_' + stem + '.wav'
    return send_from_directory(OUTPUT_FOLDER, stem_file, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
