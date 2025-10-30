import os
import sys
import json
import time
from typing import List, Dict, Any

# Ensure src is on path so we can import local modules
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, ROOT_DIR)

# Local workspace imports (uses your existing retrieval function)
from rag_inference import retrieve  # -> [src/rag_inference.py]

# Optional: load .env if python-dotenv installed
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ROOT_DIR, ".env"))
except Exception:
    pass

# Try to import google/genai client but tolerate different shapes
GENAI_AVAILABLE = False
try:
    import genai
    GENAI_AVAILABLE = True
except Exception:
    try:
        # older import shape
        from google import genai  # type: ignore
        GENAI_AVAILABLE = True
    except Exception:
        GENAI_AVAILABLE = False

LOG_PATH = os.path.join(BASE_DIR, "logs", "queries_gemini.jsonl")
TEMPLATE_PATH = os.path.join(BASE_DIR, "initial_prompt_template.txt")
TOP_K = int(os.getenv("TOP_K", "5"))


def build_retrieved_context(docs: List[Any], max_excerpt_chars: int = 800) -> (str, List[Dict[str, Any]]):
    """
    Build the retrieved_context string for the prompt and a simple docs_used list for logging.
    """
    parts = []
    docs_used = []
    for i, d in enumerate(docs, 1):
        meta = getattr(d, "metadata", {}) or {}
        doc_id = meta.get("id", f"doc_{i}")
        country = meta.get("country", "UNKNOWN")
        visa_type = meta.get("visa_type", "UNKNOWN")
        content = getattr(d, "page_content", str(d))
        excerpt = content.strip().replace("\n", " ")[:max_excerpt_chars]
        parts.append(f"[{i}] {doc_id} ({country}, {visa_type}): {excerpt}")
        docs_used.append({"id": doc_id, "country": country, "visa_type": visa_type})
    return "\n\n".join(parts), docs_used


def load_template() -> str:
    if os.path.exists(TEMPLATE_PATH):
        return open(TEMPLATE_PATH, "r", encoding="utf-8").read()
    # fallback simple template
    return (
        "You are a visa eligibility officer. Using the retrieved immigration policy context,\n"
        "evaluate whether the user meets the eligibility criteria for the given visa type.\n\n"
        "### Context:\n{retrieved_context}\n\n"
        "### User Information:\nAge: {age}\nNationality: {nationality}\nEducation: {education}\nEmployment: {employment}\nIncome: {income}\nVisa Type: {visa_type}\n\n"
        "### Instruction:\nProvide a clear eligibility decision (Likely Eligible / Likely Ineligible / Insufficient Data)\n"
        "and briefly explain your reasoning in plain English. Include citations by doc index.\n"
    )


def make_full_prompt(user_profile: Dict[str, str], retrieved_context: str) -> str:
    template = load_template()
    filled = template.format(
        retrieved_context=retrieved_context,
        age=user_profile.get("age", "Unknown"),
        nationality=user_profile.get("nationality", "Unknown"),
        education=user_profile.get("education", "Unknown"),
        employment=user_profile.get("employment", "Unknown"),
        income=user_profile.get("income", "Unknown"),
        visa_type=user_profile.get("visa_type", "Unknown"),
    )
    # Ask the model to return a JSON object with specific fields for easy parsing
    filled += (
        "\n\nReturn output as JSON ONLY with keys: decision, explanation, confidence (0-100), citations (list of doc indices).\n"
        "Example:\n"
        '{"decision":"Likely Eligible","explanation":"...","confidence":87,"citations":[1,3]}\n'
    )
    return filled


def call_gemini(prompt: str, model_candidates: List[str] = None, timeout: int = 30) -> str:
    """
    Call Gemini / Google GenAI with the updated API. Return text output.
    """
    if not GENAI_AVAILABLE:
        raise RuntimeError("genai module not available. Check your environment and google-genai installation.")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")

    import google.generativeai as genai
    genai.configure(api_key=api_key)

    # Configure the model
    try:
        # List available models
        for m in genai.list_models():
            print(f"Found model: {m.name}")
        
        # Configure generation parameters
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }

        # Initialize the model using flash model
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        
        # Generate content
        response = model.generate_content(
            contents=prompt,
            generation_config=generation_config,
            stream=False
        )
        
        try:
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'parts'):
                return ' '.join(part.text for part in response.parts)
            else:
                return str(response)
        except Exception as e:
            return f"[RESPONSE ERROR] {str(e)}: {str(response)}"
    except Exception as e:
        raise RuntimeError(f"Failed to generate content with Gemini: {e}")


def parse_json_from_text(text: str) -> Dict[str, Any]:
    """
    Attempt to find the first JSON object in the model output and parse it.
    """
    try:
        # Find first '{' and last '}' to extract JSON-ish substring
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            return json.loads(candidate)
    except Exception:
        pass
    # fallback: return raw text in explanation with low confidence
    return {"decision": "Insufficient Data", "explanation": text.strip(), "confidence": 30, "citations": []}


def log_query(entry: Dict[str, Any]):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_rag_for_query(user_profile: Dict[str, str], query_text: str, top_k: int = TOP_K) -> Dict[str, Any]:
    # 1) retrieve
    docs = retrieve(query_text, k=top_k)  # -> uses [`retrieve`](src/rag_inference.py)
    retrieved_context, docs_used = build_retrieved_context(docs)

    # 2) construct prompt
    prompt = make_full_prompt(user_profile, retrieved_context)

    # 3) call LLM (Gemini) defensively
    try:
        raw_output = call_gemini(prompt)
    except Exception as e:
        raw_output = f"[ERROR] Failed to call Gemini: {e}"

    # 4) parse model output (expecting JSON)
    parsed = {}
    if raw_output.startswith("[ERROR]"):
        parsed = {"decision": "Insufficient Data", "explanation": raw_output, "confidence": 0, "citations": []}
    else:
        parsed = parse_json_from_text(raw_output)

    # 5) build final response object
    response = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "user_profile": user_profile,
        "query_text": query_text,
        "docs_used": docs_used,
        "prompt_len": len(prompt),
        "raw_output": raw_output,
        "decision": parsed.get("decision"),
        "explanation": parsed.get("explanation"),
        "confidence": parsed.get("confidence"),
        "citations": parsed.get("citations", []),
    }

    # 6) log to file
    try:
        log_query(response)
    except Exception:
        pass

    return response


if __name__ == "__main__":
    # Example usage
    user = {"age": "22", "nationality": "India", "education": "Bachelor's", "employment": "Student", "income": "0", "visa_type": "F1 Student"}
    q = "F1 Student eligibility for USA"
    out = run_rag_for_query(user, q, top_k=3)
    print("Decision:", out["decision"])
    print("Confidence:", out["confidence"])
    print("Explanation:", out["explanation"])
    print("Citations:", out["citations"])