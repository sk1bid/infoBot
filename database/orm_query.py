from datetime import datetime, timezone

from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.plugin.plugin_base import logging

from database.models import Media, UserAction


async def orm_add_media(session: AsyncSession, image: str = None, text: str = None, coins: int = 0,
                        message_id: int = None):
    obj = Media(
        image=image,
        text=text,
        coins=coins,
        message_id=message_id
    )
    session.add(obj)
    await session.commit()


async def orm_update_media(session: AsyncSession, media_id: int, image: str = None, text: str = None,
                           coins: int = None, message_id: int = None):
    query = (
        update(Media)
        .where(Media.id == media_id)
        .values(image=image,
                text=text,
                coins=coins,
                message_id=message_id)
    )
    await session.execute(query)
    await session.commit()


async def orm_get_media(session: AsyncSession, media_id: int):
    query = select(Media).where(Media.id == media_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_delete_media(session: AsyncSession, media_id: int):
    await session.execute(delete(Media).where(Media.id == media_id))
    await session.commit()


# New Function to Get Media and Increment Coins
async def orm_get_and_increment_coins(session: AsyncSession, media_id: int):
    """
    Retrieves a Media object by its ID and increments its coins by 1 in a single atomic operation.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session.
        media_id (int): The ID of the media to retrieve and update.

    Returns:
        Media: The updated Media object with incremented coins, or None if not found.
    """
    query = (
        update(Media)
        .where(Media.id == media_id)
        .values(coins=Media.coins + 5)
        .returning(Media)
    )
    result = await session.execute(query)
    await session.commit()
    return result.scalar()


async def orm_get_and_decrement_coins(session: AsyncSession, media_id: int):
    """
    Retrieves a Media object by its ID and increments its coins by 1 in a single atomic operation.

    Args:
        session (AsyncSession): The SQLAlchemy asynchronous session.
        media_id (int): The ID of the media to retrieve and update.

    Returns:
        Media: The updated Media object with incremented coins, or None if not found.
    """
    query = (
        update(Media)
        .where(Media.id == media_id)
        .values(coins=Media.coins - 5)
        .returning(Media)
    )
    result = await session.execute(query)
    await session.commit()
    return result.scalar()


async def can_user_click(session: AsyncSession, user_id: int) -> bool:
    """
    Проверяет, может ли пользователь нажать кнопку (не нажимал ли сегодня).
    """
    try:
        query = select(UserAction).where(UserAction.user_id == user_id)
        result = await session.execute(query)
        user_action = result.scalar_one_or_none()

        if user_action:
            last_action_date = user_action.last_action
            today = datetime.now(timezone.utc).date()
            if last_action_date.date() == today:
                return False  # Пользователь уже нажимал сегодня
            else:
                # Обновляем время последнего действия
                user_action.last_action = datetime.now(timezone.utc)
                await session.commit()
                return True
        else:
            # Создаем новую запись для пользователя
            new_action = UserAction(user_id=user_id, last_action=datetime.now(timezone.utc))
            session.add(new_action)
            await session.commit()
            return True
    except SQLAlchemyError as e:
        logging.error(f"Ошибка при проверке действий пользователя {user_id}: {e}")
        await session.rollback()
        return False
