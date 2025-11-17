# config.py
FILE_PATH = "myans.txt"
ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
CHARACTER_SUBSTITUTIONS = {"a": "а", "o": "о", "а": "a", "о": "o"}

# file_parser.py
from fastapi import UploadFile, HTTPException
import logging

async def parse_answers_file(file_path: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = {}
            current_question = None
            for line in file:
                line = line.strip()
                if line.startswith("~"):
                    continue  # Skip incorrect answers
                if line.endswith("+"):
                    current_question = line[:-1]  # Remove '+'
                    data[current_question] = []
                elif current_question:
                    data[current_question].append(line)
            return data
    except FileNotFoundError:
        logging.error(f"File {file_path} not found")
        raise HTTPException(status_code=500, detail="Answer file not found")
    except Exception as e:
        logging.error(f"Error parsing file: {e}")
        raise HTTPException(status_code=500, detail="Error parsing answer file")

# question_processor.py
from typing import List

def generate_question_variants(question: str, substitutions: dict) -> List[str]:
    variants = [question]
    for char, sub in substitutions.items():
        if char in question:
            variants.append(question.replace(char, sub))
    return variants

# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from file_parser import parse_answers_file
from question_processor import generate_question_variants
from config import FILE_PATH, ALLOWED_ORIGINS, CHARACTER_SUBSTITUTIONS

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def load_data():
    app.state.answers_data = await parse_answers_file(FILE_PATH)

@app.get("/test")
async def get_answer(quest: str = Query(..., min_length=1)):
    if not quest:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    variants = generate_question_variants(quest, CHARACTER_SUBSTITUTIONS)
    for variant in variants:
        if variant in app.state.answers_data:
            return {"answers": app.state.answers_data[variant]}

    raise HTTPException(status_code=404, detail="Question not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
