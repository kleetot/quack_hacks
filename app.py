import subprocess
import os

# Run the Bash script
subprocess.run(["bash", "imports.bash"], check=True)

print("Setup script executed successfully.")

from flask import Flask, request, jsonify, render_template
import re
from phonemizer import phonemize
from phonemizer.backend import EspeakBackend

app = Flask(__name__)
UPLOAD_DIR = "static/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

LANGUAGE_MAP = {
    "en": "en",
    "fr-fr": "fr-fr",
    "es": "es",
    "de": "de",
    "it": "it"
}

def sanitize_filename(text):
    return re.sub(r'[^a-zA-Z0-9]', '_', text)

def generate_audio(text, lang_code, label):
    filename = f"{sanitize_filename(label)}.wav"
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        subprocess.run([
            'espeak',
            f'-v{lang_code}',
            f'-w{filepath}',
            text
        ], check=True)
        return filepath
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process():
    data = request.json
    text = data.get('text', '').strip()
    lang = data.get('language', 'en')
    
    lang_code = LANGUAGE_MAP.get(lang, 'en')
    if lang_code not in EspeakBackend.supported_languages():
        return jsonify({"error": "Unsupported language."}), 400

    words = text.split()
    chunks = [' '.join(words[i:i+25]) for i in range(0, len(words), 25)]

    result = []
    for i, chunk in enumerate(chunks):
        try:
            ipa = phonemize(
                chunk,
                language=lang_code,
                backend='espeak',
                strip=True
            )
            audio_path = generate_audio(chunk, lang_code, f"chunk_{i}")
            audio_url = f"/{audio_path}" if audio_path else None
            result.append({"text": chunk, "ipa": ipa, "audio": audio_url})
        except Exception as e:
            result.append({"text": chunk, "ipa": "[error]", "audio": None})

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
