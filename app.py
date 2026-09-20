"""
Kuralix — Main FastAPI Application
Run: uvicorn app:app --reload
Open: http://localhost:8000
"""

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from modules.asr import transcribe_audio
from modules.extractor import extract_fields
from modules.mapper import map_to_form
from modules import storage

app = FastAPI(title="Kuralix")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

storage.init_db()


class CorrectionRequest(BaseModel):
    submission_id: int
    field_id: str
    original_value: str
    corrected_value: str


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/transcribe")
async def api_transcribe(audio: UploadFile = File(...), language: str = Form("hi")):
    file_path = os.path.join(UPLOAD_DIR, audio.filename or "recording.wav")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    asr_result = transcribe_audio(file_path, language=language)

    if not asr_result.get("text"):
        return JSONResponse({
            "success": False,
            "error": asr_result.get("error", "Could not transcribe audio."),
            "asr": asr_result,
        })

    extracted = extract_fields(asr_result["text"])
    mapped = map_to_form(extracted)
    sid = storage.save_submission(language, asr_result["text"], mapped)

    return JSONResponse({
        "success": True,
        "submission_id": sid,
        "asr": asr_result,
        "extracted": extracted,
        "mapped": mapped,
    })


@app.post("/api/correct")
async def api_correct(req: CorrectionRequest):
    storage.save_correction(req.submission_id, req.field_id,
                            req.original_value, req.corrected_value)
    return {"success": True}


@app.get("/api/pending-sync")
async def api_pending_sync():
    pending = storage.get_pending_sync()
    return {"pending_count": len(pending), "submissions": pending}


@app.post("/api/sync/{submission_id}")
async def api_sync(submission_id: int):
    storage.mark_synced(submission_id)
    return {"success": True}


@app.get("/api/stats")
async def api_stats():
    return {"corrections": storage.get_correction_stats()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)