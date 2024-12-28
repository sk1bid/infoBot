from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Media


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