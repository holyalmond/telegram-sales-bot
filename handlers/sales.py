from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from google_sheets import add_sale, remove_last_user_sale

router = Router()

@router.message(Command("undo"))
async def command_undo(message: Message):
    success = remove_last_user_sale(message.from_user.id)
    if success:
        await message.answer("↩️ Последняя продажа удалена.")
    else:
        await message.answer("❌ Продажа не найдена или нечего отменять.")

@router.message()
async def handle_message(message: Message):
    text = message.text.strip()
    if " " not in text:
        await message.answer("❗Неверный формат. Пример: Капучино 250")
        return

    *product_parts, price_str = text.split()
    product = " ".join(product_parts)
    price_str = price_str.replace(",", ".")

    try:
        price = float(price_str)
    except ValueError:
        await message.answer("❗Цена должна быть числом.")
        return
    
    date = message.date.date().strftime("%d.%m.%y")
    time = message.date.time().strftime("%H:%M")
    user_id = message.from_user.id
    name = message.from_user.first_name

    add_sale(date, time, product, price, user_id, name)
    await message.reply(f"✅ Продажа записана: {product} - {price}₽")