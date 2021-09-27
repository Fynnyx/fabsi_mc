from sys import prefix
from twitchio.client import Client
from twitchio.ext import commands
import json

with open("properties.json", encoding='UTF8') as f:
    data = json.load(f)

bot = commands.Bot(
    token=data["properties"]["token"],
    client_secret=data["properties"]["client_secret"],
    prefix=data["properties"]["nick"],
    initial_channels=data["properties"]["initial_channels"]
)

@bot.event
async def on_ready():
    print("FabsiChatBot: logged in")

@bot.event
async def event_message(ctx):
    print(ctx.author.name)
    print(ctx.content)

if __name__ == '__main__':
    bot.run()