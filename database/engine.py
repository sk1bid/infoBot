
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base

engine = create_async_engine(os.getenv('DB_URL'), echo=False)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        # Получаем объект MetaData для управления таблицами
        metadata = Base.metadata

        # Определяем таблицы, которые нужно оставить (не удалять)
        tables_to_exclude = {'admin_exercises', 'banner', 'exercise_category'}

        # Отфильтровываем таблицы, которые нужно удалить
        tables_to_drop = [table for table in metadata.sorted_tables if table.name not in tables_to_exclude]

        # Дропаем все таблицы, кроме исключенных
        if tables_to_drop:
            await conn.run_sync(lambda conn: metadata.drop_all(conn, tables=tables_to_drop))
