from aiogram.types import WebAppInfo
from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    WebAppInfo
)
from aiogram.filters import Command

from keyboard.reply_keyboard import reply_keyboard

import asyncio

router = Router()
WEBAPP_URL = "https://romantic-insight-production-100b.up.railway.app"

print("WEBAPP_URL =", repr(WEBAPP_URL))
start_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌐 Dashboard",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                text="🆔 My User ID",
                callback_data="my_id"
            )
        ]
    ]
)


@router.message(Command("start"))
async def start_command(message: Message):

    await message.answer(
        "👋 <b>Welcome!</b>\n\n"

        "🦤 <b>Todo List Bot</b>\n\n"

        "Your personal assistant for organizing daily tasks.\n\n"

        "📌 Plan your work\n"
        "⏰ Never miss a deadline\n"
        "🔥 Set task priorities\n"
        "📈 Track your progress\n\n"

        "🌐 You can also manage your tasks using the Web Dashboard.\n\n"

        "Choose an option below.",
        parse_mode="HTML",
        reply_markup=reply_keyboard()
    )

    await message.answer(
        "⚡ Quick Actions",
        reply_markup=start_inline
    )


@router.callback_query(F.data == "my_id")
async def my_id(callback: CallbackQuery):

    msg = await callback.message.answer(
        f"🆔 <b>Your User ID</b>\n\n"
        f"<code>{callback.from_user.id}</code>\n\n"
        "⏳ This message will disappear in 30 seconds.",
        parse_mode="HTML"
    )

    await callback.answer()

    await asyncio.sleep(30)

    try:
        await msg.delete()
    except:
        pass


@router.message(Command("about"))
@router.message(F.text == "ℹ️ About")
async def about_command(message: Message):

    await message.answer(
        "🦤 <b>Todo List Bot</b>\n\n"

        "Manage your daily tasks with ease.\n\n"

        "✔ Create tasks\n"
        "✔ Edit tasks\n"
        "✔ Delete tasks\n"
        "✔ Set priorities\n"
        "✔ Track deadlines\n"
        "✔ Access the Web Dashboard\n\n",
        parse_mode="HTML"
    )

print(repr(WEBAPP_URL))
