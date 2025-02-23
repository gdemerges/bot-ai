from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()
app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8000))

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        logger.info(f"Message reçu : {request.message}")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": request.message}],
            api_key=OPENAI_API_KEY
            max_tokens=100
        )
        result = response.choices[0].message.content
        logger.info(f"Réponse envoyée : {result}")
        return {"response": result}
    except Exception as e:
        logger.error(f"Erreur lors de la requête OpenAI : {e}")
        return {"error": str(e)}
    
@app.get("/status")
def status():
    return {"status": "API en ligne"}

@app.get("/logs", response_class=PlainTextResponse)
def get_logs():
    with open("app.log", "r") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)