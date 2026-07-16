import os
import base64
import json
from google.cloud import texttospeech
from google.cloud import speech
from google.api_core.client_options import ClientOptions

# --- NEW: Import your centralized AI config! ---
from config.ai_config import client, model_name

class StudentAIController:
    def __init__(self):
        # We NO LONGER initialize Gemini here. It is handled globally by ai_config.py!
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
        prompt = f"Translate the following text to {target_language}. Provide only the translation:\n\n{text}"
        
        # --- NEW: Using the global client and model_name ---
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def generate_speech(self, text: str, language: str = "English") -> str:
        lang_code = self._get_lang_code(language)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=lang_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = self.tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        return base64.b64encode(response.audio_content).decode("utf-8")

    def process_audio_to_text(self, audio_bytes: bytes, language: str = "English") -> str:
        lang_code = self._get_lang_code(language)
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, language_code=lang_code)
        response = self.stt_client.recognize(config=config, audio=audio)
        return " ".join([result.alternatives[0].transcript for result in response.results])

    def audio_language_translator(self, audio_bytes: bytes, source_language: str, target_language: str) -> dict:
        original_text = self.process_audio_to_text(audio_bytes, source_language)
        translated_text = self.translate_text(original_text, target_language)
        translated_audio_base64 = self.generate_speech(translated_text, target_language)
        return {"original_text": original_text, "translated_text": translated_text, "audio_base64": translated_audio_base64}

    # --- GENERATIVE LEARNING FEATURES ---
    def generate_content(self, topic: str, learning_capacity: str) -> str:
        prompt = f"""
        Act as an encouraging, expert tutor. Generate educational content on the topic: '{topic}'.
        The content must be tailored for a student with a '{learning_capacity}' learning capacity.
        Make it engaging, easy to understand, and structured with bullet points or short paragraphs.
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def generate_quiz(self, topic: str, difficulty: str, num_questions: int) -> str:
        prompt = f"""
        Generate a multiple-choice mock test/quiz with {num_questions} questions on the topic: '{topic}'.
        The difficulty level should be: '{difficulty}'.
        Return the response in a structured JSON format with 'question', 'options' (array), and 'correct_answer'.
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def evaluate_quiz(self, quiz_data: dict) -> str:
        prompt = f"""
        Act as an encouraging tutor. Evaluate the following student quiz submission.
        Identify which questions they got right and wrong, and provide a brief, helpful explanation for the incorrect answers.
        
        Submission Data:
        {quiz_data}
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def assess_self_performance(self, performance_data: dict) -> str:
        prompt = f"""
        Analyze the following student performance data (grades across subjects).
        Write a supportive self-assessment report directed at the student. Point out their strongest subjects, 
        gently identify areas for growth, and give them 3 actionable study tips.
        
        Performance Data:
        {performance_data}
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def generate_assignment_alert(self, assignment_name: str, due_date: str) -> str:
        prompt = f"""
        Write a brief, friendly, and motivating alert message for a student reminding them that 
        their assignment '{assignment_name}' is due on {due_date}. 
        Keep it under 3 sentences and highly encouraging.
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()