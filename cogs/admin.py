import discord
import random
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from pathlib import Path
from utility.utils import log
from utility.config import config


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.presence_string: list[str] = ['Genshin']
        self.change_presence.start()

    # Sync Slash commands to global or current server
    @app_commands.command(name='sync', description='Sync Slash commands to global or current server')
    @app_commands.rename(area='scope')
    @app_commands.choices(area=[Choice(name='current server', value=0), Choice(name='global server', value=1)])
    async def sync(self, interaction: discord.Interaction, area: int = 0):
        if area == 0:  # Copy the global command, sync to the current server, no need to wait
            self.bot.tree.copy_global_to(guild=interaction.guild)
            result = await self.bot.tree.sync(guild=interaction.guild)
        else:  # Synchronize to the global domain, wait for an hour
            result = await self.bot.tree.sync()

        msg = f'The following commands have been synced to {"all" if area == 1 else "current"} server\n{"、".join(cmd.name for cmd in result)}'
        log.info(f'[command][Admin]sync(area={area}): {msg}')
        await interaction.response.send_message(msg)

    # broadcast message to all servers
    @app_commands.command(name='broadcast', description='broadcast message to all servers')
    @app_commands.rename(message='message')
    async def broadcast(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        count = 0
        for guild in self.bot.guilds:
            # Find the first available channel to send a message
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    try:
                        await channel.send(message)
                    except Exception as e:
                        log.error(
                            f'[exception][Admin]broadcast: channel failed to send message [server]{guild} [exception]{e}')
                        continue
                    else:
                        count += 1
                        break
        await interaction.edit_original_message(content=f'broadcast message to {count} / {len(self.bot.guilds)} server')

    # Display robot related status
    @app_commands.command(name='status', description='show helper status')
    @app_commands.choices(option=[
        Choice(name='Delay', value=0),
        Choice(name='Number of connected servers', value=1),
        Choice(name='connected server name', value=2)])
    async def status(self, interaction: discord.Interaction, option: int):
        if option == 0:
            await interaction.response.send_message(f'Delay：{round(self.bot.latency*1000)} millisecond')
        elif option == 1:
            await interaction.response.send_message(f'connected {len(self.bot.guilds)} servers')
        elif option == 2:
            await interaction.response.defer()
            names = [guild.name for guild in self.bot.guilds]
            for i in range(0, len(self.bot.guilds), 100):
                msg = '、'.join(names[i: i + 100])
                embed = discord.Embed(
                    title=f'connected server name({i + 1})', description=msg)
                await interaction.followup.send(embed=embed)

    # use system commands
    @app_commands.command(name='system', description='Use system commands')
    @app_commands.rename(option='options', param='parameter')
    @app_commands.choices(option=[Choice(name='reload', value=0), Choice(name='presence', value=1)])
    async def system(self, interaction: discord.Interaction, option: int, param: str = None):
        # Reload cogs
        if option == 0:
            if param != None:
                try:
                    await self.bot.reload_extension(f'cogs.{param}')
                except Exception as e:
                    log.error(f'[exception][Admin]system reload {param}: {e}')
                    await interaction.response.send_message(f'[exception][Admin]system reload {param}: {e}')
                else:
                    await interaction.response.send_message(f'command set {param} reload complete')
            else:
                # Load all cogs from cogs folder
                try:
                    for filepath in Path('./cogs').glob('**/*.py'):
                        cog_name = Path(filepath).stem
                        await self.bot.reload_extension(f'cogs.{cog_name}')
                except Exception as e:
                    log.error(f'[exception][Admin]system reload all: {e}')
                    await interaction.response.send_message(f'[exception][Admin]system reload all: {e}')
                else:
                    await interaction.response.send_message('All instruction set reload completed')
        # Change presence string
        elif option == 1:
            self.presence_string = param.split(',')
            await interaction.response.send_message(f'Presence list changed to：{self.presence_string}')

    @tasks.loop(minutes=5)
    async def change_presence(self):
        l = len(self.presence_string)
        n = random.randint(0, l)
        if n < l:
            await self.bot.change_presence(activity=discord.Game(self.presence_string[n]))
        elif n == l:
            await self.bot.change_presence(activity=discord.Game(f'{len(self.bot.guilds)} servers'))

    @change_presence.before_loop
    async def before_change_presence(self):
        await self.bot.wait_until_ready()

    # Test if the server has the scope of applications.commands
    async def __hasAppCmdScope(self, guild: discord.Guild) -> bool:
        try:
            await self.bot.tree.sync(guild=guild)
        except discord.Forbidden:
            return False
        except Exception as e:
            log.error(
                f'[exception][Admin]Admin > __hasAppCmdScope: [server]{guild} [Exceptions]{e}')
            return False
        else:
            return True


async def setup(client: commands.Bot):
    await client.add_cog(Admin(client), guild=discord.Object(id=config.test_server_id))
