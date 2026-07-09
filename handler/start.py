from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboard.reply_keyboard import reply_keyboard


router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "👋 Welcome!\n\n"

        "I'm Todo List Bot 🦤\n"
        "Your personal assistant for organizing daily tasks.\n\n"

        "📌 Plan your work\n"
        "⏰ Never miss a deadline\n"
        "🔥 Set task priorities\n"
        "📈 Monitor your progress\n\n"

        "Choose an option from the keyboard below or type /help to get started.\n\n"

        "Stay focused. Stay productive.🚀",
        reply_markup=reply_keyboard()
    )


@router.message(Command("about"))
@router.message(F.text == "ℹ️ About")
async def about_command(message: Message):
    await message.answer("🦤 Todo List Bot\n\nManage your daily tasks with ease. Create, update, complete, and organize your to-do list while tracking deadlines and priorities in one place.\n\nTech Stack: Python • Aiogram 3 • SQLAlchemy • SQLite")
