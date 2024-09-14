import discord
import config
import tracemalloc
tracemalloc.start()
from config import TOKEN
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.presences = True

bot = commands.Bot(command_prefix='&', intents=intents,help_command =None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    
    extensions = ['cogs.moderation', 'cogs.utility', 'cogs.info', 'cogs.onlyowner','cogs.help']  
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f'Loaded extension: {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}. Error: {e}')
    
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="&help"))

bot.run(TOKEN)

