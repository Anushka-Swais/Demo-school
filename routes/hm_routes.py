from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from controllers.hm_controller import HMAIController

router = APIRouter()
hm_controller = HMAIController()

# --- Schemas ---
class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TTSRequest(BaseModel):
    text: str
    language_code: str = "en-US"

class StudentAssessmentRequest(BaseModel):
    student_name: str
    metrics: dict  # The other dev will send grades, attendance, etc. here

class ClassroomAssessmentRequest(BaseModel):
    class_name: str
    metrics: dict  # The other dev will send class averages, subject scores, etc. here

# --- Endpoints ---
@router.post("/translate")
async def translate_script(req: TranslationRequest):
    try:
        return {"status": "success", "translated_text": hm_controller.translate_text(req.text, req.target_language)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-voice")
async def text_to_voice(req: TTSRequest):
    try:
        return {"status": "success", "audio_base64": hm_controller.generate_speech(req.text, req.language_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-to-text")
async def voice_to_text(file: UploadFile = File(...), language_code: str = Form("en-US")):
    try:
        audio_bytes = await file.read()
        return {"status": "success", "transcription": hm_controller.process_audio_to_text(audio_bytes, language_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-translator")
async def audio_translator(file: UploadFile = File(...), source_lang: str = Form("en-US"), target_lang_code: str = Form(...)):
    try:
        audio_bytes = await file.read()
        return {"status": "success", "data": hm_controller.audio_language_translator(audio_bytes, source_lang, target_lang_code)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess/student")
async def generate_student_assessment(req: StudentAssessmentRequest):
    try:
        # Pass the raw dictionary data directly to Gemini for analysis
        assessment_text = hm_controller.assess_student(req.model_dump())
        return {"status": "success", "assessment_report": assessment_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess/classroom")
async def generate_classroom_assessment(req: ClassroomAssessmentRequest):
    try:
        assessment_text = hm_controller.assess_classroom(req.model_dump())
        return {"status": "success", "assessment_report": assessment_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))