from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

router = Router()

@router.message(CommandStart())
async def command_start(message: Message):
    await message.answer("👋 Привет! Я бот для учёта продаж.\nНапиши /help, чтобы узнать, что я умею.")

@router.message(Command("help"))
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
