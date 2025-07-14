from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from google_sheets import get_report, get_month_summary, get_year_summary

import datetime

router = Router()

@router.message(Command("report"))
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

@router.message(Command("today"))
async def command_today(message: Message):
    today = message.date.date().strftime("%d.%m.%y")
    sales, amount = get_report(today)
    await message.answer(f"🧾 Отчёт за {today}\nПродаж: {sales}\nСумма: {amount}₽")

@router.message(Command("month_summary"))
async def command_month_summary(message: Message, command: CommandObject):
    month = command.args

    if not month:
        await message.answer("📅 Укажи месяц в формате: <code>/month_summary ММ.ГГ</code>", parse_mode="HTML")
        return

    try:
        datetime.datetime.strptime(month, "%m.%y")
    except ValueError:
        await message.answer("❗Неверный формат месяца. Пример: <code>/month_summary ММ.ГГ</code>", parse_mode="HTML")
        return
    
    sales, amount = get_month_summary(month)
    await message.answer(f"🧾 Отчёт за {month}\nПродаж: {sales}\nСумма: {amount}₽")

@router.message(Command("year_summary"))
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
