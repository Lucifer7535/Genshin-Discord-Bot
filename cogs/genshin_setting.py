import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from typing import Optional
from utility.GenshinApp import genshin_app


class Setting(commands.Cog, name='設定'):
    def __init__(self, bot):
        self.bot = bot

    # 提交Cookie的表單
    class CookieModal(discord.ui.Modal, title='提交Cookie'):
        cookie = discord.ui.TextInput(
            label='Cookie',
            placeholder='Please paste the cookie obtained from the webpage, please use the command "/cookie setting to display the instruction how to obtain the cookie".',
            style=discord.TextStyle.long,
            required=True,
            min_length=100,
            max_length=1500
        )

        async def on_submit(self, interaction: discord.Interaction):
            result = await genshin_app.setCookie(str(interaction.user.id), self.cookie.value)
            await interaction.response.send_message(result, ephemeral=True)

        async def on_error(self, error: Exception, interaction: discord.Interaction):
            await interaction.response.send_message('An unknown error occurred', ephemeral=True)

    @app_commands.command(
        name='cookie',
        description='To set a cookie, you must use this command to set a cookie before using it for the first time')
    @app_commands.rename(option='options')
    @app_commands.choices(option=[
        Choice(name='① Display instructions on how to obtain cookies', value=0),
        Choice(name='② Submit the obtained cookie to the bot', value=1),
        Choice(name='③ Display the notification of the use and storage of the bot', value=2)])
    async def slash_cookie(self, interaction: discord.Interaction, option: int):
        if option == 0:
            help_msg = (
                "1. First copy the entire code at the bottom of this article\n"
                "2. PC or mobile phone use Chrome to open Hoyolab login account <https://www.hoyolab.com>\n"
                "3. Enter `java` in the address bar first, then paste the code, make sure the beginning of the URL becomes `javascript:`\n"
                "4. Press Enter, the page will change to display your cookies, select all and copy\n"
                "5. Submit the result here, use: `/cookie setting to submit the obtained cookie`\n"
                "https://imgur.com/a/C4l67BW")
            code_msg = "```script:d=document.cookie; c=d.includes('account_id') || alert('Expired or invalid cookie, please log out and log in again!'); c && document.write( d)```"
            await interaction.response.send_message(content=help_msg)
            await interaction.followup.send(content=code_msg)
        elif option == 1:
            await interaction.response.send_modal(self.CookieModal())
        elif option == 2:
            msg = ('· The content of the cookie contains your personal identification code, not the account number and password\n'
                   '· Therefore, it cannot be used to log in to the game or change the account password. The content of the cookie looks like this:'
                   '`ltoken=xxxx ltuid=1234 cookie_token=yyyy account_id=1122`\n'
                   '· Bot saves and uses cookies in order to obtain your Genshin information and provide services on the Hoyolab website\n'
                   '· The Bot saves the data in the independent environment of the cloud host, and only connects to the Discord and Hoyolab servers\n'
                   '· For more detailed instructions, you can click on the personal file of the Bot to view the Baja description text. If you still have doubts, please do not use the Bot\n'
                   '· When submitting a cookie to Bot, it means that you have agreed to Bot to save and use your information\n'
                   '·You can delete the data saved in the helper at any time, please use the `/cleardata` command\n')
            embed = discord.Embed(
                title='Bot Cookie Usage and Storage Notice', description=msg)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='uid',
        description='Cancel')
    @app_commands.describe(uid='Please enter the UID of the main character of "Genshin Impact" to be saved')
    async def slash_uid(self, interaction: discord.Interaction, uid: int):
        await interaction.response.defer(ephemeral=True)
        result = await genshin_app.setUID(str(interaction.user.id), str(uid), check_uid=True)
        await interaction.edit_original_message(content=result)

    # Clear data confirmation button
    class ConfirmButton(discord.ui.View):
        def __init__(self, *, timeout: Optional[float] = 30):
            super().__init__(timeout=timeout)
            self.value = None

        @discord.ui.button(label='No', style=discord.ButtonStyle.grey)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.value = False
            self.stop()

        @discord.ui.button(label='Yes', style=discord.ButtonStyle.red)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.value = True
            self.stop()

    # delete saved profiles
    @app_commands.command(
        name='cleardata',
        description='Delete all personal data of the user saved in the Bot')
    async def slash_clear(self, interaction: discord.Interaction):
        view = self.ConfirmButton()
        await interaction.response.send_message('Are you sure you want to delete?', view=view, ephemeral=True)

        await view.wait()
        if view.value == True:
            result = genshin_app.clearUserData(str(interaction.user.id))
            await interaction.edit_original_message(content=result, view=None)
        else:
            await interaction.edit_original_message(content='Command Cancelled', view=None)


async def setup(client: commands.Bot):
    await client.add_cog(Setting(client))
