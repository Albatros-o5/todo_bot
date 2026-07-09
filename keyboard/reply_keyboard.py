from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛒 Add Task"),
                KeyboardButton(text="📋 List Tasks")
            ],
            [
                KeyboardButton(text="✅ Done Task"),
                KeyboardButton(text="📝 Update Task")
            ],
            [
                KeyboardButton(text="❌ Delete Task"),
                KeyboardButton(text="🗑️ Drop All Tasks")
            ],
            [
                KeyboardButton(text="📊 Statistics"),
                KeyboardButton(text="♻️ Cancel")
            ],
            [
                KeyboardButton(text="❓ Help"),
                KeyboardButton(text="ℹ️ About")
            ]
        ],
        resize_keyboard=True,
    )
    return keyboard
