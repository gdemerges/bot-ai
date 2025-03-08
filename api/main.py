from fastapi import FastAPI, Request, Depends
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel
import openai
import os
import uvicorn
import logging
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

http_requests_total = Counter("http_requests_total", "Nombre total de requêtes HTTP")
request_latency = Histogram("http_request_duration_seconds", "Temps de réponse des requêtes")

client = None
if os.getenv("CI") != "true":
    try:
        client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation d'OpenAI : {e}")

PERSONALITIES = {
    "neutre": "Tu es un assistant utile et impartial.",
    "sombre": "Tu es un assistant cynique et sarcastique.",
    "bienveillant": "Tu es un assistant empathique et encourageant.",
    "drôle": "Tu es un assistant comique et blagueur.",
}

bot_config = {"personality": "neutre"}

app = FastAPI()
PORT = int(os.getenv("PORT", "8000"))

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    """Génère une réponse basée sur la personnalité actuelle du bot."""
    try:
        personality = bot_config.get("personality", "neutre")
        system_message = PERSONALITIES.get(personality, PERSONALITIES["neutre"])

        if not client:
            raise ValueError("Client OpenAI non initialisé.")

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": request.message}],
            max_tokens=100,
        )
        result = response.choices[0].message.content
        logger.info(f"Réponse envoyée : {result}")
        return {"response": result}
    except Exception as e:
        logger.error(f"Erreur OpenAI : {e}")
        return {"error": str(e)}

@app.get("/status")
def status():
    return {"status": "API en ligne"}

@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/logs", response_class=PlainTextResponse)
def get_logs():
    """Récupère les logs de l'application."""
    try:
        with open("app.log", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Aucun log disponible."

@app.get("/config")
def get_config():
    """Retourne la configuration actuelle du bot."""
    return bot_config

class BotConfig(BaseModel):
    personality: str

@app.post("/config")
def update_config(config: BotConfig):
    """Met à jour la configuration du bot."""
    bot_config["personality"] = config.personality
    return {"message": "Configuration mise à jour", "config": bot_config}

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    """Middleware pour enregistrer les métriques des requêtes."""
    http_requests_total.inc()
    with request_latency.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    """Exporte les métriques pour Prometheus."""
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
