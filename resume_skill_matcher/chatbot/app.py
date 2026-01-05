import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient

# =====================
# CONFIG
# =====================
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
HF_TOKEN = os.environ.get("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN environment variable not set")

client = InferenceClient(
    model=MODEL_ID,
    token=HF_TOKEN
)

app = FastAPI(
    title="Resume Career Assistant API",
    version="1.0.0"
)

# =====================
# SCHEMAS
# =====================
class ChatRequest(BaseModel):
    prompt: str
    system_prompt: str
    max_tokens: int = 800

class ChatResponse(BaseModel):
    answer: str

# =====================
# HEALTH CHECK
# =====================
@app.get("/")
def health():
    return {"status": "ok", "service": "llama3-career-api"}

# =====================
# CHAT ENDPOINT
# =====================
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    HuggingFace Llama-3 expects ONE prompt string.
    Do NOT send messages[].
    """

    # 🔑 CRITICAL: single prompt
    final_prompt = (
        f"{request.system_prompt}\n\n"
        f"{request.prompt}"
    )

    try:
        response = client.text_generation(
            prompt=final_prompt,
            max_new_tokens=request.max_tokens,
            temperature=0.3,
            top_p=0.9,
        )

        return ChatResponse(answer=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
