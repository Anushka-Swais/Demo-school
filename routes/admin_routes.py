from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from controllers.admin_controller import AdminAIController

router = APIRouter()
ai_controller = AdminAIController()

class TranslationRequest(BaseModel):
    text: str
    target_language: str

class TTSRequest(BaseModel):
    text: str
    # Changed from language_code to language, and default to English
    language: str = "English"

@router.post("/translate")
async def translate_script(req: TranslationRequest):
    try:
        result = ai_controller.translate_text(req.text, req.target_language)
        return {"status": "success", "translated_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-voice")
async def text_to_voice(req: TTSRequest):
    try:
        # Pass the plain language name (e.g., 'Hindi') to the controller
        audio_base64 = ai_controller.generate_speech(req.text, req.language)
        return {"status": "success", "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-to-text")
async def voice_to_text(
    file: UploadFile = File(...),
    # Changed to language and Form("English")
    language: str = Form("English")
):
    try:
        audio_bytes = await file.read()
        transcription = ai_controller.process_audio_to_text(audio_bytes, language)
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-translator")
async def audio_translator(
    file: UploadFile = File(...),
    # Cleaned up the form names so the frontend just sends language names
    source_language: str = Form("English"),
    target_language: str = Form(...) 
):
    try:
        audio_bytes = await file.read()
        result = ai_controller.audio_language_translator(audio_bytes, source_language, target_language)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))