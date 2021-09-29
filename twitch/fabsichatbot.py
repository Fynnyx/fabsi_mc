from twitchio import client
from twitchio.ext import commands
from twitchio.ext import routines
import datetime
import random
import json

with open("properties.json", encoding='UTF-8') as f:
    data = json.load(f)

bot = commands.Bot(
    token=data["properties"]["token"],
    client_secret=data["properties"]["client_secret"],
    prefix=data["properties"]["prefix"],
    initial_channels=data["properties"]["initial_channels"]
)

@bot.event()
async def event_ready():
    print("FabsiChatBot: logged in")
    # Start routines
    info_rout.start()


# Routines ---------------------------------------------------------------------------

@routines.routine(seconds=data["properties"]["routines"]["information"]["time"])
async def info_rout():
    messages = data["properties"]["routines"]["information"]["messages"]
    index = random.randint(0, len(messages)-1)
    print(messages[index])
    chan = bot.get_channel("fabsi_mc")
    await chan.send("words") 
    # ctx.send(messages[index])


# @bot.event()
# async def event_message(ctx):
    # print(ctx.author.name)
    # print(ctx.content)

@bot.command()
async def dc(ctx: commands.Context):
    await ctx.send("Fabsi's Discord: %s" % (data["properties"]["social_media"]["discord"]))

bot.run()