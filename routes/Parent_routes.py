from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from controllers.parent_controller import ParentAIController
from routes.admin_routes import TranslationRequest, TTSRequest 

router = APIRouter()
parent_ai = ParentAIController()

class AssessmentSummaryRequest(BaseModel):
    student_name: str
    subject: str
    test_name: str
    marks_obtained: float
    total_marks: float
    teacher_remarks: str

class DueDateAlertRequest(BaseModel):
    student_name: str
    assignment_title: str
    subject: str
    due_date: str
    description: str

@router.post("/assessment-summary")
async def get_assessment_summary(req: AssessmentSummaryRequest):
    try:
        summary = parent_ai.generate_assessment_summary(
            student_name=req.student_name,
            subject=req.subject,
            test_name=req.test_name,
            marks_obtained=req.marks_obtained,
            total_marks=req.total_marks,
            teacher_remarks=req.teacher_remarks
        )
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/due-date-alert")
async def get_due_date_alert(req: DueDateAlertRequest):
    try:
        alert_text = parent_ai.generate_due_date_alert(
            student_name=req.student_name,
            assignment_title=req.assignment_title,
            subject=req.subject,
            due_date=req.due_date,
            description=req.description
        )
        return {"status": "success", "alert_text": alert_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate")
async def parent_translate(req: TranslationRequest):
    try:
        result = parent_ai.translate_text(req.text, req.target_language)
        return {"status": "success", "translated_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-voice")
async def parent_text_to_voice(req: TTSRequest):
    try:
        audio_base64 = parent_ai.generate_speech(req.text, req.language)
        return {"status": "success", "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-to-text")
async def parent_voice_to_text(file: UploadFile = File(...), language: str = Form("English")):
    try:
        audio_bytes = await file.read()
        transcription = parent_ai.process_audio_to_text(audio_bytes, language)
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-translator")
async def parent_audio_translator(
    file: UploadFile = File(...),
    source_language: str = Form("English"),
    target_language: str = Form(...)
):
    try:
        audio_bytes = await file.read()
        result = parent_ai.audio_language_translator(audio_bytes, source_language, target_language)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))