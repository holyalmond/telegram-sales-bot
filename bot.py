import asyncio
import logging
import sys
import os
import datetime

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, FSInputFile

from google_sheets import add_sale,remove_last_user_sale, get_report, get_month_summary, get_year_summary, get_top_products, export_sheet_xlsx

from config import BOT_TOKEN

dp = Dispatcher()

#### HANDLERS ####

@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer("👋 Привет! Я бот для учёта продаж.\nНапиши /help, чтобы узнать, что я умею.")

@dp.message(Command("help"))
async def command_help(message: Message):
    await message.answer(
        "🤖 <b>Бот учёта продаж</b>\n\n"
        "📌 <b>Как пользоваться:</b>\n"
        "Просто отправь сообщение в формате:\n"
        "<code>Название Цена</code>\n"
        "Например:\n"
        "👉 <code>Капучино 250</code>\n"
        "👉 <code>Торт Наполеон 145.50</code>\n\n"
        "Допускаются пробелы в названии и цены с точкой или запятой.\n\n"
        "📊 <b>Команды:</b>\n"
        "/start — приветствие\n"
        "/help — справка\n"
        "/report ДД.ММ.ГГ — отчёт за день\n"
        "/today — отчёт за сегодня\n"
        "/month_summary ММ.ГГ — отчёт за месяц\n"
        "/year_summary ГГГГ — отчёт за год\n"
        "/top_products ММ.ГГ — топ товаров за месяц\n"
        "/export — экспорт всей таблицы в Excel\n"
        "/undo — отмена последней продажи\n\n"
        "💡 Все продажи сохраняются в Google Таблицу.",
        parse_mode="HTML"
    )

@dp.message(Command("report"))
async def command_report(message: Message, command: CommandObject):
    date = command.args

    if not date:
        await message.answer("📅 Укажи дату в формате: <code>/report ДД.ММ.ГГ</code>", parse_mode="HTML")
        return

    try:
        datetime.datetime.strptime(date, "%d.%m.%y")
    except ValueError:
        await message.answer("❗Неверный формат даты. Пример: <code>/report ДД.ММ.ГГ</code>", parse_mode="HTML")
        return
    
    sales, amount = get_report(date)
    await message.answer(f"🧾 Отчёт за {date}\nПродаж: {sales}\nСумма: {amount}₽")

@dp.message(Command("today"))
async def command_today(message: Message):
    today = message.date.date().strftime("%d.%m.%y")
    sales, amount = get_report(today)
    await message.answer(f"🧾 Отчёт за {today}\nПродаж: {sales}\nСумма: {amount}₽")

@dp.message(Command("month_summary"))
async def command_month_summary(message: Message, command: CommandObject):
    month = command.args

    if not month:
        await message.answer("📅 Укажи месяц в формате: <code>/summary ММ.ГГ</code>", parse_mode="HTML")
        return

    try:
        datetime.datetime.strptime(month, "%m.%y")
    except ValueError:
        await message.answer("❗Неверный формат месяца. Пример: <code>/summary ММ.ГГ</code>", parse_mode="HTML")
        return
    
    sales, amount = get_month_summary(month)
    await message.answer(f"🧾 Отчёт за {month}\nПродаж: {sales}\nСумма: {amount}₽")

@dp.message(Command("year_summary"))
async def command_year_summary(message: Message, command: CommandObject):
    year = command.args
    if len(str(year)) != 4 or not str(year).isdigit():
        await message.answer("❗ Укажи год в формате <b>гггг</b>, например: <code>/year_summary 2025</code>", parse_mode="HTML")
        return
    
    sales, amount = get_year_summary(year)

    if sales == 0:
        await message.answer(f"📅 За {year} год продаж не найдено.")
    else:
        await message.answer(f"📊 <b>Отчёт за {year} год</b>\nПродаж: <b>{sales}</b>\nСумма: <b>{amount:.2f}₽</b>", parse_mode="HTML")

@dp.message(Command("export"))
async def command_export(message: Message):
    await message.answer("📤 Экспортирую таблицу, подожди секунду...")

    file_path = export_sheet_xlsx()
    if file_path:
        document = FSInputFile(file_path, filename="SalesBot.xlsx")
        await message.answer_document(document=document, caption="🧾 Вот твоя таблица")
        os.remove(file_path)
    else:
        await message.answer("⚠️ Не удалось экспортировать таблицу. Попробуй позже.")

@dp.message(Command("undo"))
async def command_undo(message: Message):
    success = remove_last_user_sale(message.from_user.id)
    if success:
        await message.answer("↩️ Последняя продажа удалена.")
    else:
        await message.answer("❌ Продажа не найдена или нечего отменять.")

@dp.message(Command("top_products"))
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

@dp.message()
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

#### START ####

async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())