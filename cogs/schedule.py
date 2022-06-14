import json
import asyncio
import discord
from datetime import datetime
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from utility.config import config
from utility.utils import log, user_last_use_time
from utility.GenshinApp import genshin_app


class Schedule(commands.Cog, name='自動化(BETA)'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.__daily_reward_filename = 'data/schedule_daily_reward.json'
        self.__resin_notifi_filename = 'data/schedule_resin_notification.json'
        try:
            with open(self.__daily_reward_filename, 'r', encoding='utf-8') as f:
                self.__daily_dict: dict[str, dict[str, str]] = json.load(f)
        except:
            self.__daily_dict: dict[str, dict[str, str]] = {}
        try:
            with open(self.__resin_notifi_filename, 'r', encoding='utf-8') as f:
                self.__resin_dict: dict[str, dict[str, str]] = json.load(f)
        except:
            self.__resin_dict: dict[str, dict[str, str]] = {}

        self.schedule.start()

    class ChooseGameButton(discord.ui.View):
        """Select the button to automatically sign in to the game"""

        def __init__(self, author: discord.Member, *, timeout: float = 30):
            super().__init__(timeout=timeout)
            self.value = None
            self.author = author

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.author.id

        @discord.ui.button(label='Genshin Impact', style=discord.ButtonStyle.blurple)
        async def option1(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.value = 'Genshin Impact'
            self.stop()

        @discord.ui.button(label='Honkai Impact3', style=discord.ButtonStyle.blurple)
        async def option2(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            self.value = 'Honkai Impact3'
            self.stop()

    class DailyMentionButton(discord.ui.View):
        """Do you want to tag users for daily check-in?"""

        def __init__(self, author: discord.Member, *, timeout: float = 30):
            super().__init__(timeout=timeout)
            self.value = True
            self.author = author

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user.id == self.author.id

        @discord.ui.button(label='Yes', style=discord.ButtonStyle.blurple)
        async def option1(self, interaction: discord.Interaction, button: discord.ui.button):
            await interaction.response.defer()
            self.value = True
            self.stop()

        @discord.ui.button(label='No', style=discord.ButtonStyle.blurple)
        async def option2(self, interaction: discord.Interaction, button: discord.ui.button):
            await interaction.response.defer()
            self.value = False
            self.stop()

    # Set up automatic scheduling function
    @app_commands.command(
        name='schedule',
        description='Set up automation functions (Hoyolab daily check-in, resin full reminder)')
    @app_commands.rename(function='function', switch='switch')
    @app_commands.describe(
        function='Select the function to automate',
        switch='Choose to turn this feature on or off')
    @app_commands.choices(
        function=[Choice(name='Show instructions for use', value='help'),
                  Choice(name='Daily automatic check-in', value='daily'),
                  Choice(name='Resin full reminder', value='resin')],
        switch=[Choice(name='enable function', value=1),
                Choice(name='disable function', value=0)])
    async def slash_schedule(self, interaction: discord.Interaction, function: str, switch: int):
        log.info(
            f'[command][{interaction.user.id}]schedule(function={function}, switch={switch})')
        if function == 'help':  # 排程功能使用說明
            msg = ('· The schedule will execute the function at a specific time, and the execution result will be pushed to the channel of the set command\n'
                   '· Before setting, please confirm that the bot has the permission to speak in the channel. If the push message fails, the bot will automatically remove the scheduling settings\n'
                   '· To change the push channel, please reset the command once on the new channel\n\n'
                   f'· Daily check-in: Automatic hoyolab check-in between {config.auto_daily_reward_time}~{config.auto_daily_reward_time+1} time every day, before setting, please use the `/daily daily check-in` command to confirm that the bot can help you check in correctly \n'
                   f'· Resin reminder: check every two hours, when the resin exceeds {config.auto_check_resin_threshold}, a reminder will be sent. Before setting, please use the `/notes instant note` command to confirm that the bot can read your resin information\n')
            await interaction.response.send_message(embed=discord.Embed(title='Instructions for using the scheduling function', description=msg))
            return

        # 設定前先確認使用者是否有Cookie資料
        check, msg = genshin_app.checkUserData(str(interaction.user.id))
        if check == False:
            await interaction.response.send_message(msg)
            return
        if function == 'daily':  # 每日自動簽到
            if switch == 1:  # 開啟簽到功能
                choose_game_btn = self.ChooseGameButton(interaction.user)
                await interaction.response.send_message('Please select a game to automatically sign in to:', view=choose_game_btn)
                await choose_game_btn.wait()
                if choose_game_btn.value == None:
                    await interaction.edit_original_message(content='Cancelled', view=None)
                    return

                daily_mention_btn = self.DailyMentionButton(interaction.user)
                await interaction.edit_original_message(content=f'Do you want the bot to tag you ({interaction.user.mention}) when you check in automatically every day?', view=daily_mention_btn)
                await daily_mention_btn.wait()

                # 新增使用者
                self.__add_user(str(interaction.user.id), str(interaction.channel_id),
                                self.__daily_dict, self.__daily_reward_filename, mention=daily_mention_btn.value)
                if choose_game_btn.value == 'Honkai Impact 3':  # 新增崩壞3使用者
                    self.__add_honkai_user(
                        str(interaction.user.id), self.__daily_dict, self.__daily_reward_filename)
                await interaction.edit_original_message(content=f'{choose_game_btn.value} Daily automatic check-in has been turned on, and the bot {"will " if daily_mention_btn.value else "will not "}mention you', view=None)
            elif switch == 0:  # 關閉簽到功能
                self.__remove_user(
                    str(interaction.user.id), self.__daily_dict, self.__daily_reward_filename)
                await interaction.response.send_message('Daily automatic check-in is turned off')
        elif function == 'resin':  # 樹脂額滿提醒
            if switch == 1:  # 開啟檢查樹脂功能
                self.__add_user(str(interaction.user.id), str(
                    interaction.channel_id), self.__resin_dict, self.__resin_notifi_filename)
                await interaction.response.send_message('Resin full reminder is on')
            elif switch == 0:  # 關閉檢查樹脂功能
                self.__remove_user(
                    str(interaction.user.id), self.__resin_dict, self.__resin_notifi_filename)
                await interaction.response.send_message('Resin full reminder is off')

    loop_interval = 10

    @tasks.loop(minutes=loop_interval)
    async def schedule(self):
        now = datetime.now()
        # Automatic check-in at {config.auto_daily_reward_time} points every day
        if now.hour == config.auto_daily_reward_time and now.minute < self.loop_interval:
            log.info(
                '[Schedule][System]schedule: Start of daily automatic check-in')
            # make a copy to avoid conflicts
            daily_dict = dict(self.__daily_dict)
            total, honkai_count = 0, 0
            for user_id, value in daily_dict.items():
                channel = self.bot.get_channel(int(value['channel']))
                has_honkai = False if value.get('honkai') == None else True
                check, msg = genshin_app.checkUserData(
                    user_id, update_use_time=False)
                if channel == None or check == False:
                    self.__remove_user(
                        user_id, self.__daily_dict, self.__daily_reward_filename)
                    continue
                result = await genshin_app.claimDailyReward(user_id, honkai=has_honkai, schedule=True)
                total += 1
                honkai_count += int(has_honkai)
                try:
                    if value.get('mention') == 'False':
                        user = await self.bot.fetch_user(int(user_id))
                        await channel.send(f'[automatic check-in] {user.display_name}：{result}')
                    else:
                        await channel.send(f'[automatic check-in] <@{user_id}> {result}')
                except Exception as e:
                    log.error(
                        f'[Scheduling][{user_id}] Automatic check-in: {e}')
                    self.__remove_user(
                        user_id, self.__daily_dict, self.__daily_reward_filename)
                await asyncio.sleep(config.auto_loop_delay)
            log.info(
                f'[Scheduling][System]schedule: The daily automatic check-in ends, a total of {total} people check in, of which {honkai_count} people also check in Honkai 3')

        # Check resin every 2 hours and stagger with daily check-in times
        if abs(now.hour - config.auto_daily_reward_time) % 2 == 1 and now.minute < self.loop_interval:
            log.info('[schedule][System]schedule: Automatic resin check starts')
            resin_dict = dict(self.__resin_dict)
            count = 0
            for user_id, value in resin_dict.items():
                channel = self.bot.get_channel(int(value['channel']))
                check, msg = genshin_app.checkUserData(
                    user_id, update_use_time=False)
                if channel == None or check == False:
                    self.__remove_user(
                        user_id, self.__resin_dict, self.__resin_notifi_filename)
                    continue
                result = await genshin_app.getRealtimeNote(user_id, schedule=True)
                count += 1
                if result != None:
                    try:
                        if isinstance(result, str):
                            await channel.send(f'<@{user_id}>，An error occurred while automatically checking the resin：{result}')
                        else:
                            await channel.send(f'<@{user_id}>，The resin is (about to) overflow!', embed=result)
                    except:
                        self.__remove_user(
                            user_id, self.__resin_dict, self.__resin_notifi_filename)
                await asyncio.sleep(config.auto_loop_delay)
            log.info(
                f'[schedule][System]schedule: Automatic check of resin end，{count} checked')

        user_last_use_time.save()  # Regularly store the user's last usage time data
        # Delete outdated user data daily
        if now.hour == 1 and now.minute < self.loop_interval:
            genshin_app.deleteExpiredUserData()

    @schedule.before_loop
    async def before_schedule(self):
        await self.bot.wait_until_ready()

    def __add_user(self, user_id: str, channel: str, data: dict, filename: str, *, mention: bool = True) -> None:
        data[user_id] = {}
        data[user_id]['channel'] = channel
        if mention == False:
            data[user_id]['mention'] = 'False'
        self.__saveScheduleData(data, filename)

    def __add_honkai_user(self, user_id: str, data: dict, filename: str) -> None:
        """Join Honkai Impact 3 to sign in to an existing user, please confirm that you already have the user's information before using it"""
        if data.get(user_id) != None:
            data[user_id]['honkai'] = 'True'
            self.__saveScheduleData(data, filename)

    def __remove_user(self, user_id: str, data: dict, filename: str) -> None:
        try:
            del data[user_id]
        except:
            log.info(
                f'[exception][System]Schedule > __remove_user(user_id={user_id}): User does not exist')
        else:
            self.__saveScheduleData(data, filename)

    def __saveScheduleData(self, data: dict, filename: str):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except:
            log.error(
                f'[exception][System]Schedule > __saveScheduleData(filename={filename}): Archive write failed')


async def setup(client: commands.Bot):
    await client.add_cog(Schedule(client))
