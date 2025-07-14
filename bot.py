from aiogram import Bot, Dispatcher

import asyncio
import logging
import sys

from config import BOT_TOKEN
from handlers import base, sales, reports, export, stats

dp = Dispatcher()

async def main():
    bot = Bot(BOT_TOKEN)

    dp.include_routers(
        base.router,
        reports.router,
        export.router,
        stats.router,
        sales.router
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())