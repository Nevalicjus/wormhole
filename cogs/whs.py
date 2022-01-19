import discord
import os
from discord.ext import commands
import json
import asyncio
import datetime
import typing

class Whs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def create(self, ctx, id1: discord.TextChannel, id2: typing.Union[discord.TextChannel, discord.Guild], id3: discord.TextChannel = None):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if id3 == None:
            #running in local mode
            ch1 = self.client.get_channel(id1.id)
            if ch1 == None:
                embed = self.constructResponseEmbedBase(f"Your first ID doesn't look like a channel or I don't have access to it")
                await ctx.send(embed = embed)
                return
            ch2 = self.client.get_channel(id2.id)
            if ch2 == None:
                embed = self.constructResponseEmbedBase(f"Your second ID doesn't look like a channel or I don't have access to it")
                await ctx.send(embed = embed)
                return

            if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
                embed = self.constructResponseEmbedBase(f"You are not permitted to run this command")
                await ctx.send(embed = embed)
                return

            with open(f'configs/{ctx.guild.id}.json', 'r') as f:
                config = json.load(f)

            if len(config["Whs"]["Ws"].keys()) >= config["General"]["MaxWs"]:
                embed = self.constructResponseEmbedBase(f"You cannot create any more Wormholes in this Guild! Limit here is {wormconfig['General']['MaxWhs']}")
                await ctx.send(embed = embed)
                return

            if len(config["Whs"]["Hs"].keys()) >= config["General"]["MaxHs"]:
                embed = self.constructResponseEmbedBase(f"You cannot create any more Wormholes in this Guild! Limit here is {wormconfig['General']['MaxWhs']}")
                await ctx.send(embed = embed)
                return

            config["Whs"]["Ws"][f"{id1.id}"] = {}
            config["Whs"]["Ws"][f"{id1.id}"]["name"] = "None"
            config["Whs"]["Ws"][f"{id1.id}"]["guildid"] = ctx.guild.id
            config["Whs"]["Ws"][f"{id1.id}"]["holeid"] = id2.id

            config["Whs"]["Hs"][f"{id2.id}"] = {}
            config["Whs"]["Hs"][f"{id2.id}"]["name"] = "None"
            config["Whs"]["Hs"][f"{id2.id}"]["guildid"] = ctx.guild.id
            config["Whs"]["Hs"][f"{id2.id}"]["wormid"] = id1.id

            with open(f'configs/{ctx.guild.id}.json', 'w') as f:
                json.dump(config, f, indent = 4)

            embed = self.constructResponseEmbedBase(f"Successfully created a link between {id1.mention} and {id2.mention}")
            await ctx.send(embed = embed)

        else:
            #running in global mode
            ch1 = self.client.get_channel(id1.id)
            if ch1 == None:
                embed = self.constructResponseEmbedBase(f"Your first ID doesn't look like a channel or I don't have access to it")
                await ctx.send(embed = embed)
                return
            g2 = self.client.get_guild(id2.id)
            if g2 == None:
                embed = self.constructResponseEmbedBase(f"Your second ID doesn't look like a Guild or I don't have access to it")
                await ctx.send(embed = embed)
                return
            ch3 = self.client.get_guild(id3.id)
            if ch3 == None:
                embed = self.constructResponseEmbedBase(f"Your third ID doesn't look like a Guild or I don't have access to it")
                await ctx.send(embed = embed)
                return

            if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
                embed = self.constructResponseEmbedBase(f"You are not permitted to run this command")
                await ctx.send(embed = embed)
                return

            if id2 not in client.guilds:
                embed = self.constructResponseEmbedBase(f"I am not a member of the guild you are trying to point me to")
                await ctx.send(embed = embed)
                return

            if self.checkPerms(ctx.author.id, id2.id, ["admin", "manage_guild"]) == False:
                embed = self.constructResponseEmbedBase(f"You do not have the required permissions to create a wormhole on hole server")
                await ctx.send(embed = embed)
                return

            with open(f'configs/{ctx.guild.id}.json', 'r') as f:
                wormconfig = json.load(f)

            if len(wormconfig["Whs"]["Ws"].keys()) >= wormconfig["General"]["MaxWs"]:
                embed = self.constructResponseEmbedBase(f"You cannot create any more Wormholes from the worm Guild! Limit here is {wormconfig['General']['MaxWhs']}")
                await ctx.send(embed = embed)
                return

            with open(f'configs/{id2.id}.json', 'r') as f:
                holeconfig = json.load(f)

            if len(holeconfig["Whs"]["Hs"].keys()) >= holeconfig["General"]["MaxHs"]:
                embed = self.constructResponseEmbedBase(f"You cannot create any more Wormholes to the hole Guild! Limit there is {wormconfig['General']['MaxWhs']}")
                await ctx.send(embed = embed)
                return

            wormconfig["Whs"]["Ws"][f"{id1.id}"] = {}
            wormconfig["Whs"]["Ws"][f"{id1.id}"]["name"] = "None"
            wormconfig["Whs"]["Ws"][f"{id1.id}"]["guildid"] = id2.id
            wormconfig["Whs"]["Ws"][f"{id1.id}"]["holeid"] = id3.id

            holeconfig["Whs"]["Hs"][f"{id3.id}"] = {}
            holeconfig["Whs"]["Hs"][f"{id3.id}"]["name"] = "None"
            holeconfig["Whs"]["Hs"][f"{id3.id}"]["guildid"] = ctx.guild.id
            holeconfig["Whs"]["Hs"][f"{id3.id}"]["wormid"] = id1.id

            with open(f'configs/{ctx.guild.id}.json', 'w') as f:
                json.dump(wormconfig, f, indent = 4)

            with open(f'configs/{id2.id}.json', 'w') as f:
                json.dump(holeconfig, f, indent = 4)

            embed = self.constructResponseEmbedBase(f"Successfully created a link between {id1.mention} and {id3.mention}[`{id2.id}`]")
            await ctx.send(embed = embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild
        channel = message.channel

        with open(f'configs/{guild.id}.json', 'r') as f:
            config = json.load(f)

        if f"{channel.id}" in list(config["Whs"]["Ws"].keys()):
            dest_guild_id = config["Whs"]["Ws"][f"{channel.id}"]["guildid"]
            dest_channel_id = config["Whs"]["Ws"][f"{channel.id}"]["holeid"]

            dest_guild = self.client.get_guild(dest_guild_id)
            dest_channel = dest_guild.get_channel(dest_channel_id)

            embed = discord.Embed(title = f"**Wormhole - Message**", description = f"{message.author.mention}: {message.content}", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://n3v.xyz/icons/wormhole-logo.png")
            now = datetime.datetime.now()
            embed.set_footer(text = f"{now.strftime('%H:%M:%S')} / {now.strftime('%d/%m/%y')} | Wormhole made with \u2764\ufe0f by Nevalicjus")

            await dest_channel.send(embed = embed)


    def log(self, guild_id, log_msg: str):
        with open('main-config.json', 'r') as f:
            config = json.load(f)
            logfile = config['LogFile']
        if guild_id == 0:
            print(f"[{datetime.datetime.now()}] [\033[34mOTHER\033[0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [OTHER]: " + log_msg + "\n")
        else:
            print(f"[{datetime.datetime.now()}] [{guild_id}] [\033[34mOTHER\033[0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [{guild_id}] [OTHER]: " + log_msg + "\n")

    def checkPerms(self, user_id, guild_id, addscopes = []):
        try:
            with open(f'configs/{guild_id}.json', 'r') as f:
                config = json.load(f)
                admin_roles = config['General']['AdminRoles']
        except FileNotFoundError:
            return False

        with open(f'main-config.json', 'r') as f:
            main_config = json.load(f)
            owners = main_config['OwnerUsers']

        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)

        if "owner_only" in addscopes:
            if user_id == guild.owner_id:
                return True

        if "owner_users_only" in addscopes:
            if user_id in owners:
                return True

        if user_id in owners:
            return True
        if user_id == guild.owner_id:
            return True
        for role in member.roles:
            if role.id in admin_roles:
                return True

        if "admin" in addscopes:
            if member.guild_permissions.administrator == True:
                return True
        if "manage_guild" in addscopes:
            if member.guild_permissions.manage_guild == True:
                return True

        else:
            return False

    def checkInvos(self, guild_id):
        try:
            try:
                with open(f'configs/{guild_id}.json', 'r') as f:
                    config = json.load(f)
                    delinvos = config['General']['DeleteInvocations']
            except FileNotFoundError:
                return False

            if delinvos == 1:
                return True
            else:
                return False

        except KeyError:
            #there was no config for guild_id or it was corrupted, new config should be generated
            pass

    def constructResponseEmbedBase(self, desc):
        embed = discord.Embed(title = f"**Wormhole**", description = desc, color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url="https://n3v.xyz/icons/wormhole-logo.png")
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | Wormhole made with \u2764\ufe0f by Nevalicjus")

        return embed

    async def serverLog(self, guild_id, type: str, log_msg):
        with open(f'configs/{guild_id}.json', 'r') as f:
            config = json.load(f)
            log_channel_id = config['General']['ServerLog']
        if log_channel_id == 0:
            return

        if type in ["wh_created"]:
            em_color = discord.Colour.from_rgb(67, 181, 129)
        #if type in []:
        #    em_color = discord.Colour.from_rgb(250, 166, 26)
        if type in ["wh_deleted"]:
            em_color = discord.Colour.from_rgb(240, 71, 71)

        embed = discord.Embed(title = f"**Wormhole Logging**", color = em_color)
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | Wormhole made with \u2764\ufe0f by Nevalicjus")

        if type == "wh_created":
            embed.add_field(name = "Wormhole Created", value = log_msg, inline = False)
        if type == "wh_deleted":
            embed.add_field(name = "Wormhole Deleted", value = log_msg, inline = False)

        log_channel = self.client.get_channel(log_channel_id)
        await log_channel.send(embed = embed)


def setup(client):
    client.add_cog(Whs(client))
