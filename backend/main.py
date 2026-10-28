from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai_review import review_with_ai
from er_validator import validate
from file_ingest import ingest
from question_bank import QUESTIONS
from quiz import generate_quiz

app = FastAPI(title="AI-Based ER Diagram Validator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------- upload (any file) + rule-based validation ----------

_CHECK = "Check that the Table Summary below matches your diagram before trusting the results."
NOTICES = {
    "ai-image": "This diagram was read from your image by AI. " + _CHECK,
    "ai-pdf": "This diagram was read from your PDF by AI. " + _CHECK,
    "ai-office": "This diagram was read from your document by AI. " + _CHECK,
    "ai-text": "This diagram was read from your text file by AI. " + _CHECK,
    "ai-drawio": "This draw.io file does not use table shapes, so the AI interpreted its shapes. " + _CHECK,
}


@app.post("/upload")
@app.post("/api/upload")
def upload_diagram(file: UploadFile = File(...)):
    # a plain def (not async) so slow AI calls run in a worker thread and don't block the server
    raw = file.file.read()

    try:
        model, info = ingest(file.filename, raw)
    except RuntimeError as e:  # e.g. missing GEMINI_API_KEY
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:  # empty / too large / unreadable / no diagram in it
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Could not read the file: {e}")

    validation = validate(model)

    return {
        "message": (
            f"Parsed {len(model['entities'])} tables and "
            f"{len(model['relationships'])} relationships."
        ),
        "source": info["source"],
        "file_type": info["file_type"],
        "notice": NOTICES.get(info["source"]),
        "notation": model.get("notation"),
        "entities": model["entities"],
        "relationships": model["relationships"],
        "validation": validation,
    }


# ---------- AI review of the diagram ----------

class AIReviewRequest(BaseModel):
    diagram: dict
    rule_results: dict = {}


@app.post("/api/ai-review")
def ai_review(req: AIReviewRequest):
    try:
        issues = review_with_ai(req.diagram, req.rule_results)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI review failed: {e}")
    return {"issues": issues, "issue_count": len(issues)}


# ---------- quiz (AI generated) ----------

class QuizRequest(BaseModel):
    count: int = Field(5, ge=1, le=20)
    difficulty: Literal["Easy", "Medium", "Hard"] = "Easy"


@app.post("/api/quiz")
def quiz(req: QuizRequest):
    questions, source = generate_quiz(req.count, req.difficulty)
    return {"questions": questions, "source": source, "count": len(questions)}


# ---------- competitive exam questions ----------

@app.get("/api/competitive")
def competitive():
    return {"count": len(QUESTIONS), "questions": QUESTIONS}
