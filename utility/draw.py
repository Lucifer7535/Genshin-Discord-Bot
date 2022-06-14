import genshin
import random
from urllib import request
from PIL import Image, ImageFont, ImageDraw
from typing import Tuple
from io import BytesIO
from pathlib import Path
from utility.utils import getServerName


def drawAvatar(img: Image.Image, avatar: Image.Image, pos: Tuple[float, float]):
    """Draw your profile picture in a circle"""
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(((0, 0), avatar.size), fill=255)
    img.paste(avatar, pos, mask=mask)


def drawRoundedRect(img: Image.Image, pos: Tuple[float, float, float, float], **kwargs):
    """Draw a semi-transparent rounded rectangle"""
    transparent = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent, 'RGBA')
    draw.rounded_rectangle(pos, **kwargs)
    img.paste(Image.alpha_composite(img, transparent))


def drawText(img: Image.Image, pos: Tuple[float, float], text: str, font: str, size: int, fill, anchor=None):
    """Print text on the picture"""
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(f'data/font/{font}', size)
    draw.text(pos, text, fill, font, anchor=anchor)


def drawRecordCard(avatar_bytes: bytes, record_card: genshin.models.RecordCard, user_stats: genshin.models.PartialGenshinUserStats) -> BytesIO:
    """Make a personal record card

     ------
     Parameters
     avatar_bytes `bytes`: Discord user's avatar image, passed in bytes
     record_card `RecordCard`: Record card data obtained from Hoyolab
     user_stats `PartialGenshinUserStats`: User game records from Hoyolab
     ------
     Returns
     `BytesIO`: The created image is stored in memory, and the file pointer is returned. Before accessing, `seek(0)` is required.
     """
    img = Image.open(f'data/image/record_card/{random.randint(1, 12)}.jpg')
    img = img.convert('RGBA')

    avatar = avatar = Image.open(BytesIO(avatar_bytes)).resize((250, 250))
    drawAvatar(img, avatar, (70, 210))

    drawRoundedRect(img, (340, 270, 990, 460), radius=30, fill=(0, 0, 0, 120))
    drawRoundedRect(img, (90, 520, 990, 1730), radius=30, fill=(0, 0, 0, 120))

    white = (255, 255, 255, 255)
    grey = (230, 230, 230, 255)

    drawText(img, (665, 335), record_card.nickname,
             'SourceHanSerifTC-Bold.otf', 88, white, 'mm')
    drawText(img, (665, 415), f'{getServerName(record_card.server)}  Lv.{record_card.level}  UID:{record_card.uid}',
             'SourceHanSansTC-Medium.otf', 40, white, 'mm')

    s = user_stats.stats
    stat_list = [(s.days_active, 'Days Active'), (s.achievements, 'Achievements'), (s.characters, 'Characters'),
                 (s.anemoculi, 'Anemoculus'), (s.geoculi,
                                               'Geoculus'), (s.electroculi, 'Electroculus'),
                 (s.unlocked_waypoints, '\nUnlocked\nWaypoints'), (s.unlocked_domains,
                                                                   '\nUnlocked\nDomains'), (s.spiral_abyss, '\nSpiral\nAbyss'),
                 (s.luxurious_chests, '\nLuxurious\nChests'), (s.precious_chests,
                                                               '\nPrecious\nChests'), (s.exquisite_chests, '\nExquisite\nChests'),
                 (s.common_chests, '\nCommon\nChests'), (s.remarkable_chests, '\nRemarkable\nChests')]

    for n, stat in enumerate(stat_list):
        column = int(n % 3)
        row = int(n / 3)
        drawText(img, (245 + column * 295, 630 + row * 230),
                 str(stat[0]), 'SourceHanSansTC-Bold.otf', 80, white, 'mm')
        drawText(img, (245 + column * 295, 700 + row * 230),
                 str(stat[1]), 'SourceHanSansTC-Regular.otf', 40, grey, 'mm')

    img = img.convert('RGB')
    fp = BytesIO()
    img.save(fp, 'jpeg', optimize=True, quality=50)
    return fp


def drawCharacter(img: Image.Image, character: genshin.models.AbyssCharacter, size: Tuple[int, int], pos: Tuple[float, float]):
    """Draw character avatar, including background frame, character level

     ------
     Parameters
     character `AbyssCharacter`: character profile
     size `Tuple[int, int]`: background box size
     pos `Tuple[float, float]`: the upper left corner position to be drawn
     """
    background = Image.open(
        f'data/image/character/char_{character.rarity}star_bg.png').convert('RGBA').resize(size)
    avatar_file = Path(f'data/image/character/{character.id}.png')
    # If there is no image file locally, download it from the URL
    if avatar_file.exists() == False:
        request.urlretrieve(
            character.icon, f'data/image/character/{character.id}.png')
    avatar = Image.open(avatar_file).resize((size[0], size[0]))
    img.paste(background, pos, background)
    img.paste(avatar, pos, avatar)


def drawAbyssStar(img: Image.Image, number: int, size: Tuple[int, int], pos: Tuple[float, float]):
    """Draw the number of stars in the abyss

     ------
     Parameters
     number `int`: number of stars
     size `Tuple[int, int]`: the size of a single star
     pos `Tuple[float, float]`: the center position, the star will be automatically centered
     """
    star = Image.open(
        f'data/image/spiral_abyss/star.png').convert('RGBA').resize(size)
    pad = 5
    upper_left = (pos[0] - number / 2 * size[0] -
                  (number - 1) * pad, pos[1] - size[1] / 2)
    for i in range(0, number):
        img.paste(
            star, (int(upper_left[0] + i * (size[0] + 2 * pad)), int(upper_left[1])), star)


def drawAbyssCard(abyss: genshin.models.SpiralAbyss) -> BytesIO:
    """Draw the abyss floor record map, including the number of stars in each room and the roles and levels used in the upper and lower halves

     ------
     Parameters
     abyss `SpiralAbyss`: Deep Spiral data from Hoyolab
     ------
     Returns
     `BytesIO`: The created image is stored in memory, and the file pointer is returned. Before accessing, `seek(0)` is required.
     """
    img = Image.open('data/image/spiral_abyss/background_blur.jpg')
    img = img.convert('RGBA')

    character_size = (172, 210)
    character_pad = 8
    for floor in abyss.floors:
        if floor is not abyss.floors[-1]:
            continue
        # show the depth of the abyss
        drawText(img, (1050, 145), f'{floor.floor}',
                 'SourceHanSansTC-Bold.otf', 85, (50, 50, 50), 'mm')
        # The number of chambers
        for i, chamber in enumerate(floor.chambers):
            # Display the number of stars in this chambers
            drawAbyssStar(img, chamber.stars, (70, 70), (1050, 500 + i * 400))
           # upper and lower half chambers
            for j, battle in enumerate(chamber.battles):
                middle = 453 + j * 1196
                left_upper = (int(middle - len(battle.characters) / 2 * character_size[0] - (
                    len(battle.characters) - 1) * character_pad), 395 + i * 400)
                for k, character in enumerate(battle.characters):
                    x = left_upper[0] + k * \
                        (character_size[0] + 2 * character_pad)
                    y = left_upper[1]
                    drawCharacter(img, character, (172, 210), (x, y))
                    drawText(img, (x + character_size[0] / 2, y + character_size[1] * 0.90),
                             f'{character.level}級', 'SourceHanSansTC-Regular.otf', 30, (50, 50, 50), 'mm')
    img = img.convert('RGB')
    fp = BytesIO()
    img.save(fp, 'jpeg', optimize=True, quality=40)
    return fp
