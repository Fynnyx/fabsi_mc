from os import scandir
import discord
from discord import Member
from discord.ext import commands
import discord.utils
import asyncio
import json
from discord.webhook import AsyncWebhookAdapter
import requests

with open("properties.json") as f:
    data = json.load(f)

TOKEN = data["properties"]["token"]
PREFIX = data["properties"]["prefix"]

intents = discord.Intents()
intents.guilds = True
intents.members = True
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.dm_messages = True



client = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents)

# Functions ---------------------------------------------------------------------------

async def status_task():
    messages = data["properties"]["status"]["messages"]
    time = data["properties"]["status"]["time"]    
    while True:
        for x in range(len(messages)):
            await client.change_presence(activity=discord.Game(name=messages[x]))
            await asyncio.sleep(time)


async def check_isLive():

    with open("properties.json") as f:
        data = json.load(f)

    client_id = data["properties"]["events"]["twitch"]["client_id"]
    client_secret = data["properties"]["events"]["twitch"]["client_secret"]
    streamer_name = data["properties"]["events"]["twitch"]["streamer"]

    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        "grant_type": 'client_credentials'
    }
    r = requests.post('https://id.twitch.tv/oauth2/token', body)
    keys = r.json();
    headers = {
        'Client-ID': client_id,
        'Authorization': 'Bearer ' + keys['access_token']
    }
    stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
    stream_data = stream.json()
    
    if len(stream_data['data']) == 1:
        return dict(stream_data)
    else:
        return False    


async def check_permissions(command, user:Member, channel):
    command_perm_list = data["properties"]["commands"][str(command)]["permissions"]
    user_allowed = False
    for perm in command_perm_list:
        for role in user.roles:
            if str(perm) == str(role.name):
                user_allowed: bool = True
    if user_allowed == True:
        return True
    else:
        msg = await channel.send("⛔Permission Denied")
        await asyncio.sleep(3)
        await msg.delete()
        return False

async def send_error(error, channel):
    msg = await channel.send("⛔Error: %s" % error)
    await asyncio.sleep(5)
    await msg.delete()


# Events ---------------------------------------------------------------------------

@client.event
async def on_ready():
    print("FabsiBot: logged in")
    client.loop.create_task(status_task())
    # client.loop.create_task(twitch())

@client.event
async def on_member_join(member):
    channel_id = int(data["properties"]["events"]["on_member_join"]["welcome_channel"])
    channel = await client.fetch_channel(channel_id)
    rule_channel = await client.fetch_channel(data["properties"]["events"]["on_member_join"]["rules_channel"])
    info_channel = await client.fetch_channel(data["properties"]["events"]["on_member_join"]["info_channel"])
    await channel.send("Hey <@" + str(member.id) + "> schön dass du auf Fabsi's Server gejoint bis, lies dir bitte die Regeln in <#" + str(rule_channel.id) + "> durch und schau in <#" + str(info_channel.id) + "> für mehr Informationen.")



# Moderator ---------------------------------------------------------------------------

@client.command(aliases=data["properties"]["commands"]["clear"]["aliases"])
async def clear(ctx, amount:str):
    channel = ctx.message.channel
    if await check_permissions("clear", ctx.message.author, channel):
        if amount == 'all':
            await channel.purge()
            await send_deleted_msgs("all", channel)
        elif amount:
            try:
                amount = int(amount)
                await channel.purge(limit=amount)
                await send_deleted_msgs(amount, channel)
            except TypeError:
                await send_error("Amount must be a number!", channel)
            except:
                await send_error("Please try this format -> `-clear [amount(number)]`", channel)
    else:
        await ctx.message.delete()


async def send_deleted_msgs(amount, channel):
    msg = await channel.send("🗑Deleted `%s` messages" % amount)
    await asyncio.sleep(2)
    await msg.delete()


@client.listen('on_message')
async def blacklist(message):
    blacklist = data["properties"]["events"]["blacklist"]["blacklist"]
    for x in blacklist:
        if x in message.content:
            await message.channel.send("<@&889822969596088320> Die Nachricht verwendet geblockte Wörter") 

# @client.listen("on_reaction_add")
# async def reaction_role(reaction):


# Help Command ---------------------------------------------------------------------------

@client.command(pass_context=True, aliases=list(data["properties"]["commands"]["help"]["aliases"]))
async def help(ctx):
    await send_help_embed(ctx)

