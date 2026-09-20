# Kuralix

**Voice-Based Form Filling for Indian Regional Languages**

Built by **Team ARAIVA** — P. Chaitra, M. Varshith  
Dayananda Sagar University

Built for **Neuromorphix 2026**, Problem CS06 — *AI in Daily Lives*

---

## What it does

Kuralix is a voice-first web assistant that lets users fill health forms by speaking naturally in **Hindi, Marathi, Tamil, Telugu, or English** — including code-mixing (Hinglish, Tanglish, etc.).

1. User speaks into the browser
2. Speech is transcribed via Google Speech Recognition (auto language detection)
3. NLP extracts structured fields: Name, Age, Gender, Village, Symptoms, Phone
4. Form is auto-filled with per-field confidence scores
5. Low-confidence fields are flagged for human review
6. Corrections are saved to SQLite for a continuous feedback loop

## Features

- 🎤 **Auto language detection** across 5 Indian languages
- 🧠 **Multi-lingual NLP** — keyword + fuzzy matching for all 5 languages simultaneously
- 📊 **Confidence scoring** per field with visual review flags
- ✏️ **Human-in-the-loop corrections** saved for improvement
- 💾 **Offline-first** storage (SQLite)
- 🖥️ **Runs on low-end Android/PC** — lightweight, no heavy ML deps

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Frontend | HTML, CSS, vanilla JavaScript (Jinja2 templates) |
| Speech-to-Text | Google Web Speech API (free) via SpeechRecognition |
| Audio Processing | FFmpeg (WebM/Opus → 16 kHz mono WAV) |
| NLP | Regex + RapidFuzz fuzzy matching |
| Storage | SQLite |

## Setup

```bash
git clone https://github.com/varshithroy-ship-it3/kuralix.git
cd kuralix
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
Install FFmpeg and ensure it's on PATH.

Run:

bash
uvicorn app:app --reload
Open http://localhost:8000 in Chrome. Allow microphone access when prompted.

How to Use
Click the 🎤 button and speak naturally, e.g.:

"Mera naam Sunita Patil hai, umar battis, gaon Pune, mujhe bukhar aur khansi hai"

The form auto-fills with extracted fields

Green badges = high confidence, yellow/red = needs review

Edit any incorrect fields

Click Submit — corrections are logged for future improvement

Team
ARAIVA — P. Chaitra, M. Varshith
Dayananda Sagar University — 2026

text

**Scroll down**, click **Commit changes...**, then **Commit changes** again to confirm.

## Final step — verify README appears

Refresh the GitHub page. You should see the formatted README rendered below the file list.

---

## ✅ What's done

| Item | Status |
|---|---|
| Code working locally | ✅ |
| All 5 languages extract correctly | ✅ |
| GitHub repo created | ✅ |
| Initial commit pushed | ✅ |
| README | ⏳ paste now |

Once README is committed, you're **100% done with the repo side**. Then we move to the **PPT + demo prep** — that's what's left for the hackathon round.
