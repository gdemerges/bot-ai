import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  

@bot.event
async def on_ready():
    print(f'✅ {bot.user} est connecté et prêt !')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "ping":
        await message.channel.send("Pong ! 🏓")
        
    await bot.process_commands(message)

bot.run(TOKEN)