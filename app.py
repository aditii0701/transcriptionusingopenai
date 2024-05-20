import os
from flask import Flask, render_template, request, jsonify
import requests


# Load environment variables from .env file if it exists


app = Flask(__name__)

# Get the OpenAI API key from the environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # Check if the audio file is part of the request
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file uploaded'}), 400

        audio_file = request.files['audio_file']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Upload the file to OpenAI's Whisper model
        files = {
            'file': (audio_file.filename, audio_file, 'audio/mpeg')
        }
        data = {
            "model": "whisper-1"
        }
        upload_response = requests.post("https://api.openai.com/v1/audio/transcriptions", headers=HEADERS, files=files, data=data)

        # Log the response for debugging
        print(f"Upload response status: {upload_response.status_code}")
        print(f"Upload response content: {upload_response.content}")

        if upload_response.status_code != 200:
            return jsonify({'error': f'Error uploading file: {upload_response.content.decode()}'}), 500

        # Retrieve transcription
        transcript_response = upload_response.json()
        if 'error' in transcript_response:
            return jsonify({'error': transcript_response['error']['message']}), 500

        transcript_text = transcript_response.get('text', '')

        return jsonify({'transcript': transcript_text}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)