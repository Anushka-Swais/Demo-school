from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from controllers.teacher_controller import TeacherAIController

router = APIRouter()
teacher_controller = TeacherAIController()

# --- Schemas ---
class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TTSRequest(BaseModel):
    text: str
    language_code: str = "en-US"

class MaterialRequest(BaseModel):
    topic: str
    grade_level: str

class QuestionPaperRequest(BaseModel):
    topic: str
    difficulty: str
    format_type: str
    num_questions: int

class AutoCorrectRequest(BaseModel):
    question: str
    student_answer: str
    rubric: str

class AlertRequest(BaseModel):
    alert_type: str # "due_date" or "completion"
    details: dict # e.g., {"assignment_name": "Math Homework", "due_date": "Friday", "student_name": "John"}

class AssessmentRequest(BaseModel):
    scope_description: str # e.g., "Class 10A Science" or "John Doe All Subjects"
    performance_data: dict

# --- Endpoints ---
@router.post("/translate")
async def translate_script(req: TranslationRequest):
    try:
        return {"status": "success", "translated_text": teacher_controller.translate_text(req.text, req.target_language)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-voice")
async def text_to_voice(req: TTSRequest):
    try:
        return {"status": "success", "audio_base64": teacher_controller.generate_speech(req.text, req.language_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-to-text")
async def voice_to_text(file: UploadFile = File(...), language_code: str = Form("en-US")):
    try:
        audio_bytes = await file.read()
        return {"status": "success", "transcription": teacher_controller.process_audio_to_text(audio_bytes, language_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-translator")
async def audio_translator(file: UploadFile = File(...), source_lang: str = Form("en-US"), target_lang_code: str = Form(...)):
    try:
        audio_bytes = await file.read()
        return {"status": "success", "data": teacher_controller.audio_language_translator(audio_bytes, source_lang, target_lang_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-material")
async def generate_material(req: MaterialRequest):
    try:
        material = teacher_controller.generate_teaching_material(req.topic, req.grade_level)
        return {"status": "success", "teaching_material": material}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-exam")
async def generate_exam(req: QuestionPaperRequest):
    try:
        exam = teacher_controller.generate_question_paper(req.topic, req.difficulty, req.format_type, req.num_questions)
        return {"status": "success", "question_paper": exam}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auto-correct")
async def auto_correct(req: AutoCorrectRequest):
    try:
        feedback = teacher_controller.auto_correct_answer(req.question, req.student_answer, req.rubric)
        return {"status": "success", "grading_feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts")
async def generate_alert(req: AlertRequest):
    try:
        alert = teacher_controller.generate_teacher_alert(req.alert_type, req.details)
        return {"status": "success", "alert_message": alert}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess")
async def evaluate_performance(req: AssessmentRequest):
    try:
        assessment = teacher_controller.evaluate_performance(req.performance_data, req.scope_description)
        return {"status": "success", "assessment_report": assessment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))