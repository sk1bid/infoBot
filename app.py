import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_media, orm_get_and_increment_coins, orm_add_media, orm_get_and_decrement_coins
from kbds.inline import get_inline_mix_btns

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker

logging.basicConfig(
    level=logging.DEBUG,
)

# Создаём экземпляр бота
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = [851690283]

dp = Dispatcher()

engine = session_maker.kw['bind']


@dp.callback_query(F.data.startswith("coin"))
async def start(callback: types.CallbackQuery, session: AsyncSession):
    if callback.data.split("_")[-1] == "+":
        media = await orm_get_and_increment_coins(session, 1)
        await callback.answer("Спасибо!")
    else:
        media = await orm_get_and_decrement_coins(session, 1)
        await callback.answer("И тебе не хворать!")

    keyboard = get_inline_mix_btns(
        btns={
            "Написать владельцу 🎭": "https://t.me/cg_skbid",
            f"Social Points: {media.coins}": "None",
            "📛": "coin_-",
            "✴": "coin_+",
        },
    )
    await bot.edit_message_reply_markup(
        chat_id=os.getenv("ID"),
        message_id=media.message_id,
        reply_markup=keyboard
    )


async def on_startup(bot: Bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()

    async with session_maker() as session:
        logging.info("Бот запускается...")

        media = await orm_get_media(session, 1)

        keyboard = get_inline_mix_btns(
            btns={
                "Написать владельцу 🎭": "https://t.me/cg_skbid",
                f"Social Points {0}"
                "📛": "coin_-",
                "✴": "coin_+",

            },
        )
        if media is None:
            text = f"А теперь так"
            message = await bot.send_message(chat_id=os.getenv('ID'), text=text, reply_markup=keyboard)
            await orm_add_media(session, message_id=message.message_id)


async def on_shutdown(bot: Bot):
    logging.info('Бот остановлен')
    await bot.close()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.error(f"Ошибка при удалении вебхука: {e}")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
