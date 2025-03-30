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
    'afrikaans': 'af',
    'aragonese': 'an',
    'bulgarian': 'bg',
    'bengali': 'bn',
    'bosnian': 'bs',
    'catalan': 'ca',
    'czech': 'cs',
    'welsh': 'cy',
    'danish': 'da',
    'german': 'de',
    'greek': 'el',
    'default': 'en',
    'english': 'en-gb',
    'en-scottish': 'en-sc',
    'english-north': 'en-uk-north',
    'english rp': 'en-uk-rp',
    'english wmids': 'en-uk-wmids',
    'english-us': 'en-us',
    'en-westindies': 'en-wi',
    'esperanto': 'eo',
    'spanish': 'es',
    'spanish-latin-am': 'es-la',
    'estonian': 'et',
    'basque-test': 'eu',
    'Persian+English-US': 'fa',
    'persian-pinglish': 'fa-pin',
    'finnish': 'fi',
    'french-Belgium': 'fr-be',
    'french': 'fr-fr',
    'irish-gaeilge': 'ga',
    'greek-ancient': 'grc',
    'gujarati-test': 'gu',
    'hindi': 'hi',
    'croatian': 'hr',
    'hungarian': 'hu',
    'armenian': 'hy',
    'armenian-west': 'hy-west',
    'interlingua': 'ia',
    'indonesian': 'id',
    'icelandic': 'is',
    'italian': 'it',
    'lojban': 'jbo',
    'georgian': 'ka',
    'kannada': 'kn',
    'kurdish': 'ku',
    'latin': 'la',
    'lingua franca nova': 'lfn',
    'lithuanian': 'lt',
    'latvian': 'lv',
    'macedonian': 'mk',
    'malayalam': 'ml',
    'malay': 'ms',
    'nepali': 'ne',
    'dutch': 'nl',
    'norwegian': 'no',
    'punjabi': 'pa',
    'polish': 'pl',
    'brazil': 'pt-br',
    'portugal': 'pt-pt',
    'romanian': 'ro',
    'russian': 'ru',
    'slovak': 'sk',
    'albanian': 'sq',
    'serbian': 'sr',
    'swedish': 'sv',
    'swahili-test': 'sw',
    'tamil': 'ta',
    'telugu-test': 'te',
    'turkish': 'tr',
    'vietnam': 'vi',
    'vietnam hue': 'vi-hue',
    'vietnam sgn': 'vi-sgn',
    'Mandarin': 'zh',
    'cantonese': 'zh-yue'
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
