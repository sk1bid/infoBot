import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.exceptions import TelegramRetryAfter

from database.orm_query import orm_get_media, orm_get_and_increment_coins, orm_add_media, orm_get_and_decrement_coins, \
    can_user_click
from kbds.inline import get_inline_mix_btns

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Создаём экземпляр бота
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = [851690283]

# Создаём диспетчер и регистрируем роутеры
dp = Dispatcher()

engine = session_maker.kw['bind']

# Глобальная блокировка для редактирования сообщений
edit_lock = asyncio.Lock()


@dp.callback_query(F.data.startswith("coin"))
async def coin_callback(callback: types.CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    can_click = await can_user_click(session, user_id)

    if not can_click:
        await callback.answer("Вы уже нажимали кнопку сегодня. Попробуйте завтра.", show_alert=True)
        logging.info(f"Пользователь {user_id} попытался нажать кнопку повторно.")
        return

    async with edit_lock:
        try:
            action = callback.data.split("_")[-1]
            if action == "+":
                media = await orm_get_and_increment_coins(session, 1)
                await callback.answer("Спасибо!")
            elif action == "-":
                media = await orm_get_and_decrement_coins(session, 1)
                await callback.answer("И тебе не хворать!")
            else:
                await callback.answer("Неизвестное действие.", show_alert=True)
                logging.warning(f"Неизвестное действие: {callback.data}")
                return
            if media.coins >= 0:
                keyboard = get_inline_mix_btns(
                    btns={
                        "Написать владельцу 🎭": "https://t.me/cg_skbid",
                        f"🟢 Social Points: {media.coins}": "None",
                        "📛": "coin_-",
                        "✴": "coin_+",
                    },
                )
            else:
                keyboard = get_inline_mix_btns(
                    btns={
                        "Написать владельцу 🎭": "https://t.me/cg_skbid",
                        f"🔴 Social Points: {media.coins}": "None",
                        "📛": "coin_-",
                        "✴": "coin_+",
                    },
                )

            await bot.edit_message_reply_markup(
                chat_id=os.getenv("ID"),
                message_id=media.message_id,
                reply_markup=keyboard
            )
            logging.debug(f"Сообщение ID {media.message_id} обновлено. Монеты: {media.coins}")
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            logging.warning(f"Превышен лимит запросов. Повтор через {retry_after} секунд.")
            await asyncio.sleep(retry_after)
            # Опционально: повторить попытку редактирования сообщения
            try:
                await bot.edit_message_reply_markup(
                    chat_id=os.getenv("ID"),
                    message_id=media.message_id,
                    reply_markup=keyboard
                )
                logging.debug(f"Сообщение ID {media.message_id} успешно обновлено после ожидания.")
            except Exception as ex:
                logging.error(f"Не удалось обновить сообщение после ожидания: {ex}")
        except Exception as e:
            logging.error(f"Неизвестная ошибка в обработчике callback: {e}")
            await callback.answer("Произошла ошибка. Попробуйте позже.", show_alert=True)


async def on_startup(bot: Bot):
    logger.info("Бот запускается...")
    run_param = False
    if run_param:
        await drop_db()
        logger.debug("База данных удалена согласно параметру run_param.")

    await create_db()
    logger.debug("База данных создана.")

    async with session_maker() as session:
        media = await orm_get_media(session, 1)

        keyboard = get_inline_mix_btns(
            btns={
                "Написать владельцу 🎭": "https://t.me/cg_skbid",
                f"Social Points: {0}": "None",
                "📛": "coin_-",
                "✴": "coin_+",
            },
        )
        if media is None:
            text = " "
            try:
                message = await bot.send_message(chat_id=os.getenv('ID'), text=text, reply_markup=keyboard)
                await orm_add_media(session, message_id=message.message_id, coins=0)
                logger.debug(f"Отправлено и добавлено новое media с message ID {message.message_id} и coins=0.")
            except Exception as e:
                logger.error(f"Не удалось отправить или добавить media: {e}")
        else:
            logger.debug(f"Media уже существует: ID={media.id}, Coins={media.coins}")


async def on_shutdown(bot: Bot):
    logger.info('Бот останавливается...')
    try:
        await bot.close()
        logger.debug("Бот успешно закрыт.")
    except Exception as e:
        logger.error(f"Ошибка при закрытии бота: {e}")


async def main():
    # Регистрируем функции, которые будут выполняться при старте и остановке бота
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Регистрируем middleware для работы с базой данных
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    # Удаляем вебхук (если он был установлен) и начинаем polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.debug("Webhook успешно удален.")
    except Exception as e:
        logger.error(f"Ошибка при удалении вебхука: {e}")

    # Начинаем polling
    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Ошибка при запуске polling: {e}")


if __name__ == '__main__':
    asyncio.run(main())
