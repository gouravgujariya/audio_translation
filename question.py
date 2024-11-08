import tkinter as tk
from tkinter import filedialog
import pyaudio
import wave
from pydub import AudioSegment
import os
import whisper
from gtts import gTTS
from googletrans import Translator
import google.generativeai as genai
import tempfile
# from httpcore import SyncHTTPTransport

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

    def text_to_speech(self, text, lang='en'):
        tts = gTTS(text=text, lang=lang)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name

    def process_audio(self, audio_file):
        text = self.transcribe_audio(audio_file)
        translated_text = self.translate_text(text)
        audio_output_file = self.text_to_speech(translated_text)
        return text, translated_text, audio_output_file

    def output(self, audio_file):
        text, translated_text, audio_output_file = self.process_audio(audio_file)
        print(f"Original Text: {text}")
        print(f"Translated Text: {translated_text}")
        return audio_output_file


class AudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Translator")

        self.record_button = tk.Button(root, text="Record Audio", command=self.record_audio)
        self.record_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.play_button = tk.Button(root, text="Play Translated Audio", command=self.play_audio, state=tk.DISABLED)
        self.play_button.pack(pady=10)

        self.language_button = tk.Button(root, text="Change Language", command=self.change_language)
        self.language_button.pack(pady=10)

        self.file_path = "output.wav"
        self.recording = False
        self.frames = []

        self.audio = pyaudio.PyAudio()
        self.stream = None

        self.translator = TranslatorAssistant()

    def record_audio(self):
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.recording = True
        self.frames = []

        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024)
        self.root.after(10, self.record)

    def record(self):
        if self.recording:
            data = self.stream.read(1024)
            self.frames.append(data)
            self.root.after(10, self.record)

    def stop_recording(self):
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()

        with wave.open(self.file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))

        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)

    def play_audio(self):
        audio_output_file = self.translator.output(self.file_path)

        # Playing the translated audio
        audio = AudioSegment.from_mp3(audio_output_file)
        temp_file_path = "output_temp.wav"
        audio.export(temp_file_path, format="wav")

        wf = wave.open(temp_file_path, 'rb')
        stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        wf.close()

        os.remove(temp_file_path)

    def change_language(self):
        new_language = tk.simpledialog.askstring("Change Language", "Enter new target language:")
        if new_language:
            self.translator.target_language = new_language

    def on_closing(self):
        self.audio.terminate()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
