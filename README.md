# Genshin Discord Bot

This bot is a translated version of [Genshin Discord Bot](https://github.com/KT-Yeh/Genshin-Discord-Bot/tree/discord.py_v2.0).<br> It uses development version of discord.py v2.0.

# Genshin-Discord-Bot
[![](https://i.imgur.com/9znFz4X.png)](https://discord.com/api/oauth2/authorize?client_id=978718491471380501&permissions=264192&scope=bot%20applications.commands)<br>
Click the image above or the invitation link: [Bot Invitation Link](https://discord.com/api/oauth2/authorize?client_id=978718491471380501&permissions=264192&scope=bot%20applications.commands) to invite this bot to your server.<br>

Discord Server require someone with administrative rights to invite the Bot.

-->If having any doubts how to use or deploy the bot. Join this [server](https://discord.gg/AX2WmFTFWS)

You can use this Discord bot to directly query various information in Genshin Impact, including:

1. Instant notes, including resin, realm currency, parametric transformer time remaining, exploration dispatched...etc.
2. Query the deep spiral record.
3. Check Traveler's Notes.
4. Personal record card (active days, achievements, characters, anemoculus, geoculus...etc.).
5. Use Hoyolab redemption code.
6. Hoyolab auto check-in every day.
7. Automatic resin check every two hours, push reminder when resin exceeds 145.
8. Using the new slash command, input/automatic pop-up command prompts, no need to remember how to use any commands.

For More Info About the Bot: https://forum.gamer.com.tw/Co.php?bsn=36730&sn=162433

### <u>If you want to create your personal bot then follow these instructions.</u>

## How to Setup the Bot

1. Sign in to your Discord account at [Discord Developer](https://discord.com/developers/applications/).
![](https://i.imgur.com/dbDHEM3.png)
2. Click "New Application" to create an application, enter the desired name and click "Create".
![](https://i.imgur.com/BcJcSnU.png)
3. On the Bot page, click "Add Bot" to add a bot.
![](https://i.imgur.com/lsIgGCi.png)
4. In OAuth2/URL Generator, check "bot", "applications.commands" and "Send Messages" respectively. The URL link generated at the bottom is the robot's invitation link. Open the link to invite the robot to your own test server.![](https://i.imgur.com/y1Ml43u.png)
5. Get the ID required for the configuration file
In General Information, get the Bot's Application ID.
![](https://i.imgur.com/h07q5zT.png)
6. On the Bot page, press "Reset Token" to get the Bot's Token.![](https://i.imgur.com/BfzjewI.png)
7. Right-click on your own Discord server name or icon to copy the server ID 
8. (the copy ID button to show, go to Settings->Advanced->Developer Mode to enable.![](https://i.imgur.com/qEhWTde.png)
9. Fork this repository and also star it.
10. Enter your copied application_id , test_server_id, bot_token in the config.json file in forked repository. Commit changes to config.json.
11. In the forked repository, Download the emojis from emoji folder and upload it to your discord server.
12. After uploading make sure that you have named your custom emojis.
13. Then in the discord channel use the command - `\:emoji_name:`
14. You will get a `<:emoji_name:13123231212323>` emoji id like this
15. Do it for each emoji and fill the respective values in data/emoji.json file in your forked repository.
16. Open the readme.md file and click on edit.
17. `your_forked_repo_link` replace this part with your forked repository link in line 18.
18. Commit changes to readme.md
19. Use the deploy to heroku button to deploy it.
20. After the bot is deployed on heroku.
21. VERY IMPORTANT: Make sure to make forked repository private to prevent people from seeing bot config variables.
22. You Can do this by opening your repository going to settings. Scroll till last and there is a option - change repository visibility.
<br><pre></pre>
<a href="https://heroku.com/deploy?template=your_repo_link">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy">
</a>

## Thanks

Bot Credit Goes to: https://github.com/KT-Yeh/Genshin-Discord-Bot/tree/discord.py_v2.0 <br>
Concept inspired by: https://github.com/Xm798/Genshin-Dailynote-Helper <br>
Genshin API used from: https://github.com/thesadru/genshin.py <br>
Discord API used from: https://github.com/Rapptz/discord.py
