import os
import re
import subprocess
import logging
from phonemizer import phonemize
from phonemizer.backend import EspeakBackend
from IPython.display import Audio, display

# Setup logging
logging.basicConfig(level=logging.INFO)

# Directory for audio files
AUDIO_DIR = "ipa_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Clean IPA to safe filenames
def sanitize_filename(ipa_symbol):
    return re.sub(r'[^a-zA-Z0-9]', '_', ipa_symbol)

# Generate audio from original text (NOT IPA)
def generate_audio_with_espeak(original_text, lang_code, label):
    filename = f"{sanitize_filename(label)}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)

    try:
        subprocess.run([
            'espeak',
            f'-v{lang_code}',
            f'-w{filepath}',
            original_text
        ], check=True)
        return filepath
    except Exception as e:
        logging.error(f"Failed to generate audio for '{original_text}': {e}")
        return None

# Handle long input & generate IPA + audio
def process_user_input(text, input_language):
    lang_code = LANGUAGE_MAP.get(input_language, input_language)

    if lang_code not in EspeakBackend.supported_languages():
        print(f"Language '{input_language}' (→ '{lang_code}') not supported.")
        return

    # Split input into chunks of ≤ 25 words
    words = text.split()
    chunks = [' '.join(words[i:i+25]) for i in range(0, len(words), 25)]

    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}: \"{chunk}\"")

        try:
            phonemized_text = phonemize(
                chunk,
                language=lang_code,
                backend='espeak',
                strip=True
            )
        except Exception as e:
            print(f"Error phonemizing chunk: {e}")
            continue

        print(f"IPA: {phonemized_text}")

        audio_file = generate_audio_with_espeak(chunk, lang_code, f"chunk_{i}")
        if audio_file and os.path.exists(audio_file):
            display(Audio(audio_file))
        else:
            print("Audio generation failed.")

# Run
text_input = input("Enter text: ").strip()
lang_input = input("Enter valid espeak language code: ").strip()
process_user_input(text_input, lang_input)

