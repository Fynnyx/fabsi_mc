from twitchio import client
from twitchio.ext import commands
from twitchio.ext import routines
import datetime
import random
import requests
import json

with open("properties.json", encoding='UTF-8') as f:
    global data
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

    # global variables
    global isInfoEnabled
    isInfoEnabled = data["properties"]["routines"]["information"]["default"]
    global bot_nick
    bot_nick = data["properties"]["nick"]

    # Start routines
    info_rout.start()
    update_json.start()


# Routines ---------------------------------------------------------------------------

@routines.routine(seconds=data["properties"]["routines"]["update_data"]["time"])
async def update_json():
    with open("properties.json", encoding='UTF-8') as f:
        global data
        data = json.load(f)

@bot.command(aliases=data["properties"]["commands"]["enable_info"])
async def enable_info(ctx):
    if ctx.author.is_mod:
        global isInfoEnabled 
        isInfoEnabled = True

@bot.command(aliases=data["properties"]["commands"]["disable_info"])
async def disable_info(ctx):
    if ctx.author.is_mod:
        global isInfoEnabled 
        isInfoEnabled = False


@routines.routine(seconds=data["properties"]["routines"]["information"]["time"])
async def info_rout():
    if isInfoEnabled == True:
        messages = data["properties"]["routines"]["information"]["messages"]
        index = random.randint(0, len(messages)-1)
        # print(messages[index])
        channel = bot.get_channel(data["properties"]["channel"])
        await channel.send(messages[index])


# Commands ---------------------------------------------------------------------------

bot.run()