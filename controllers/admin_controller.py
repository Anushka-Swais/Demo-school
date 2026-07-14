import os
import base64
import google.generativeai as genai
from google.cloud import texttospeech
from google.cloud import speech
from google.api_core.client_options import ClientOptions

class AdminAIController:
    def __init__(self):
        # 1. Initialize Gemini API Key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")
        genai.configure(api_key=api_key)
        
        # 2. Dynamically load the model strictly from .env (No hardcoding)
        model_name = os.getenv("GEMINI_MODEL")
        if not model_name:
            raise ValueError("GEMINI_MODEL is missing from environment variables.")
        
        self.vision_model = genai.GenerativeModel(model_name)

        # 3. Initialize GCP Clients using the API Key string
        gcp_key = os.getenv("GOOGLE_TTS_API_KEY")
        if not gcp_key:
             raise ValueError("GOOGLE_TTS_API_KEY is missing from environment variables.")
             
        client_options = ClientOptions(api_key=gcp_key)
        
        self.tts_client = texttospeech.TextToSpeechClient(client_options=client_options)
        self.stt_client = speech.SpeechClient(client_options=client_options)

    def translate_text(self, text: str, target_language: str) -> str:
        prompt = f"Translate the following text to {target_language}. Provide only the translation, no extra commentary:\n\n{text}"
        response = self.vision_model.generate_content(prompt)
        return response.text.strip()

    def generate_speech(self, text: str, language_code: str = "en-US") -> str:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # Return base64 encoded audio string
        return base64.b64encode(response.audio_content).decode("utf-8")

    def process_audio_to_text(self, audio_bytes: bytes, language_code: str = "en-US") -> str:
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language_code,
        )
        
        response = self.stt_client.recognize(config=config, audio=audio)
        
        transcription = " ".join([result.alternatives[0].transcript for result in response.results])
        return transcription

    def audio_language_translator(self, audio_bytes: bytes, source_lang: str, target_lang: str) -> dict:
        # Step 1: Voice to Text
        original_text = self.process_audio_to_text(audio_bytes, source_lang)
        
        # Step 2: Translate Text
        translated_text = self.translate_text(original_text, target_lang)
        
        # Step 3: Text to Voice
        translated_audio_base64 = self.generate_speech(translated_text, target_lang)
        
        return {
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_base64": translated_audio_base64
        }