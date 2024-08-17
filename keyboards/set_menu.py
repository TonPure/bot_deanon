from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon_ru import LEXICON_COMMANDS_RU

# ф-я настройки кнопки menu
async def set_main_menu(bot):
    main_menu_commands = [
        BotCommand(
            command = command,
            description = description
        ) for command, description in LEXICON_COMMANDS_RU.items()
        ]
    await bot.set_my_commands(main_menu_commands)
