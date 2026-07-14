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
    language_code: str = "en-US"

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
        audio_base64 = ai_controller.generate_speech(req.text, req.language_code)
        return {"status": "success", "audio_base64": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-to-text")
async def voice_to_text(
    file: UploadFile = File(...),
    language_code: str = Form("en-US")
):
    try:
        audio_bytes = await file.read()
        transcription = ai_controller.process_audio_to_text(audio_bytes, language_code)
        return {"status": "success", "transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audio-translator")
async def audio_translator(
    file: UploadFile = File(...),
    source_lang: str = Form("en-US"),
    target_lang_code: str = Form(...) # e.g., 'es-ES' for Spanish
):
    try:
        audio_bytes = await file.read()
        result = ai_controller.audio_language_translator(audio_bytes, source_lang, target_lang_code)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))