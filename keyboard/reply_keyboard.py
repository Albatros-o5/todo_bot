from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)

WEBAPP_URL = "https://todobot-production-ee27.up.railway.app"


def reply_keyboard():

    keyboard = ReplyKeyboardMarkup(

        keyboard=[

            [
                KeyboardButton(
                    text="🌐 Dashboard",
                    web_app=WebAppInfo(
                        url=WEBAPP_URL
                    )
                )
            ],

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
        input_field_placeholder="Choose an option..."

    )

    return keyboard
