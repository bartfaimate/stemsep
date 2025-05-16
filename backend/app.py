from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Run spleeter
    command = [
        'spleeter',
        'separate',
        '-i', filepath,
        '-p', 'spleeter:2stems',
        '-o', OUTPUT_FOLDER
    ]
    try:
        subprocess.run(command, check=True)
        return jsonify({'message': 'Stem separation complete', 'filename': file.filename})
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Spleeter failed'}), 500

@app.route('/download/<filename>/<stem>')
def download_stem(filename, stem):
    stem_file = os.path.join(filename.replace('.mp3', ''), f'{stem}.wav')
    return send_from_directory(OUTPUT_FOLDER, stem_file, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
