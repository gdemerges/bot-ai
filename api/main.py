from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import openai
import os
import uvicorn
import logging
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from fastapi.responses import Response

load_dotenv()

requests_counter = Counter("http_requests_total", "Nombre total de requêtes HTTP")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)
app = FastAPI()

PORT = int(os.getenv("PORT", "8000"))

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        personality = bot_config.get("personality", "neutre")

        system_message = {
            "neutre": "Tu es un assistant utile et impartial.",
            "sombre": "Tu es un assistant cynique et sarcastique.",
            "bienveillant": "Tu es un assistant empathique et encourageant.",
            "drôle": "Tu es un assistant comique et blagueur."
        }.get(personality, "Tu es un assistant utile et impartial.")

        logger.info("Personnalité actuelle : %s", personality)
        logger.info("Message reçu : %s", request.message)

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": request.message}
            ],
            max_tokens=100
        )
        result = response.choices[0].message.content
        logger.info("Réponse envoyée : %s", result)
        return {"response": result}
    except Exception as e:
        logger.error("Erreur lors de la requête OpenAI : %s", e)
        return {"error": str(e)}
    
@app.get("/status")
def status():
    return {"status": "API en ligne"}

@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/logs", response_class=PlainTextResponse)
def get_logs():
    with open("app.log", "r", encoding="utf-8") as f:
        return f.read()
    
bot_config = {
    "personality": "neutre"
}

class BotConfig(BaseModel):
    personality: str

@app.get("/config")
def get_config():
    """Retourne la configuration actuelle du bot"""
    return bot_config

@app.post("/config")
def update_config(config: BotConfig):
    """Met à jour la configuration du bot"""
    bot_config["personality"] = config.personality
    return {"message": "Configuration mise à jour", "config": bot_config}

http_requests_total = Counter("http_requests_total", "Nombre total de requêtes reçues")

request_latency = Histogram("http_request_duration_seconds", "Temps de réponse des requêtes")

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    http_requests_total.inc()
    with request_latency.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
