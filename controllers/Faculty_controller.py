import os
import base64
from google import genai
from google.cloud import texttospeech
from google.cloud import speech
from google.api_core.client_options import ClientOptions

class FacultyAIController:
    def __init__(self):
        # 1. Initialize Gemini Client (New SDK Standard)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing from environment variables.")
        self.client = genai.Client(api_key=api_key)
        
        # 2. Load model name from environment
        self.model_name = os.getenv("GEMINI_MODEL")
        if not self.model_name:
            raise ValueError("GEMINI_MODEL is missing from environment variables.")

        # 3. Initialize GCP Clients
        gcp_key = os.getenv("GOOGLE_TTS_API_KEY")
        if not gcp_key:
             raise ValueError("GOOGLE_TTS_API_KEY is missing from environment variables.")
             
        client_options = ClientOptions(api_key=gcp_key)
        self.tts_client = texttospeech.TextToSpeechClient(client_options=client_options)
        self.stt_client = speech.SpeechClient(client_options=client_options)

        # 4. Regional Language Mapper for Google Cloud Voice APIs
        self.language_map = {
            "english": "en-IN",
            "hindi": "hi-IN",
            "telugu": "te-IN",
            "kannada": "kn-IN",
            "tamil": "ta-IN",
            "gujrati": "gu-IN", 
            "gujarati": "gu-IN",
            "marathi": "mr-IN",
            "panjabi": "pa-IN",
            "punjabi": "pa-IN"
        }

    def _get_lang_code(self, language_name: str) -> str:
        """Helper to convert friendly names like 'Hindi' into 'hi-IN' for GCP APIs"""
        lang_lower = language_name.lower().strip()
        return self.language_map.get(lang_lower, language_name if "-" in language_name else "en-US")

    # --- SHARED COMMUNICATION FEATURES ---
    def translate_text(self, text: str, target_language: str) -> str:
        prompt = f"Translate the following text to {target_language}. Provide only the translation:\n\n{text}"
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
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

    # --- GENERATIVE TEACHING FEATURES ---
    def generate_teaching_material(self, topic: str, grade_level: str) -> str:
        prompt = f"""
        Act as an expert curriculum designer. Generate comprehensive teaching material and a lesson plan 
        for the topic '{topic}' tailored for {grade_level} students. Include learning objectives, 
        a core concept explanation, and a classroom activity.
        """
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text.strip()

    def generate_question_paper(self, topic: str, difficulty: str, format_type: str, num_questions: int) -> str:
        prompt = f"""
        Generate a {difficulty} level question paper with {num_questions} questions on the topic '{topic}'.
        The format should be {format_type} (e.g., multiple-choice, short answer, essay).
        Provide the questions clearly, and append a detailed answer key at the bottom for the teacher.
        """
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text.strip()

    def auto_correct_answer(self, question: str, student_answer: str, rubric: str) -> str:
        prompt = f"""
        Act as an objective grader. Evaluate the student's answer against the provided rubric/correct answer.
        Question: {question}
        Student Answer: {student_answer}
        Rubric/Correct Answer: {rubric}
        
        Provide a score (e.g., out of 10) and brief, constructive feedback explaining why points were awarded or deducted.
        """
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text.strip()

    # --- ALERT SYSTEMS ---
    def generate_teacher_alert(self, alert_type: str, details: dict) -> str:
        if alert_type == "due_date":
            prompt = f"Draft a brief, polite reminder message from a teacher to students that the assignment '{details.get('assignment_name')}' is due on {details.get('due_date')}."
        elif alert_type == "completion":
            prompt = f"Draft a brief, encouraging notification confirming that the student {details.get('student_name')} has successfully submitted the assignment '{details.get('assignment_name')}'."
        else:
            return "Invalid alert type."
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text.strip()

    # --- ASSESSMENT FEATURES ---
    def evaluate_performance(self, data: dict, scope_description: str) -> str:
        prompt = f"""
        Act as an expert educator. Analyze the following performance data.
        Scope of analysis: {scope_description} (e.g., Single student across all subjects, entire class for one subject).
        
        Data: {data}
        
        Provide a professional evaluation report. Highlight the major strengths, identify specific weaknesses, 
        and suggest pedagogical interventions or next steps.
        """
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text.strip()