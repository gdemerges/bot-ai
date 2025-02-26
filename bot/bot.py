import discord
from discord.ext import commands
import os
import httpx

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_BOT_TOKEN") 
API_URL = os.getenv("FASTAPI_URL") 

@bot.event
async def on_ready():
    print(f'✅ {bot.user} est connecté et prêt !')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower().startswith("!ask"):
        user_message = message.content[5:] 

        if not user_message:
            await message.channel.send("❌ Veuillez poser une question après `!ask`.")
            return

        await message.channel.send("💬 Génération de la réponse...")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{API_URL}/chat", json={"message": user_message})
                response_data = response.json()

            if "response" in response_data:
                answer = response_data["response"]
            else:
                answer = "❌ Erreur lors de la requête à l'API."

        except Exception as e:
            answer = f"❌ Erreur de connexion : {e}"

        await message.channel.send(answer)

    await bot.process_commands(message)
    
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

bot.run(TOKEN)