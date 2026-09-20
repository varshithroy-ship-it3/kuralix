"""
Kuralix ASR v3 — Auto language detection + audio preprocessing.
"""

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import speech_recognition as sr

FFMPEG_PATH = r"C:\Users\musal\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"

LANG_MAP = {
    "hi": "hi-IN",
    "mr": "mr-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "en": "en-IN",
}
ALL_LANGS = list(LANG_MAP.keys())

# Script ranges for scoring
SCRIPT_RANGES = {
    "hi": (0x0900, 0x097F),   # Devanagari
    "mr": (0x0900, 0x097F),   # Devanagari (Marathi)
    "ta": (0x0B80, 0x0BFF),   # Tamil
    "te": (0x0C00, 0x0C7F),   # Telugu
    "en": (0x0041, 0x007A),   # Latin
}


def _ensure_wav(audio_path: str) -> str:
    """Convert webm/opus → clean 16 kHz mono WAV with preprocessing."""
    try:
        with open(audio_path, "rb") as f:
            header = f.read(4)
        if header == b"RIFF":
            return audio_path
    except Exception:
        pass

    out_path = os.path.splitext(audio_path)[0] + "_converted.wav"
    cmd = [
        FFMPEG_PATH, "-y",
        "-i", audio_path,
        "-ac", "1",
        "-ar", "16000",
        # Preprocessing: high-pass (remove rumble) + loudness normalize
        "-af", "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-f", "wav",
        out_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path


def _transcribe_one(wav_path: str, lang_code: str) -> dict:
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    try:
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=lang_code)
        return {"lang": lang_code, "text": text, "error": None}
    except sr.UnknownValueError:
        return {"lang": lang_code, "text": "", "error": "unknown"}
    except sr.RequestError as e:
        return {"lang": lang_code, "text": "", "error": f"request: {e}"}
    except Exception as e:
        return {"lang": lang_code, "text": "", "error": str(e)}


def _script_bonus(text: str, lang_code: str) -> int:
    """Score text by how many chars belong to the expected script."""
    if lang_code not in SCRIPT_RANGES:
        return 0
    lo, hi = SCRIPT_RANGES[lang_code]
    count = 0
    for c in text:
        if lo <= ord(c) <= hi:
            count += 1
    return min(count, 60)  # cap


def _score(text: str, lang_code: str) -> int:
    """Higher score = better candidate."""
    if not text:
        return 0
    score = 0
    try:
        from modules.extractor import extract_fields
        fields = extract_fields(text)
        score += len(fields) * 40
    except Exception:
        pass
    score += _script_bonus(text, lang_code)
    score += min(len(text.split()), 20) * 2
    return score


def transcribe_audio(audio_path: str, language: str = None) -> dict:
    try:
        wav_path = _ensure_wav(audio_path)
    except Exception as e:
        return {"text": "", "language": "auto", "confidence": 0.0,
                "error": f"Audio conversion failed: {e}"}

    results = []
    with ThreadPoolExecutor(max_workers=len(ALL_LANGS)) as pool:
        futures = {pool.submit(_transcribe_one, wav_path, LANG_MAP[lc]): lc
                   for lc in ALL_LANGS}
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception:
                pass

    candidates = [r for r in results if r.get("text")]
    if not candidates:
        err = results[0]["error"] if results else "no results"
        return {"text": "", "language": "auto", "confidence": 0.0,
                "error": f"Could not understand audio ({err})"}

    scored = []
    for r in candidates:
        lc = r["lang"].split("-")[0]
        scored.append((r, _score(r["text"], lc)))
    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[0][0]

    return {
        "text": best["text"],
        "language": best["lang"],
        "confidence": 0.85,
        "candidates": [{"lang": r["lang"], "text": r["text"], "score": s}
                       for r, s in scored],
    }