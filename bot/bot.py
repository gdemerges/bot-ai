import discord
from discord.ext import commands
import os
import httpx
from dotenv import load_dotenv
from prometheus_client import Counter, start_http_server

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
API_URL = os.getenv("FASTAPI_URL")
API_CONFIG_URL = os.getenv("FASTAPI_CONFIG_URL", "http://127.0.0.1:8000/config")

if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN non défini !")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

messages_processed = Counter("discord_messages_processed", "Nombre total de messages traités par le bot")
start_http_server(9090)

def get_personality():
    """Récupère la personnalité du bot depuis l'API."""
    try:
        response = httpx.get(API_CONFIG_URL, timeout=10)
        return response.json().get("personality", "neutre") if response.status_code == 200 else "neutre"
    except httpx.RequestError:
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
            answer = response.json().get("response", "❌ Erreur lors de la requête.")
    except httpx.RequestError as e:
        answer = f"❌ Erreur de connexion : {e}"

    await message.channel.send(answer)
    messages_processed.inc()
    await bot.process_commands(message)

@bot.command()
async def parler(ctx, *, message):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_URL}/chat", json={"message": message})
        answer = response.json().get("response", "❌ Erreur lors de la requête.")

    await ctx.send(answer)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

if __name__ == "__main__":
    if os.getenv("CI") != "true":
        bot.run(TOKEN)
