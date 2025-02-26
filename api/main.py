from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import openai
import os
import uvicorn
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

PORT = int(os.getenv("PORT", 8000))

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        logger.info(f"Message reçu : {request.message}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": request.message}],
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