import discord
import os
from discord.ext import commands
import json
import asyncio
import datetime

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    #------------------------------
    # Create config file for guild on guild join
    #------------------------------
    async def on_guild_join(self, guild):
        self.log(guild.id, f"Joined new guild - {guild.name} [{guild.id}]")

        with open(f'main-config.json', 'r') as f:
            mconfig = json.load(f)

        config = {}
        config["General"] = {}
        config["General"]["DeleteInvocations"] = 0
        config["General"]["AdminRoles"] = []
        config["General"]["ServerLog"] = 0
        config["General"]["Prefix"] = mconfig["Prefix"]
        config["General"]["Analytics"] = False
        config["General"]["AnalyticsLog"] = 0
        config["General"]["MaxWs"] = mconfig["MaxWs"]
        config["General"]["MaxHs"] = mconfig["MaxHs"]
        config["General"]["NotifOwnerOnWh"] = True

        config["Whs"] = {}
        config["Whs"]["Ws"] = {}
        config["Whs"]["Hs"] = {}

        with open(f"configs/{guild.id}.json", 'w') as f:
            json.dump(config, f, indent = 4)

    @commands.Cog.listener()
    #------------------------------
    # Delete the config file when leaving guild
    #------------------------------
    async def on_guild_remove(self, guild):
        self.log(guild.id, f"Left guild - {guild.name} [{guild.id}]")

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')
        if str(guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {guild.id}')

        #saves config
        savefp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.system(f'cp {os.getenv("PWD")}/configs/{guild.id}.json {os.getenv("PWD")}/saved-configs/{guild.id}/{savefp}.json')

        #removes config file on guild leave
        os.system(f"rm configs/{guild.id}.json")

    @commands.command(aliases = ['savecnfg', 'sconf'])
    #------------------------------
    # Saves the current config
    #------------------------------
    async def saveconfig(self, ctx):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')
        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')

        with open(f'main-config.json', 'r') as f:
            config = json.load(f)

        if len(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}')) >= config['MaxSavedConfigs']:
            embed = self.constructResponseEmbedBase(f"Saved Config couldn't be created, Max Saved Configurations number: {config['MaxSavedConfigs']} reached.")
            await ctx.send(embed = embed)
            return

        savefp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.system(f'cp {os.getenv("PWD")}/configs/{ctx.guild.id}.json {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{savefp}.json')

        await self.serverLog(ctx.guild.id, "cnfg_save", "Saved Config was created, at {0} by {1}[`{2}`]".format(datetime.datetime.now().strftime('%H:%M:%S | %d/%m/%Y'), ctx.author, ctx.author.id))
        embed = self.constructResponseEmbedBase(f"Your Saved Config was created, at {datetime.datetime.now().strftime('%H:%M:%S | %d/%m/%Y')}")
        await ctx.send(embed = embed)

    @commands.command(aliases = ['lscnfgs', 'lsconf'])
    #------------------------------
    # Lists Saved Configs
    #------------------------------
    async def listconfigs(self, ctx, specific: int = -1):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if specific not in [-1, 0]:
            guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

            if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
                os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')
                embed = self.constructResponseEmbedBase(f"You had no configurations saved")
                await ctx.send(embed = embed)
                return

            guilds_configs = sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True)
            fetched_config = guilds_configs[specific - 1]

            with open(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{fetched_config}', 'r') as f:
                saved_config = json.load(f)

            embed = discord.Embed(title = f"**Saved Config\n{fetched_config[17:19]}:{fetched_config[14:16]}:{fetched_config[11:13]} | {fetched_config[8:10]}/{fetched_config[5:7]}/{fetched_config[0:4]}**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://n3v.xyz/icons/wormhole-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Wormhole made with \u2764\ufe0f by Nevalicjus")

            for setting in saved_config['General']:
                embed.add_field(name = f"{setting}:", value = f"{saved_config['General'][setting]}", inline = False)

            await ctx.send(embed = embed)

            embed = discord.Embed(title = f"**Saved Config's Invites\n{fetched_config[17:19]}:{fetched_config[14:16]}:{fetched_config[11:13]} | {fetched_config[8:10]}/{fetched_config[5:7]}/{fetched_config[0:4]}**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://n3v.xyz/icons/wormhole-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Wormhole made with \u2764\ufe0f by Nevalicjus")

            no_fields = 0
            for inv in saved_config['Invites']:
                about = ''
                for invrole in saved_config['Invites'][f"{inv}"]["roles"]:
                    try:
                        role = ctx.guild.get_role(invrole)
                        about += f"{role.name}\n"
                    except:
                        about += f"ErrorFetchingRole\n"
                about += f"Uses - {saved_config['Invites'][inv]['uses']}\n"
                if about != '':
                    if saved_config['Invites'][f'{inv}']['name'] != "None":
                        embed.add_field(name = f"{saved_config['Invites'][inv]['name']}", value = about, inline = True)
                    else:
                        embed.add_field(name = f"https://discord.gg/{inv}", value = about, inline = True)
                    no_fields +=1
                if no_fields == 25:
                    await ctx.send(embed = embed)
                    no_fields = 0
                    for i in range(25):
                        embed.remove_field(0)
            if no_fields != 0:
                await ctx.send(embed = embed)

            return

        if specific == 0:

            with open(f'{os.getenv("PWD")}/configs/{ctx.guild.id}.json', 'r') as f:
                config = json.load(f)

            embed = discord.Embed(title = f"**Current Config**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://n3v.xyz/icons/wormhole-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Wormhole made with \u2764\ufe0f by Nevalicjus")

            for setting in config['General']:
                embed.add_field(name = f"{setting}:", value = f"{config['General'][setting]}", inline = False)

            await ctx.send(embed = embed)

            embed = discord.Embed(title = f"**Current Config's Invites**", color = discord.Colour.from_rgb(119, 137, 218))
            embed.set_thumbnail(url="https://n3v.xyz/icons/wormhole-logo.png")
            embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Wormhole made with \u2764\ufe0f by Nevalicjus")

            no_fields = 0
            for inv in config['Invites']:
                about = ''
                for invrole in config['Invites'][f"{inv}"]["roles"]:
                    role = ctx.guild.get_role(invrole)
                    about += f"{role.name}\n"
                about += f"Uses - {config['Invites'][inv]['uses']}\n"
                if about != '':
                    if config['Invites'][f'{inv}']['name'] != "None":
                        embed.add_field(name = f"{config['Invites'][inv]['name']}", value = about, inline = True)
                    else:
                        embed.add_field(name = f"https://discord.gg/{inv}", value = about, inline = True)
                    no_fields +=1
                if no_fields == 25:
                    await ctx.send(embed = embed)
                    no_fields = 0
                    for i in range(25):
                        embed.remove_field(0)
            if no_fields != 0:
                await ctx.send(embed = embed)

            return

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')

        embed = discord.Embed(title = f"**Saved Configs**", color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url="https://n3v.xyz/icons/wormhole-logo.png")
        embed.set_footer(text = f"Support Server - https://discord.gg/wsEU32a3ke | Wormhole made with \u2764\ufe0f by Nevalicjus")
        embed.add_field(name = f"Config 0", value = f"Currently used Config", inline = False)

        i = 0
        for config in sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True):
            i += 1
            config_name: str = config
            embed.add_field(name = f"Config {i} saved on:", value = f"{config_name[11:13]}:{config_name[14:16]}:{config_name[17:19]} | {config_name[8:10]}/{config_name[5:7]}/{config_name[0:4]}", inline = False)

        await ctx.send(embed = embed)

    @commands.command(aliases = ['removeconfig', 'delcnfg', 'delconf', 'remconf'])
    #------------------------------
    # Deletes a Saved Config
    #------------------------------
    async def deleteconfig(self, ctx, target_config: int = 0):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if target_config == 0:
            embed = self.constructResponseEmbedBase(f"You didn't pick any config to delete. To view configs use `i!lscnfgs`")
            await ctx.send(embed = embed)
            return

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')
            embed = self.constructResponseEmbedBase(f"You had no configurations saved")
            await ctx.send(embed = embed)
            return

        guilds_configs = sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True)

        try:
            os.system(f'rm {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{guilds_configs[target_config - 1]}')
            await self.serverLog(ctx.guild.id, "cnfg_del", "Saved Config {0} was deleted by {1}[`{2}`]".format(guilds_configs[target_config - 1], ctx.author, ctx.author.id))
            embed = self.constructResponseEmbedBase(f"Saved Config {guilds_configs[target_config - 1]} was successfully deleted")
            await ctx.send(embed = embed)
            return

        except FileNotFoundError:
            embed = self.constructResponseEmbedBase(f"No Saved Config from this date exists")
            await ctx.send(embed = embed)
            return

    @commands.command(aliases = ['switchcnfg', 'switchconf'])
    #------------------------------
    # Switch the chosen config with the current one
    #------------------------------
    async def switchconfig(self, ctx, target_config: int = 0):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if target_config == 0:
            embed = self.constructResponseEmbedBase(f"You didn't pick any config to switch. To view configs use `i!lscnfgs`")
            await ctx.send(embed = embed)
            return

        guilds_with_saved_cnfgs = os.listdir(f'{os.getenv("PWD")}/saved-configs/')

        if str(ctx.guild.id) not in guilds_with_saved_cnfgs:
            os.system(f'cd {os.getenv("PWD")}/saved-configs/ && mkdir {ctx.guild.id}')
            embed = self.constructResponseEmbedBase(f"You had no configurations saved")
            await ctx.send(embed = embed)
            return

        guilds_configs = sorted(os.listdir(f'{os.getenv("PWD")}/saved-configs/{ctx.guild.id}/'), reverse=True)

        savefp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.system(f'cp {os.getenv("PWD")}/configs/{ctx.guild.id}.json {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{savefp}.json && chmod +r {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{savefp}.json')

        os.system(f'mv {os.getenv("PWD")}/saved-configs/{ctx.guild.id}/{guilds_configs[target_config - 1]} {os.getenv("PWD")}/configs/{ctx.guild.id}.json')

        await self.serverLog(ctx.guild.id, "cnfg_switch", "{0}[`{1}`], switched current config for the one created on:\n{2}:{3}:{4} | {5}/{6}/{7}, and the previous config was saved".format(ctx.message.author, ctx.message.author.id, guilds_configs[target_config - 1][11:13], guilds_configs[target_config - 1][14:16], guilds_configs[target_config - 1][17:19], guilds_configs[target_config - 1][8:10], guilds_configs[target_config - 1][5:7], guilds_configs[target_config - 1][0:4]))
        embed = self.constructResponseEmbedBase(f"Your Current Config was switched, for the one created on:\n{guilds_configs[target_config - 1][11:13]}:{guilds_configs[target_config - 1][14:16]}:{guilds_configs[target_config - 1][17:19]} | {guilds_configs[target_config - 1][8:10]}/{guilds_configs[target_config - 1][5:7]}/{guilds_configs[target_config - 1][0:4]},\n and previous Current Config was saved")
        await ctx.send(embed = embed)

    @commands.command()
    #------------------------------
    # Add role.id to adminroles for permission verification
    #------------------------------
    async def addmod(self, ctx, role: discord.Role):
        #checks for invo deletion
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        admin_roles = config['General']['AdminRoles']

        if role.id in admin_roles:
            embed = self.constructResponseEmbedBase("This role was already an admin role")
            await ctx.send(embed = embed)

        admin_roles.append(role.id)
        config['General']['AdminRoles'] = admin_roles
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)
        embed = self.constructResponseEmbedBase(f"Added role {role.name} as an admin role")
        await ctx.send(embed = embed)
        await self.serverLog(ctx.guild.id, "mod_added", "Admin role <@{0}> added".format(role.id))

    @addmod.error
    async def addmod_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "role":
                await ctx.send("Your command is missing a required argument: a valid Discord role (Role meention or Role ID)")
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("Role you are trying to mention or provide ID of doesn't exist")

    @commands.command()
    #------------------------------
    # Remove role.id from adminrole for no further permission verification
    #------------------------------
    async def delmod(self, ctx, role: discord.Role):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        admin_roles = config['General']['AdminRoles']

        if role.id not in admin_roles:
            embed = self.constructResponseEmbedBase("This role wasn't an admin role")
            await ctx.send(embed = embed)

        admin_roles.remove(role.id)
        config['General']['AdminRoles'] = admin_roles
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)
        embed = self.constructResponseEmbedBase(f"Removed role {role.name} as an admin role")
        await ctx.send(embed = embed)
        await self.serverLog(ctx.guild.id, "mod_deleted", "Admin role <@{0}> removed".format(role.id))

    @delmod.error
    async def delmod_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "role":
                await ctx.send("Your command is missing a required argument: a valid Discord role (Role meention or Role ID)")
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("Role you are trying to mention or provide ID of doesn't exist")

    @commands.command(aliases = ['elog'])
    #------------------------------
    # Enable server logging
    #------------------------------
    async def enablelog(self, ctx, channel: discord.TextChannel):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        config['General']['ServerLog'] = channel.id
        await ctx.send(f"Enabled log on channel {channel}")
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    @enablelog.error
    async def enablelog_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "channel":
                await ctx.send("Your command is missing a required argument: a valid channel (Channel mention or Channel ID)")
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel you are trying to mention or provide ID of doesn't exist")

    @commands.command(aliases = ['dlog'])
    #------------------------------
    # Disable server logging
    #------------------------------
    async def disablelog(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            embed = self.constructResponseEmbedBase("You are not permitted to run this command")
            await ctx.send(embed = embed)
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        config['General']['ServerLog'] = 0
        await ctx.send(f"Disabled log")
        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

    @commands.command()
    #------------------------------
    # Change bot's server-prefix
    #------------------------------
    async def prefix(self, ctx, new_prefix: str = "None"):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)

        if new_prefix == "None":
            embed = self.constructResponseEmbedBase(f"Your current prefix is `{config['General']['Prefix']}`")
            await ctx.send(embed = embed)
            return


        config['General']['Prefix'] = new_prefix

        embed = self.constructResponseEmbedBase(f"You've successfully changed the prefix to `{new_prefix}`")
        await ctx.send(embed = embed)
        await self.serverLog(ctx.guild.id, "prefix_change", f"Prefix was changed to {new_prefix}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(config, f, indent = 4)

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

        if type in ["mod_added", "cnfg_save"]:
            em_color = discord.Colour.from_rgb(67, 181, 129)
        if type in ["delinvos", "prefix_change", "cnfg_switch"]:
            em_color = discord.Colour.from_rgb(250, 166, 26)
        if type in ["mod_deleted", "cnfg_del"]:
            em_color = discord.Colour.from_rgb(240, 71, 71)

        embed = discord.Embed(title = f"**Wormhole Logging**", color = em_color)
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | Wormhole made with \u2764\ufe0f by Nevalicjus")

        if type == "mod_added":
            embed.add_field(name = "Admin Role Added", value = log_msg, inline = False)
        if type == "delinvos":
            embed.add_field(name = "Invocation Deletion", value = log_msg, inline = False)
        if type == "mod_deleted":
            embed.add_field(name = "Admin Role Removed", value = log_msg, inline = False)
        if type == "prefix_change":
            embed.add_field(name = "Prefix Changed", value = log_msg, inline = False)
        if type == "cnfg_save":
            embed.add_field(name = "Saved Config Created", value = log_msg, inline = False)
        if type == "cnfg_switch":
            embed.add_field(name = "Current Config Switch", value = log_msg, inline = False)
        if type == "cnfg_del":
            embed.add_field(name = "Saved Config Deleted", value = log_msg, inline = False)

        log_channel = self.client.get_channel(log_channel_id)
        await log_channel.send(embed = embed)

def setup(client):
    client.add_cog(Other(client))
