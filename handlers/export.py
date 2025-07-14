from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from google_sheets import export_sheet_xlsx

import os

router = Router()

@router.message(Command("export"))
async def command_export(message: Message):
    await message.answer("📤 Экспортирую таблицу, подожди секунду...")

    file_path = export_sheet_xlsx()
    if file_path:
        document = FSInputFile(file_path, filename="SalesBot.xlsx")
        await message.answer_document(document=document, caption="🧾 Вот твоя таблица")
        os.remove(file_path)
    else:
        await message.answer("⚠️ Не удалось экспортировать таблицу. Попробуй позже.")

