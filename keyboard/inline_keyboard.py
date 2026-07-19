from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_inline_keyboard():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌐 Open Web Dashboard",
                    url="https://YOUR-DOMAIN.com"
                )
            ]
        ]
    )

    return keyboard
