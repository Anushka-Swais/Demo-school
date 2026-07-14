import os
import base64
import google.generativeai as genai
from google.cloud import texttospeech
from google.cloud import speech
from google.api_core.client_options import ClientOptions

class HMAIController:
    def __init__(self):
        # 1. Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")
        genai.configure(api_key=api_key)
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.ai_model = genai.GenerativeModel(model_name)

        # 2. Initialize GCP Clients
        gcp_key = os.getenv("GOOGLE_TTS_API_KEY")
        if not gcp_key:
             raise ValueError("GOOGLE_TTS_API_KEY is missing from environment variables.")
             
        client_options = ClientOptions(api_key=gcp_key)
        self.tts_client = texttospeech.TextToSpeechClient(client_options=client_options)
        self.stt_client = speech.SpeechClient(client_options=client_options)

    # --- SHARED COMMUNICATION FEATURES (Req 1, 2, 3) ---
    def translate_text(self, text: str, target_language: str) -> str:
        prompt = f"Translate the following text to {target_language}. Provide only the translation:\n\n{text}"
        return self.ai_model.generate_content(prompt).text.strip()

    def generate_speech(self, text: str, language_code: str = "en-US") -> str:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = self.tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        return base64.b64encode(response.audio_content).decode("utf-8")

    def process_audio_to_text(self, audio_bytes: bytes, language_code: str = "en-US") -> str:
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, language_code=language_code)
        response = self.stt_client.recognize(config=config, audio=audio)
        return " ".join([result.alternatives[0].transcript for result in response.results])

    def audio_language_translator(self, audio_bytes: bytes, source_lang: str, target_lang: str) -> dict:
        original_text = self.process_audio_to_text(audio_bytes, source_lang)
        translated_text = self.translate_text(original_text, target_lang)
        translated_audio_base64 = self.generate_speech(translated_text, target_lang)
        return {"original_text": original_text, "translated_text": translated_text, "audio_base64": translated_audio_base64}

    # --- NEW GENERATIVE ANALYTICS FEATURES (Req 4, 5) ---
    def assess_student(self, student_data: dict) -> str:
        prompt = f"""
        Act as an expert Head Master. Analyze the following student performance data. 
        Provide a comprehensive, encouraging, but objective assessment report. 
        Highlight their strengths, identify areas for improvement, and suggest actionable advice.
        
        Student Data:
        {student_data}
        """
        response = self.ai_model.generate_content(prompt)
        return response.text.strip()

    def assess_classroom(self, classroom_data: dict) -> str:
        prompt = f"""
        Act as an expert Head Master. Analyze the following macro-level classroom performance data.
        Provide an overall assessment of the class's performance. Identify specific subjects where the class excels 
        and subjects that require pedagogical attention or teacher intervention.
        
        Classroom Data:
        {classroom_data}
        """
        response = self.ai_model.generate_content(prompt)
        return response.text.strip()