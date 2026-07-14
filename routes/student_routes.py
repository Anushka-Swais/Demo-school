from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from controllers.student_controller import StudentAIController

router = APIRouter()
student_controller = StudentAIController()

# --- Schemas ---
class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TTSRequest(BaseModel):
    text: str
    language_code: str = "en-US"

class ContentRequest(BaseModel):
    topic: str
    learning_capacity: str  # e.g., 'beginner', 'intermediate', 'advanced', or 'visual learner'

class QuizRequest(BaseModel):
    topic: str
    difficulty: str
    num_questions: int = 5

class QuizEvaluationRequest(BaseModel):
    submission_data: dict  # The questions, the correct answers, and the student's selected answers

class SelfAssessmentRequest(BaseModel):
    performance_data: dict # Subject scores and historical data

class AlertRequest(BaseModel):
    assignment_name: str
    due_date: str

# --- Endpoints ---
@router.post("/translate")
async def translate_script(req: TranslationRequest):
    try:
        return {"status": "success", "translated_text": student_controller.translate_text(req.text, req.target_language)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-voice")
async def text_to_voice(req: TTSRequest):
    try:
        return {"status": "success", "audio_base64": student_controller.generate_speech(req.text, req.language_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-to-text")
async def voice_to_text(file: UploadFile = File(...), language_code: str = Form("en-US")):
    try:
        audio_bytes = await file.read()
        return {"status": "success", "transcription": student_controller.process_audio_to_text(audio_bytes, language_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-translator")
async def audio_translator(file: UploadFile = File(...), source_lang: str = Form("en-US"), target_lang_code: str = Form(...)):
    try:
        audio_bytes = await file.read()
        return {"status": "success", "data": student_controller.audio_language_translator(audio_bytes, source_lang, target_lang_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content/generate")
async def generate_content(req: ContentRequest):
    try:
        content = student_controller.generate_content(req.topic, req.learning_capacity)
        return {"status": "success", "generated_content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz/generate")
async def generate_quiz(req: QuizRequest):
    try:
        quiz = student_controller.generate_quiz(req.topic, req.difficulty, req.num_questions)
        return {"status": "success", "quiz_data": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quiz/evaluate")
async def evaluate_quiz(req: QuizEvaluationRequest):
    try:
        evaluation = student_controller.evaluate_quiz(req.model_dump())
        return {"status": "success", "evaluation_report": evaluation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess/self")
async def self_assessment(req: SelfAssessmentRequest):
    try:
        assessment = student_controller.assess_self_performance(req.model_dump())
        return {"status": "success", "assessment_report": assessment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/generate")
async def generate_alert(req: AlertRequest):
    try:
        alert_msg = student_controller.generate_assignment_alert(req.assignment_name, req.due_date)
        return {"status": "success", "alert_message": alert_msg}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))