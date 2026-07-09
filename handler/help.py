from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command


router = Router()


@router.message(Command("help"))
@router.message(F.text == "❓ Help")
async def help_command(message: Message):
    await message.answer(
        "📚 <b>Todo List Bot — Help</b>\n\n"
        "Use the following commands to manage your tasks efficiently:\n\n"

        "➕ <b>/add</b> — Create a new task\n"
        "📋 <b>/list</b> — View all your tasks\n"
        "✅ <b>/done</b> — Mark a task as completed\n"
        "✏️ <b>/update</b> — Edit an existing task\n"
        "🗑 <b>/delete</b> — Remove a selected task\n"
        "💥 <b>/drop</b> — Delete all tasks\n"
        "📊 <b>/stats</b> — View task statistics\n"
        "❌ <b>/cancel</b> — Cancel the current operation\n"
        "ℹ️ <b>/about</b> — Information about the bot\n\n"

        "💡 <i>You can also use the buttons below the chat for quick access to all features.</i>",
        parse_mode="HTML"
    )