async def send_help_embed(ctx):
    help_embed = discord.Embed(title="Hilfe für den %s." % str(client.user.name),
                                    description="Hier werden dir alle Informationen über die verschiedenen Commands die der <@%s> kann, welche Aliasse er hat und wer die Rechte hat den Command zu benutzen." % str(client.user.id),
                                    colour=discord.Colour(0x9013fe))

    for command in data["properties"]["commands"]:
        
        help_embed.add_field(name="-- %s --" %(command),
                                value="*Beschreibung:* %s \n *Aliasse:* %s \n *Rechte:* %s hat/haben Zugriff auf diesen Command." % (data["properties"]["commands"][command]["description"], data["properties"]["commands"][command]["aliases"], data["properties"]["commands"][command]["permissions"]),
                                inline=False)

    await ctx.channel.send(embed=help_embed)

# Commands ---------------------------------------------------------------------------

@client.command()
async def stage(ctx, *, name):
    if await check_permissions("stage", ctx.message.author, ctx.channel):
        category_id = int(data["properties"]["commands"]["stage"]["category_id"])
        category = discord.utils.get(ctx.guild.categories, id=category_id)
        name = "🔴 " + name
        s_channel = await ctx.guild.create_stage_channel(name, category=category, position=1)
        # await s_channel.set_permissions(s_channel, overwrite=None)
        msg = await ctx.channel.send("Created Stage channel: " + name)
        await asyncio.sleep(4)
        await msg.delete()
    else:
        await ctx.message.delete()

@client.command()
async def delstage(ctx):
    category = discord.utils.get(ctx.guild.categories, name="-- 🔴 Record/Live --")
    for channel in category.stage_channels:
        await channel.delete()
        msg = await ctx.send('Deleted: %s' % (channel.name))
        await asyncio.sleep(4)
        await msg.delete()

@client.command(aliases=data["properties"]["commands"]["social_media"]["aliases"])
async def social_media(ctx):
    await ctx.channel.send("Twitch: %s" % (data["properties"]["commands"]["social_media"]["links"]["twitch"]))

@client.command()
async def twitch(ctx):
    isLive = await check_isLive()
    if not isLive:
        return
    else:
        with open("stream.json", "w") as f:
            f.write(json.dumps(dict(isLive), indent=2))
        with open("properties.json") as f:
            data = json.load(f)
        with open("stream.json") as f:
            stream_data = json.load(f)

        stream_id = stream_data["data"][0]["id"]
        last_stream_id = data["properties"]["events"]["twitch"]["last_stream_id"]

        # if stream_id != last_stream_id:

        data["properties"]["events"]["twitch"]["last_stream_id"] = str(stream_id)
        with open("properties.json", "w") as f:
            f.write(json.dumps(data, indent=2))

        name = stream_data["data"][0]["user_name"]
        user_login = stream_data["data"][0]["user_login"]
        game = stream_data["data"][0]["game_name"]
        title = stream_data["data"][0]["title"]
        thumbnail = stream_data["data"][0]["thumbnail_url"]
        thumbnail = thumbnail.replace('{width}', '320')
        thumbnail = thumbnail.replace('{height}', '180')
        role_id = str(data["properties"]["events"]["twitch"]["twitch_role"])

        twitch_embed = discord.Embed(title="🔴 - %s streamt %s - " % (name, game),
                                        url="https://twitch.tv/%s" % (user_login),
                                        description='Schaue [hier](https://twitch.tv/%s) vorbei oder klicke oben.\nIch freue mich dich zu sehen' % (user_login), 
                                        color=discord.Color.dark_purple())
        twitch_embed.add_field(name=title, value="-------------------------------------")
        twitch_embed.set_image(url=thumbnail)

        channel = client.get_channel(int(data["properties"]["events"]["twitch"]["twitch_channel"]))
        await channel.send("<@&" + role_id + ">")
        twitch_message = await channel.send(embed=twitch_embed)
        
        # NEEDS TO BE FIXED --------------
        # else: 
        #     name = stream_data["data"][0]["user_name"]
        #     user_login = stream_data["data"][0]["user_login"]
        #     game = stream_data["data"][0]["game_name"]
        #     title = stream_data["data"][0]["title"]
        #     thumbnail = stream_data["data"][0]["thumbnail_url"]
        #     thumbnail = thumbnail.replace('{width}', '320')
        #     thumbnail = thumbnail.replace('{height}', '180')

        #     new_twitch_embed = discord.Embed(title="🔴 - %s streamt %s - " % (name, game),
        #                                     url="https://twitch.tv/%s" % (user_login),
        #                                     description='Schaue [hier](https://twitch.tv/%s) vorbei oder klicke oben.\nIch freue mich dich zu sehen' % (user_login), 
        #                                     color=discord.Color.dark_purple())
        #     new_twitch_embed.add_field(name=title, value="-------------------------------------")
        #     new_twitch_embed.set_image(url=thumbnail)
        #     await twitch_message.edit(embed=new_twitch_embed)


client.run(TOKEN)