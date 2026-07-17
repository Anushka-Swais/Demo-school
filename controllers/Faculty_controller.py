import os
import base64
from google.cloud import texttospeech
from google.cloud import speech
from google.api_core.client_options import ClientOptions

# Import your centralized AI config
from config.ai_config import client, model_name

class FacultyAIController:
    def __init__(self):
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

    # --- GENERATIVE FACULTY FEATURES ---
    def generate_lesson_plan(self, topic: str, grade_level: str, duration: str) -> str:
        prompt = f"""
        Act as an expert curriculum designer. Generate a comprehensive lesson plan for the topic '{topic}' 
        tailored for {grade_level} students. The lesson duration is {duration}.
        Include:
        1. Learning Objectives
        2. Core Concept Explanation
        3. Classroom Activity/Interactive Element
        4. Assessment Method
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()

    def generate_quiz_for_class(self, topic: str, difficulty: str, format_type: str, num_questions: int) -> str:
        # NEW: Forcing a strict JSON schema guarantees all question types are generated
        prompt = f"""
        Act as an expert curriculum designer and teacher. 
        Generate a {difficulty} level comprehensive exam paper on the topic '{topic}'.
        
        CRITICAL INSTRUCTION: You MUST divide the {num_questions} total questions across four specific formats. 
        You MUST return the output STRICTLY as a valid JSON object matching the exact schema below. Do not include markdown formatting like ```json.
        
        {{
            "exam_title": "{topic} - {difficulty} Exam",
            "total_questions_requested": {num_questions},
            "sections": {{
                "mcq": [
                    {{ "type": "Quiz/MCQ", "question": "...", "options": ["...", "...", "...", "..."], "correct_answer": "..." }}
                ],
                "true_false": [
                    {{ "type": "True/False", "question": "...", "correct_answer": "True or False" }}
                ],
                "short_answer": [
                    {{ "type": "Short Question", "question": "...", "answer_key": "Brief expected answer..." }}
                ],
                "long_answer": [
                    {{ "type": "Long Question", "question": "...", "grading_rubric": "Key points to look for..." }}
                ]
            }}
        }}
        
        Ensure you populate every array with at least one question, and the total number of questions across all arrays must equal {num_questions}.
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        # We strip out any stray markdown formatting the AI might try to wrap the JSON in
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        return clean_response

    def generate_assignment(self, topic: str, grade_level: str, instructions: str) -> str:
        prompt = f"""
        Create a homework assignment for {grade_level} students on the topic of '{topic}'.
        Additional instructions/requirements from the teacher: {instructions}
        Make the assignment engaging and clear.
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()
        
    def draft_student_feedback(self, student_name: str, performance_notes: str, tone: str = "encouraging") -> str:
        prompt = f"""
        Draft professional and {tone} feedback for a student named {student_name} based on these notes:
        {performance_notes}
        The feedback should be constructive, highlighting strengths and gently addressing areas for improvement.
        """
        response = client.models.generate_content(model=model_name, contents=prompt)
        return response.text.strip()