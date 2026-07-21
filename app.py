from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv
import asyncio

from handler.task import router

from database.db import Base, engine

from handler.help import router as help_router
from handler.start import router as start_router


load_dotenv()

Base.metadata.create_all(bind=engine)


dp = Dispatcher()
dp.include_router(router)
dp.include_router(help_router)
dp.include_router(start_router)


async def main():
    bot = Bot(token=getenv("BOT_TOKEN"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
