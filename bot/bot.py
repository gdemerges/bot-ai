import discord
from discord.ext import commands
import os
import httpx
from dotenv import load_dotenv
import requests
from prometheus_client import Counter, start_http_server

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("FASTAPI_URL")
API_CONFIG_URL = "http://127.0.0.1:8000/config"

messages_processed = Counter("discord_messages_processed", "Nombre total de messages traités par le bot")

start_http_server(9090)

def get_personality():
    """Récupère la personnalité actuelle du bot depuis l'API"""
    try:
        response = requests.get(API_CONFIG_URL, timeout=10)
        if response.status_code == 200:
            return response.json().get("personality", "neutre")
        return "neutre"
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération de la personnalité : {e}")
        return "neutre"


@bot.event
async def on_ready():
    print(f'✅ {bot.user} est connecté et prêt !')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/chat", json={"message": message.content})
            response_data = response.json()

        if "response" in response_data:
            answer = response_data["response"]
        else:
            answer = "❌ Erreur lors de la requête à l'API."

    except httpx.RequestError as e:
        answer = f"❌ Erreur de connexion : {e}"
    except httpx.HTTPStatusError as e:
        answer = f"❌ Erreur HTTP : {e}"

    await message.channel.send(answer)
    
    messages_processed.inc()
    await bot.process_commands(message)
    
@bot.command()
async def parler(ctx, *, message):
    """Le bot répond en fonction de sa personnalité via l'API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/chat", json={"message": message})
            response_data = response.json()

        if "response" in response_data:
            answer = response_data["response"]
        else:
            answer = "❌ Erreur lors de la requête à l'API."

    except httpx.RequestError as e:
        answer = f"❌ Erreur de connexion : {e}"
    except httpx.HTTPStatusError as e:
        answer = f"❌ Erreur HTTP : {e}"

    await ctx.send(answer)
    
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

bot.run(TOKEN)
