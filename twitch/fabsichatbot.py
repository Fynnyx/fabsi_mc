from twitchio.ext import commands
import json

with open("properties.json", encoding='UTF8') as f:
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

# @bot.event()
# async def event_message(ctx):
    # print(ctx.author.name)
    # print(ctx.content)

# @bot.command()
# async def test(ctx: commands.Context):
#     await ctx.send("Test command triggerd")

@bot.command()
async def dc(ctx: commands.Context):
    await ctx.send("Fabsi's Discord: %s" % (data["properties"]["social_media"]["discord"]))

bot.run()