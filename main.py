import os
import whisper
from gtts import gTTS
from googletrans import Translator
import google.generativeai as genai
import tempfile

# Configure Genai Key
genai.configure(api_key="AIzaSyCkif2CSS7X4HJxyLMJS2M-ZHPa_NnR9d8")

# Function to Load Google Gemini Model and provide queries as response
def get_gemini_response(message, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, message])
    return response.text

# Define Your Prompt
prompt = """
You are a translation assistant. Your task is to translate user messages into the specified target language.
- If the user provides text and specifies a target language, translate the text into that language.
- If the user asks to change the target language, remember the new target language for future translations.
- If the user asks anything other than translation, respond with an error message saying "I can only help with translations."

Examples:
1. Translate "Hello, how are you?" into Spanish.
2. Change the language to French.
3. Translate "Good morning" into the target language.
"""

class TranslatorAssistant:
    def __init__(self):
        self.model = whisper.load_model("base")
        # self.target_language = "Spanish"

    def transcribe_audio(self, audio_file):
        result = self.model.transcribe(audio_file)
        return result['text']

    def translate_text(self, text):
        translation_request = text
        response = get_gemini_response(translation_request, prompt)
        return response

    def text_to_speech(self, text):
        tts = gTTS(text=text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name

    def process_audio(self, audio_file):
        text = self.transcribe_audio(audio_file)
        translated_text = self.translate_text(text)
        audio_output_file = self.text_to_speech(translated_text)
        return audio_output_file

def main(audio_file_path):
    translator = TranslatorAssistant()
    translated_audio_file = translator.process_audio(audio_file_path)
    return translated_audio_file

if __name__ == "__main__":
    audio_file_path = "/input/LJ001-0005.wav"
    translated_audio_file = main(audio_file_path)
    print(f"Translated audio file saved as: {translated_audio_file}")