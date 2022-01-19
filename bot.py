import discord
import os
from discord.ext import commands
import json
import asyncio
import datetime
intents = discord.Intents.default()
intents.members = True
from aiohttp import web

with open('main-config.json', 'r') as f:
    config = json.load(f)
    prefix = config['Prefix']
    token = config['DiscordToken']
    logfile = config['LogFile']
    delinvos = config['DeleteOwnerCommandsInvos']
    whapi_opt = config["WHAPI"]
    whapi_addr = config["WHAPIAddr"]
    whapi_port = config["WHAPIPort"]

def get_prefix(client, message):
    try:
        with open(f'configs/{message.guild.id}.json', 'r') as f:
            config = json.load(f)
            prefix = config['General']['Prefix']
    except:
        prefix = "wh!"

    return prefix

client = commands.Bot(command_prefix = get_prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    ascii = """
  _   _             __          __                  _           _
 | \ | |            \ \        / /                 | |         | |
 |  \| | _____   __  \ \  /\  / /__  _ __ _ __ ___ | |__   ___ | | ___
 | . ` |/ _ \ \ / /   \ \/  \/ / _ \| '__| '_ ` _ \| '_ \ / _ \| |/ _ \
 | |\  |  __/\ V /     \  /\  / (_) | |  | | | | | | | | | (_) | |  __/
 |_| \_|\___| \_/       \/  \/ \___/|_|  |_| |_| |_|_| |_|\___/|_|\___|

    """
    print(f"\033[34m{ascii}\033[0m")
    log("Wormhole started")
    loaded_cogs = await loadall()
    log(f"Cogs named: {loaded_cogs} were loaded")
    client.loop.create_task(status_task())
    log("Status service started")
    log(f"Wormhole ready")

@client.command(help="Loads a cog.")
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} was loaded')
    log(f'{extension} was loaded')

@client.command(help="Unloads a cog.")
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} was unloaded')
    log(f'{extension} was unloaded')

@client.command(help="Reloads a cog")
@commands.is_owner()
async def reload(ctx, extension):
    if extension == "all":
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                client.unload_extension(f'cogs.{filename[:-3]}')
                client.load_extension(f'cogs.{filename[:-3]}')
                await ctx.send(f'{filename[:-3]} was reloaded')
                log(f'{filename[:-3]} was reloaded')
    else:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} was reloaded')
        log(f'{extension} was reloaded')

async def loadall():
    loaded_cogs = ""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')
            loaded_cogs += f"{filename[:-3]} "
    return loaded_cogs

def log(log_msg: str):
    print(f"[{datetime.datetime.now()}] [\033[1;31mINTERNAL\033[0;0m]: " + log_msg)
    with open('log.txt', 'a') as f:
        f.write(f"[{datetime.datetime.now()}] [INTERNAL]: " + log_msg + "\n")

async def status_task():
    while True:
        members = 0
        try:
            for guild in client.guilds:
                members += guild.member_count
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=f"on {len(client.guilds)} guilds with {members} members"))
            await asyncio.sleep(30)
            await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="wh!help | https://n3v.xyz"))
            await asyncio.sleep(30)
        except:
            pass

async def alive(request):
    return web.Response(text = "Wormhole is running")

async def web_start():
    app = web.Application()
    app.add_routes([web.get('/alive-wormhole', alive)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, whapi_addr, whapi_port)
    await site.start()
    log(f"Wormhole Status Update running")

    while True:
        await asyncio.sleep(3600)

if whapi_opt == True:
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(token))
    loop.create_task(web_start())
    #client.run(token)
    loop.run_forever()
else:
    client.run(token)
