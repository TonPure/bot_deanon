import asyncio
from config_data.config import Config, load_config
from keyboards import inlines
from keyboards.set_menu import set_main_menu
from handlers import handlers
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

async def main():

    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token,
          parse_mode='HTML')
    dp = Dispatcher()
    
    dp.include_router(handlers.router)
    
    await set_main_menu(bot)
    #handler
    # id = str(message.from_user.first_name)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
