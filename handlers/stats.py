from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from google_sheets import get_top_products

import datetime

router = Router()

@router.message(Command("top_products"))
async def command_top(message: Message, command: CommandObject):
    month = command.args.strip() if command.args else None

    if month is not None:
        try:
            datetime.datetime.strptime(month, "%m.%y")
        except ValueError:
            await message.answer("❗Неверный формат месяца. Пример: <code>/top_products ММ.ГГ</code>", parse_mode="HTML")
            return
    
    top = get_top_products(month)

    if not top or top is None:
        await message.answer("❌ Нет данных за указанный период.")
        return

    result = "🏆 <b>Топ товаров</b>:\n\n"
    for i, (product, count) in enumerate(top, 1):
        result += f"{i}. {product} — {count} шт.\n"

    await message.answer(result, parse_mode="HTML")
