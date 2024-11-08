import os
import whisper
from gtts import gTTS
import google.generativeai as genai
import tempfile
import threading

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

    def transcribe_audio(self, audio_file):
        result = self.model.transcribe(audio_file)
        return result['text']

    def translate_text(self, text):
        translation_request = text
        response = get_gemini_response(translation_request, prompt)
        return response

    def text_to_speech(self, text, output_folder):
        tts = gTTS(text=text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=output_folder)
        tts.save(temp_file.name)
        return temp_file.name

    def process_audio(self, input_file_path, output_folder):
        filename = os.path.basename(input_file_path)
        text = self.transcribe_audio(input_file_path)
        translated_text = self.translate_text(text)
        audio_output_file = self.text_to_speech(translated_text, output_folder)
        output_file_path = os.path.join(output_folder, f"translated_{filename}.mp3")

        # Check if the final output path already exists
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

        os.rename(audio_output_file, output_file_path)
        return output_file_path


def process_file(translator, input_file_path, output_folder):
    translated_audio_file = translator.process_audio(input_file_path, output_folder)
    print(f"Translated audio file saved as: {translated_audio_file}")


def main(input_folder, output_folder):
    translator = TranslatorAssistant()
    threads = []

    for filename in os.listdir(input_folder):
        if filename.endswith(".wav"):
            input_file_path = os.path.join(input_folder, filename)
            thread = threading.Thread(target=process_file, args=(translator, input_file_path, output_folder))
            threads.append(thread)
            thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    input_folder = "C:\\Users\\ergou\\PycharmProjects\\pythonProject\\audio_translation\\input"
    output_folder = "C:\\Users\\ergou\\PycharmProjects\\pythonProject\\audio_translation\\output"
    main(input_folder, output_folder)
