import os
import base64
import json
from google.cloud import texttospeech
from google.cloud import speech
from google.api_core.client_options import ClientOptions

# --- NEW: Import your centralized AI config! ---
from config.ai_config import client, model_name 

class AdminAIController:
    def __init__(self):
        # We NO LONGER initialize Gemini here. It is handled globally!
        # We only need to initialize Google Cloud Voice for TTS/STT.
        
        gcp_key = os.getenv("GOOGLE_TTS_API_KEY")
        if not gcp_key:
             raise ValueError("GOOGLE_TTS_API_KEY is missing from environment variables.")
             
        client_options = ClientOptions(api_key=gcp_key)
        self.tts_client = texttospeech.TextToSpeechClient(client_options=client_options)
        self.stt_client = speech.SpeechClient(client_options=client_options)

        self.language_map = {
            "english": "en-IN", "hindi": "hi-IN", "telugu": "te-IN",
            "kannada": "kn-IN", "tamil": "ta-IN", "gujrati": "gu-IN", 
            "gujarati": "gu-IN", "marathi": "mr-IN", "panjabi": "pa-IN", "punjabi": "pa-IN"
        }

    def _get_lang_code(self, language_name: str) -> str:
        lang_lower = language_name.lower().strip()
        return self.language_map.get(lang_lower, language_name if "-" in language_name else "en-US")

    # --- SHARED COMMUNICATION FEATURES ---
    def translate_text(self, text: str, target_language: str) -> str:
        prompt = f"Translate the following text to {target_language}. Provide only the translation, without any markdown formatting or extra text:\n\n{text}"
        
        # --- NEW: Using the global client and model_name ---
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def generate_speech(self, text: str, language: str = "English") -> str:
        lang_code = self._get_lang_code(language)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code, 
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        return base64.b64encode(response.audio_content).decode("utf-8")

    def process_audio_to_text(self, audio_bytes: bytes, language: str = "English") -> str:
        lang_code = self._get_lang_code(language)
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=lang_code,
        )
        
        response = self.stt_client.recognize(config=config, audio=audio)
        
        transcription = " ".join([result.alternatives[0].transcript for result in response.results])
        return transcription

    def audio_language_translator(self, audio_bytes: bytes, source_language: str, target_language: str) -> dict:
        original_text = self.process_audio_to_text(audio_bytes, source_language)
        translated_text = self.translate_text(original_text, target_language)
        translated_audio_base64 = self.generate_speech(translated_text, target_language)
        
        return {
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_base64": translated_audio_base64
        }

    # --- GENERATIVE ADMIN FEATURES ---
    def draft_official_communication(self, context: str, audience: str, tone: str) -> str:
        prompt = f"""
        Act as a professional school administrator. Draft an official communication based on the following:
        Context: {context}
        Target Audience: {audience}
        Desired Tone: {tone}
        
        Keep the message clear, concise, and professionally formatted.
        """
        
        # --- NEW: Using the global client and model_name ---
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def generate_policy_summary(self, policy_document_text: str) -> str:
        prompt = f"""
        Summarize the following school policy document into a clear, easily understandable format for staff and parents.
        Highlight the most critical rules, procedures, and any consequences. Use bullet points for readability.
        
        Policy Text: {policy_document_text}
        """
        
        # --- NEW: Using the global client and model_name ---
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()