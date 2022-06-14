import asyncio
import json
import discord
import genshin
from datetime import datetime, timedelta
from typing import Sequence, Union, Tuple
from .emoji import emoji
from .utils import log, getCharacterName, trimCookie, getServerName, getDayOfWeek, user_last_use_time
from .config import config


class GenshinApp:
    def __init__(self) -> None:
        try:
            with open('data/user_data.json', 'r', encoding="utf-8") as f:
                self.__user_data: dict[str, dict[str, str]] = json.load(f)
        except:
            self.__user_data: dict[str, dict[str, str]] = {}

    async def setCookie(self, user_id: str, cookie: str) -> str:
        """Set user cookies

        ------
        Parameters
         user_id `str`: User Discord ID
         cookie `str`: Hoyolab cookie
        ------
        Returns
        `str`: the message to reply to the user
        """
        log.info(f'[command][{user_id}]setCookie: cookie={cookie}')
        user_id = str(user_id)
        cookie = trimCookie(cookie)
        if cookie == None:
            return f'Invalid cookie, please re-enter (enter `/cookie settings` to display instructions)'
        client = genshin.Client(lang='en-us')
        client.set_cookies(cookie)
        try:
            accounts = await client.get_game_accounts()
        except genshin.errors.GenshinException as e:
            log.info(
                f'[exception][{user_id}]setCookie: [retcode]{e.retcode} [Exceptions]{e.original}')
            result = e.original
        else:
            if len(accounts) == 0:
                log.info(f'[info][{user_id}]setCookie: No roles in account')
                result = 'There is no role in the account, cancel the setting of cookies'
            else:
                self.__user_data[user_id] = {}
                self.__user_data[user_id]['cookie'] = cookie
                log.info(
                    f'[info][{user_id}]setCookie: Cookie set successfully')

                if len(accounts) == 1 and len(str(accounts[0].uid)) == 9:
                    await self.setUID(user_id, str(accounts[0].uid))
                    result = f'Cookie has been set, role UID: {accounts[0].uid} has been saved!'
                else:
                    result = f'There are {len(accounts)} roles in the account\n```'
                    for account in accounts:
                        result += f'UID:{account.uid} Level: {account.level} Character Name: {account.nickname}\n'
                    result += f'```\nPlease enter the UID of the main character of Genshin Impact to be saved'
                    self.__saveUserData()
        finally:
            return result

    async def setUID(self, user_id: str, uid: str, *, check_uid: bool = False) -> str:
        """Set the UID of Account, and save the specified UID when there are multiple characters in the account
        ------
        Parameters
        user_id `str`: User Discord ID
         uid `str`: The UID of Genshin Impact to save
         check_uid `bool`: `True` means to check whether this UID is valid, `False` means to store directly without checking
        ------
        Returns
        `str`: the message to reply to the user
        """
        log.info(
            f'[command][{user_id}]setUID: uid={uid}, check_uid={check_uid}')
        if not check_uid:
            self.__user_data[user_id]['uid'] = uid
            self.__saveUserData()
            return f'Role UID: {uid} set up'
        check, msg = self.checkUserData(user_id, checkUID=False)
        if check == False:
            return msg
        if len(uid) != 9:
            return f'The UID length is wrong, please enter the correct UID of Genshin Impact'

        client = self.__getGenshinClient(user_id)
        try:
            accounts = await client.get_game_accounts()
        except Exception as e:
            log.error(f'[exception][{user_id}]setUID: {e}')
            return 'Failed to verify account information, please reset cookies or try again later'
        else:
            if int(uid) in [account.uid for account in accounts]:
                self.__user_data[user_id]['uid'] = uid
                self.__saveUserData()
                log.info(f'[info][{user_id}]setUID: {uid} has been set')
                return f'Character UID: {uid} has been set'
            else:
                log.info(
                    f'[info][{user_id}]setUID: Could not find the character data for this UID')
                return f'The character information of the UID cannot be found, please confirm whether the input is correct'

    async def getRealtimeNote(self, user_id: str, *, schedule=False) -> Union[None, str, discord.Embed]:
        """Obtain user instant notes (resin, Dongtianbao money, parameter quality changer, dispatch, daily, weekly)

        ------
        Parameters
         user_id `str`: User Discord ID
         schedule `bool`: Whether to check resin for scheduling, when set to `True`, the instant note result will only be returned when the resin exceeds the set standard
         ------
         Returns
         `None | str | Embed`: When the resin is automatically checked, `None` is returned if it does not overflow normally; an error message `str` is returned when an exception occurs, and the query result `discord.Embed` is returned under normal conditions
        """
        if not schedule:
            log.info(f'[command][{user_id}]getRealtimeNote')
        check, msg = self.checkUserData(
            user_id, update_use_time=(not schedule))
        if check == False:
            return msg

        uid = self.__user_data[user_id]['uid']
        client = self.__getGenshinClient(user_id)
        try:
            notes = await client.get_genshin_notes(int(uid))
        except genshin.errors.DataNotPublic:
            log.info(f'[exception][{user_id}]getRealtimeNote: DataNotPublic')
            return 'The instant note function is not enabled, please enable the instant note function from the Hoyolab website or app first'
        except genshin.errors.InvalidCookies as e:
            log.info(
                f'[exception][{user_id}]getRealtimeNote: [retcode]{e.retcode} [exception message]{e.original}')
            return 'Cookie has expired, please reset the cookie'
        except genshin.errors.GenshinException as e:
            log.info(
                f'[exception][{user_id}]getRealtimeNote: [retcode]{e.retcode} [exception message]{e.original}')
            return e.original
        except Exception as e:
            log.error(f'[exception][{user_id}]getRealtimeNote: {e}')
            return str(e)
        else:
            if schedule == True and notes.current_resin < config.auto_check_resin_threshold:
                return None
            else:
                msg = f'{getServerName(uid[0])} {uid.replace(uid[3:-3], "***", 1)}\n'
                msg += f'--------------------\n'
                msg += self.__parseNotes(notes, shortForm=schedule)
                # According to the amount of resin, with 80 as the dividing line, the embed color changes from green (0x28c828) to yellow (0xc8c828), and then to red (0xc82828)
                r = notes.current_resin
                color = 0x28c828 + 0x010000 * \
                    int(0xa0 * r / 80) if r < 80 else 0xc8c828 - \
                    0x000100 * int(0xa0 * (r - 80) / 80)
                embed = discord.Embed(description=msg, color=color)
                return embed

    async def redeemCode(self, user_id: str, code: str) -> str:
        """Use the specified redemption code for the user

         ------
         Parameters
         user_id `str`: User Discord ID
         code `str`: Hoyolab redemption code
         ------
         Returns
         `str`: the message to reply to the user
        """
        log.info(f'[command][{user_id}]redeemCode: code={code}')
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        client = self.__getGenshinClient(user_id)
        try:
            await client.redeem_code(code, int(self.__user_data[user_id]['uid']))
        except genshin.errors.GenshinException as e:
            log.info(
                f'[exception][{user_id}]redeemCode: [retcode]{e.retcode} [exception message]{e.original}')
            result = e.original
        except Exception as e:
            log.error(
                f'[exception][{user_id}]redeemCode: [exception message]{e}')
            result = f'{e}'
        else:
            result = f'Redemption code {code} used successfully!'
        finally:
            return result

    async def claimDailyReward(self, user_id: str, *, honkai: bool = False, schedule=False) -> str:
        """Sign in for users at Hoyolab

         ------
         Parameters
         user_id `str`: User Discord ID
         honkai `bool`: whether to also sign in Honkai 3
         schedule `bool`: whether to check in automatically for the schedule
         ------
         Returns
         `str`: the message to reply to the user
        """
        if not schedule:
            log.info(f'[command][{user_id}]claimDailyReward: honkai={honkai}')
        check, msg = self.checkUserData(
            user_id, update_use_time=(not schedule))
        if check == False:
            return msg
        client = self.__getGenshinClient(user_id)

        game_name = {genshin.Game.GENSHIN: 'Genshin Impact',
                     genshin.Game.HONKAI: 'Honkai Impact 3'}

        async def claimReward(game: genshin.Game, retry: int = 3) -> str:
            try:
                reward = await client.claim_daily_reward(game=game)
            except genshin.errors.AlreadyClaimed:
                return f"{game_name[game]} has received today's rewards!"
            except genshin.errors.GenshinException as e:
                log.info(
                    f'[exception][{user_id}]claimDailyReward: {game_name[game]}[retcode]{e.retcode} [exception message]{e.original}')
                if e.retcode == 0 and retry > 0:
                    await asyncio.sleep(0.5)
                    return await claimReward(game, retry - 1)
                if e.retcode == -10002 and game == genshin.Game.HONKAI:
                    return 'Honkai 3 failed to sign in, the character information was not queried, please confirm whether the captain has bound the new HoYoverse pass'
                return f'{game_name[game]}Failed to sign in：[retcode]{e.retcode} [content]{e.original}'
            except Exception as e:
                log.error(
                    f'[exception][{user_id}]claimDailyReward: {game_name[game]}[exception message]{e}')
                return f'{game_name[game]}Failed to sign in：{e}'
            else:
                return f'{game_name[game]}Sign in today successfully, get {reward.amount}x {reward.name}！'

        result = await claimReward(genshin.Game.GENSHIN)
        if honkai:
            result = result + ' ' + await claimReward(genshin.Game.HONKAI)

        # Hoyolab community check-in
        try:
            await client.check_in_community()
        except genshin.errors.GenshinException as e:
            log.info(
                f'[exception][{user_id}]claimDailyReward: Hoyolab[retcode]{e.retcode} [exception message]{e.original}')
        except Exception as e:
            log.error(
                f'[exception][{user_id}]claimDailyReward: Hoyolab[exception message]{e}')

        return result

    async def getSpiralAbyss(self, user_id: str, previous: bool = False) -> Union[str, genshin.models.SpiralAbyss]:
        """Get the information of the deep spiral

         ------
         Parameters
         user_id `str`: User Discord ID
         previous `bool`: `True` to query the information of the previous issue, `False` to query the information of the current issue
         ------
         Returns
         `Union[str, SpiralAbyss]`: return error message `str` when exception occurs, return query result `SpiralAbyss` under normal conditions
         """
        log.info(f'[command][{user_id}]getSpiralAbyss: previous={previous}')
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        client = self.__getGenshinClient(user_id)
        try:
            abyss = await client.get_genshin_spiral_abyss(int(self.__user_data[user_id]['uid']), previous=previous)
        except genshin.errors.GenshinException as e:
            log.error(
                f'[exception][{user_id}]getSpiralAbyss: [retcode]{e.retcode} [exception message]{e.original}')
            return e.original
        except Exception as e:
            log.error(
                f'[exception][{user_id}]getSpiralAbyss: [exception message]{e}')
            return f'{e}'
        else:
            return abyss

    async def getTravelerDiary(self, user_id: str, month: int) -> Union[str, discord.Embed]:
        """Get user traveler's notes

         ------
         Parameters:
         user_id `str`: User Discord ID
         month `int`: the month to query
         ------
         Returns:
         `Union[str, discord.Embed]`: return error message `str` when exception occurs, return query result `discord.Embed` under normal conditions
         """
        log.info(f'[command][{user_id}]getTravelerDiary: month={month}')
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        client = self.__getGenshinClient(user_id)
        try:
            diary = await client.get_diary(int(self.__user_data[user_id]['uid']), month=month)
        except genshin.errors.GenshinException as e:
            log.error(
                f'[exception][{user_id}]getTravelerDiary: [retcode]{e.retcode} [exception message]{e.original}')
            result = e.original
        except Exception as e:
            log.error(
                f'[exception][{user_id}]getTravelerDiary: [exception message]{e}')
            result = f'{e}'
        else:
            d = diary.data
            result = discord.Embed(
                title=f"{diary.nickname} Traveler's Notes：{month} month",
                description=f"Primogem's income compared to last month {'increased by' if d.primogems_rate > 0 else 'decreased by'} {abs(d.primogems_rate)}%，\nMora income compared to last month {'increased by' if d.mora_rate > 0 else 'decreased by'} {abs(d.mora_rate)}%",
                color=0xfd96f4
            )
            result.add_field(
                name='Obtained this month',
                value=f'{emoji.items.primogem}Primogems：{d.current_primogems} ({round(d.current_primogems/160)}{emoji.items.intertwined_fate})　\nLast month Primogems：{d.last_primogems} ({round(d.last_primogems/160)}{emoji.items.intertwined_fate})\n'
                f'{emoji.items.mora}Mora：{format(d.current_mora, ",")}　\nLast Month Mora：{format(d.last_mora, ",")}',
                inline=False
            )
            # Divide the primogems composition into two fields
            for i in range(0, 2):
                msg = ''
                length = len(d.categories)
                for j in range(round(length/2*i), round(length/2*(i+1))):
                    msg += f'{d.categories[j].name[0:15]}：{d.categories[j].percentage}%\n'
                result.add_field(
                    name=f'Primogems Income Composition ({i+1})', value=msg, inline=True)
        finally:
            return result

    async def getRecordCard(self, user_id: str) -> Union[str, Tuple[genshin.models.RecordCard, genshin.models.PartialGenshinUserStats]]:
        """Get user record card

         ------
         Parameters:
         user_id `str`: User Discord ID
         ------
         Returns:
         `str | (RecordCard, PartialGenshinUserStats)`: Error message `str` is returned when an exception occurs, and query results are returned under normal conditions `(RecordCard, PartialGenshinUserStats)`
         """
        log.info(f'[command][{user_id}]getRecordCard')
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        client = self.__getGenshinClient(user_id)
        try:
            cards = await client.get_record_cards()
            userstats = await client.get_partial_genshin_user(int(self.__user_data[user_id]['uid']))
        except genshin.errors.GenshinException as e:
            log.error(
                f'[exception][{user_id}]getRecordCard: [retcode]{e.retcode} [exception message]{e.original}')
            return e.original
        except Exception as e:
            log.error(
                f'[exception][{user_id}]getRecordCard: [exception message]{e}')
            return str(e)
        else:
            for card in cards:
                if card.uid == int(self.__user_data[user_id]['uid']):
                    return (card, userstats)
            return "Can't find Genshin record card"

    async def getCharacters(self, user_id: str) -> Union[str, Sequence[genshin.models.Character]]:
        """Get all the role data of the user

         ------
         Parameters:
         user_id `str`: User Discord ID
         ------
         Returns:
         `str | Sequence[Character]`: When an exception occurs, the error message `str` is returned, and the query result `Sequence[Character]` is returned under normal conditions.
         """
        log.info(f'[command][{user_id}]getCharacters')
        check, msg = self.checkUserData(user_id)
        if check == False:
            return msg
        client = self.__getGenshinClient(user_id)
        try:
            characters = await client.get_genshin_characters(int(self.__user_data[user_id]['uid']))
        except genshin.errors.GenshinException as e:
            log.error(
                f'[exception][{user_id}]getCharacters: [retcode]{e.retcode} [exception message]{e.original}')
            return e.original
        except Exception as e:
            log.error(
                f'[exception][{user_id}]getCharacters: [exception message]{e}')
            return str(e)
        else:
            return characters

    def checkUserData(self, user_id: str, *, checkUID=True, update_use_time=True) -> Tuple[bool, str]:
        """Check whether user-related information has been saved in the database

         ------
         Parameters
         user_id `str`: User Discord ID
         checkUID `bool`: whether to check UID
         update_use_time `bool`: whether to update the user's last use time
         ------
         Returns
         `bool`: `True` check succeeds, the data exists in the database; `False` check fails, the data does not exist in the database
         `str`: message to the user when the check fails
         """
        if user_id not in self.__user_data.keys():
            log.info(f'[info][{user_id}]checkUserData: User not found')
            return False, f'The user cannot be found, please set a cookie first (enter `/cookie setting` to display the description)'
        else:
            if 'cookie' not in self.__user_data[user_id].keys():
                log.info(f'[info][{user_id}]checkUserData: Cookie not found')
                return False, f'Cannot find the cookie, please set the cookie first (enter `/cookie setting` to display the description)'
            if checkUID and 'uid' not in self.__user_data[user_id].keys():
                log.info(
                    f'[info][{user_id}]checkUserData: Could not find role UID')
                return False, f'Cannot find the character UID, please set the UID first (use `/uid setting` to set the UID)'
        if update_use_time:
            user_last_use_time.update(user_id)
        return True, None

    def clearUserData(self, user_id: str) -> str:
        """Permanently delete user data from the database

         ------
         Parameters
         user_id `str`: User Discord ID
         ------
         Returns:
         `str`: the message to reply to the user
         """
        log.info(f'[command][{user_id}]clearUserData')
        try:
            del self.__user_data[user_id]
            user_last_use_time.deleteUser(user_id)
        except:
            return 'Deletion failed, user data not found'
        else:
            self.__saveUserData()
            return 'User data has been deleted'

    def deleteExpiredUserData(self) -> None:
        """Delete users that have not been used for more than 30 days"""
        now = datetime.now()
        count = 0
        user_data = dict(self.__user_data)
        for user_id in user_data.keys():
            if user_last_use_time.checkExpiry(user_id, now, 30) == True:
                self.clearUserData(user_id)
                count += 1
        log.info(
            f'[info][System]deleteExpiredUserData: {len(user_data)} users checked, {count} expired users deleted')

    def parseAbyssOverview(self, abyss: genshin.models.SpiralAbyss) -> discord.Embed:
        """Analyze the abyss overview data, including date, number of layers, number of battles, total number of stars...etc.

         ------
         Parameters
         abyss `SpiralAbyss`: Deep Spiral Information
         ------
         Returns
         `discord.Embed`: discord embed format
         """
        result = discord.Embed(
            description=f'The record in the {abyss.season} period of spiral abyss,({abyss.start_time.astimezone().strftime("%Y.%m.%d")} ~ {abyss.end_time.astimezone().strftime("%Y.%m.%d")})', color=0x6959c1)

        def get_char(c): return ' ' if len(
            c) == 0 else f'{getCharacterName(c[0])}：{c[0].value}'
        result.add_field(
            name=f'Deepest reach：{abyss.max_floor}　Number of battles：{"👑" if abyss.total_stars == 36 and abyss.total_battles == 12 else abyss.total_battles}　★：{abyss.total_stars}',
            value=f'[Most Kills] {get_char(abyss.ranks.most_kills)}\n'
            f'[Strongest Strike] {get_char(abyss.ranks.strongest_strike)}\n'
            f'[Most Damage Taken] {get_char(abyss.ranks.most_damage_taken)}\n'
            f'[Most Burst Used(Q)] {get_char(abyss.ranks.most_bursts_used)}\n'
            f'[Most Skill Used(E)] {get_char(abyss.ranks.most_skills_used)}',
            inline=False
        )
        return result

    def parseAbyssFloor(self, embed: discord.Embed, abyss: genshin.models.SpiralAbyss, full_data: bool = False) -> discord.Embed:
        """Analyze each floor of the abyss, add the number of stars on each floor and the character data used to the embed

         ------
         Parameters
         embed `discord.Embed`: Embed data obtained from the `parseAbyssOverview` function
         abyss `SpiralAbyss`: Deep Spiral Information
         full_data `bool`: `True` means parsing all floors; `False` means parsing only the last level
         ------
         Returns
         `discord.Embed`: discord embed format
         """
        for floor in abyss.floors:
            if full_data == False and floor is not abyss.floors[-1]:
                continue
            for chamber in floor.chambers:
                name = f'{floor.floor}-{chamber.chamber}　★{chamber.stars}'
                # Get the character name of the upper and lower half layers of the abyss
                chara_list = [[], []]
                for i, battle in enumerate(chamber.battles):
                    for chara in battle.characters:
                        chara_list[i].append(getCharacterName(chara))
                value = f'[{".".join(chara_list[0])}]／\n[{".".join(chara_list[1])}]'
                embed.add_field(name=name, value=value)
        return embed

    def parseCharacter(self, character: genshin.models.Character) -> discord.Embed:
        """Analyze characters, including zodiac, level, favor, weapon, holy relic

         ------
         Parameters
         character `Character`: character profile
         ------
         Returns
         `discord.Embed`: discord embed format
        """
        color = {'pyro': 0xfb4120, 'electro': 0xbf73e7, 'hydro': 0x15b1ff,
                 'cryo': 0x70daf1, 'dendro': 0xa0ca22, 'anemo': 0x5cd4ac, 'geo': 0xfab632}
        embed = discord.Embed(color=color.get(character.element.lower()))
        embed.set_thumbnail(url=character.icon)
        embed.add_field(name=f'★{character.rarity} {character.name}', inline=True,
                        value=f'Constellation：{character.constellation}\nLevel：Lv. {character.level}\nFriendship：Lv. {character.friendship}')

        weapon = character.weapon
        embed.add_field(name=f'★{weapon.rarity} {weapon.name}', inline=True,
                        value=f'Refinement：{weapon.refinement} \nWeapon level：Lv. {weapon.level}')

        if character.constellation > 0:
            number = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6'}
            msg = '\n'.join(
                [f'C{number[constella.pos]}：{constella.name}' for constella in character.constellations if constella.activated])
            embed.add_field(name='Constellation', inline=False, value=msg)

        if len(character.artifacts) > 0:
            msg = '\n'.join(
                [f'{artifact.pos_name}：{artifact.name} ({artifact.set.name})' for artifact in character.artifacts])
            embed.add_field(name='Artifacts', inline=False, value=msg)

        return embed

    def __parseNotes(self, notes: genshin.models.Notes, shortForm: bool = False) -> str:
        result = ''
        # Original resin
        result += f'{emoji.notes.resin}Current Resin Count：{notes.current_resin}/{notes.max_resin}\n'
        if notes.current_resin >= notes.max_resin:
            recover_time = 'Full!'
        else:
            day_msg = getDayOfWeek(notes.resin_recovery_time)
            recover_time = f'{day_msg} {notes.resin_recovery_time.strftime("%H:%M")}'
        result += f'{emoji.notes.resin}Full Resin Recovery Time：{recover_time}\n'
        # Daily, Weekly
        if not shortForm:
            result += f'{emoji.notes.commission}Daily Commissioned Tasks: {notes.completed_commissions} Completed\n'
            result += f'{emoji.notes.enemies_of_note}Weekly boss discount: {notes.remaining_resin_discounts} times remaining\n'
        result += f'--------------------\n'
        # realm money recovery time
        result += f'{emoji.notes.realm_currency}Current Realm Currency：{notes.current_realm_currency}/{notes.max_realm_currency}\n'
        if notes.max_realm_currency > 0:
            if notes.current_realm_currency >= notes.max_realm_currency:
                recover_time = 'Full!'
            else:
                day_msg = getDayOfWeek(notes.realm_currency_recovery_time)
                recover_time = f'{day_msg} {notes.realm_currency_recovery_time.strftime("%H:%M")}'
            result += f'{emoji.notes.realm_currency}Realm Currency Recovery Time：{recover_time}\n'
        # parameteric transformer remaining time
        if notes.transformer_recovery_time != None:
            t = notes.remaining_transformer_recovery_time
            if t.days > 0:
                recover_time = f'{t.days} days remaining'
            elif t.hours > 0:
                recover_time = f'{t.hours} hours remaining'
            elif t.minutes > 0:
                recover_time = f'{t.minutes} minutes remaining'
            elif t.seconds > 0:
                recover_time = f'{t.seconds} seconds remaining'
            else:
                recover_time = 'Parametric Transformer Usable'
            result += f'{emoji.notes.transformer}The remaining time of the Parametric Transformer：{recover_time}\n'
        # Explore the remaining time of dispatch characters
        if not shortForm:
            result += f'--------------------\n'
            exped_finished = 0
            exped_msg = ''
            for expedition in notes.expeditions:
                exped_msg += f'· {getCharacterName(expedition.character)}'
                if expedition.finished:
                    exped_finished += 1
                    exped_msg += '：completed\n'
                else:
                    day_msg = getDayOfWeek(expedition.completion_time)
                    exped_msg += f' Completion time：{day_msg} {expedition.completion_time.strftime("%H:%M")}\n'
            result += f'Exploration Dispatches Completed：{exped_finished}/{len(notes.expeditions)}\n'
            result += exped_msg

        return result

    def __saveUserData(self) -> None:
        try:
            with open('data/user_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.__user_data, f)
        except:
            log.error(
                '[exception][System]GenshinApp > __saveUserData: Archive write failed')

    def __getGenshinClient(self, user_id: str) -> genshin.Client:
        uid = self.__user_data[user_id].get('uid')
        if uid != None and uid[0] in ['1', '2', '5']:
            client = genshin.Client(
                region=genshin.Region.CHINESE, lang='zh-cn')
        else:
            client = genshin.Client(lang='en-us')
        client.set_cookies(self.__user_data[user_id]['cookie'])
        client.default_game = genshin.Game.GENSHIN
        return client


genshin_app = GenshinApp()
