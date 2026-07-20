from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_inline_keyboard():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌐 Open Web Dashboard",
                    url="https://todobot-production-ee27.up.railway.app"
                )
            ]
        ]
    )

    return keyboard
