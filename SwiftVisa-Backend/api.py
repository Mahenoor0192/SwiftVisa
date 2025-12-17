from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import inference_with_gemini
run_rag_for_query = inference_with_gemini.run_rag_for_query

app = FastAPI()   # 👈 THIS MUST EXIST

class UserProfile(BaseModel):
    age: str
    nationality: str
    education: str
    employment: str
    income: str
    visa_type: str
    extra: Dict[str, Any]

@app.post("/evaluate")
def evaluate(profile: UserProfile):
    query = f"{profile.visa_type} visa requirements for {profile.nationality}"
    result = run_rag_for_query(profile.dict(), query)
    return result
