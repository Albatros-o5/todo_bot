from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup,  CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from datetime import datetime
from database.repository import TaskRepository
from keyboard.reply_keyboard import reply_keyboard

router = Router()


class Form(StatesGroup):
    task = State()
    description = State()
    deadline = State()
    priority = State()


class UpdateForm(StatesGroup):
    task = State()
    description = State()
    deadline = State()
    priority = State()


@router.message(Command(commands=["add"]))
@router.message(F.text == "🛒 Add Task")
async def start(message: Message, state: FSMContext):
    await message.answer("Please enter the task name:")
    await state.set_state(Form.task)


@router.message(Command("cancel"))
@router.message(F.text == "♻️ Cancel")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Operation canceled.",
        reply_markup=reply_keyboard()
    )


@router.message(Form.task)
async def add_task(message: Message, state: FSMContext):
    task_name = message.text.strip()

    if not task_name:
        await message.answer("Task name cannot be empty.")
        return

    if len(task_name) > 100:
        await message.answer("Task name must be less than 100 characters.")
        return

    await state.update_data(task=task_name)
    await state.set_state(Form.description)
    await message.answer("Please enter the task description:")


@router.message(Form.description)
async def add_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if not description:
        await message.answer("Description cannot be empty.")
        return

    if len(description) > 400:
        await message.answer("Description must be less than 400 characters.")
        return

    await state.update_data(description=description)
    await state.set_state(Form.deadline)

    await message.answer(
        "📅 Enter deadline.\n\n"
        "Format:\n"
        "<code>YYYY-MM-DD HH:MM</code>\n\n"
        "Example:\n"
        "<code>2026-12-31 18:30</code>",
        parse_mode="HTML"
    )


@router.message(Form.deadline)
async def add_deadline(message: Message, state: FSMContext):
    try:
        deadline = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(
            "❌ Invalid date format.\n\n"
            "Please use the format: YYYY-MM-DD HH:MM\n\n"
            "Example:\n"
            "<code>2026-09-16 22:00</code>",
            parse_mode="HTML")
        return

    await state.update_data(deadline=deadline)
    await state.set_state(Form.priority)
    await message.answer("Please enter the task priority :", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟢Low", callback_data="low"),
                InlineKeyboardButton(text="🟡Medium", callback_data="medium"),
                InlineKeyboardButton(text="🔴High", callback_data="high"),
            ]
        ]
    ))


@router.callback_query(Form.priority)
async def add_priority(callback: CallbackQuery, state: FSMContext):

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    priority = callback.data

    await state.update_data(priority=priority)

    data = await state.get_data()

    db = TaskRepository()

    db.add_task(
        user_id=callback.from_user.id,
        task=data["task"],
        description=data["description"],
        deadline=data["deadline"],
        priority=data["priority"]
    )

    await callback.message.answer(
        f"""
📌 Task: {data['task']}
📝 Description: {data['description']}
📅 Deadline: {data['deadline']}
🔥 Priority: {data['priority']}

✅ Task saved.
"""
    )

    await state.clear()


@router.message(Command("list"))
@router.message(F.text == "📋 List Tasks")
async def list_tasks(message: Message):
    db = TaskRepository()
    tasks = db.show_tasks(user_id=message.from_user.id)
    if not tasks:
        await message.answer("List of your tasks is empty😪")
        return
    text = "🖥️ Your Tasks:\n\n"
    for task in tasks:
        status = "✅ Done" if task.status else "❌ Not Done"
        text += (
            f"📌 Task: {task.task}\n"
            f"📝 Description: {task.description}\n"
            f"📅 Deadline: {task.deadline}\n"
            f"🔥 Priority: {task.priority}\n"
            f"📊 Status: {status}\n\n"
        )
    await message.answer(text)


@router.message(Command("done"))
@router.message(F.text == "✅ Done Task")
async def done_task(message: Message):
    db = TaskRepository()
    tasks = db.all_tasks(message.from_user.id)
    if not tasks:
        await message.answer("List of your tasks is empty😪")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{task.task} (ID: {task.id})", callback_data=f"done_{task.id}")]
            for task in tasks if not task.status
        ]
    )

    if not keyboard.inline_keyboard:
        await message.answer("All your tasks are already marked as done! 🎉")
        return

    await message.answer("Select a task to mark as done:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("done_"))
async def mark_task_done(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    db = TaskRepository()
    success = db.done_task(task_id=task_id, user_id=callback.from_user.id)
    if success:
        await callback.answer("Task marked as done! ✅")
        await callback.message.answer("Task marked as done successfully! ✅")
        await callback.message.edit_reply_markup(reply_markup=None)
    else:
        await callback.answer("Task not found or already marked as done. ❌")


@router.message(Command("delete"))
@router.message(F.text == "❌ Delete Task")
async def delete_task(message: Message):
    db = TaskRepository()
    tasks = db.show_tasks(message.from_user.id)
    if not tasks:
        await message.answer("List of your tasks is empty😪")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{task.task} (ID: {task.id})", callback_data=f"delete_{task.id}")]
            for task in tasks
        ]
    )

    await message.answer("Select a task to delete:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_selected_task(callback: CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    db = TaskRepository()
    success = db.delete_task(task_id=task_id, user_id=callback.from_user.id)
    if success:
        await callback.answer("Task deleted! ✅")
        await callback.message.answer("Task deleted successfully! ✅")
        await callback.message.edit_reply_markup(reply_markup=None)
    else:
        await callback.answer("Task not found. ❌")

        await callback.message.edit_reply_markup(reply_markup=None)


@router.message(Command("update"))
@router.message(F.text == "📝 Update Task")
async def update_task(message: Message):
    db = TaskRepository()
    tasks = db.show_tasks(message.from_user.id)
    if not tasks:
        await message.answer("List of your tasks is empty😪")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{task.task} (ID: {task.id})", callback_data=f"update_{task.id}")]
            for task in tasks
        ]
    )

    await message.answer("Select a task to update:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("update_"))
async def update_selected_task(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])
    db = TaskRepository()
    task = db.get_task(task_id=task_id, user_id=callback.from_user.id)
    if not task:
        await callback.answer("Task not found. ❌")
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(task_id=task_id)
    await state.set_state(UpdateForm.task)
    await callback.message.answer(
        f"Current task: {task.task}\n\n"
        "Please enter the new task name:"
    )


@router.message(UpdateForm.task)
async def update_task_name(message: Message, state: FSMContext):
    task_name = message.text.strip()

    if not task_name:
        await message.answer("Task name cannot be empty.")
        return

    if len(task_name) > 100:
        await message.answer("Task name must be less than 100 characters.")
        return
    await state.update_data(task=task_name)
    await state.set_state(UpdateForm.description)
    await message.answer("Please enter the new task description:")


@router.message(UpdateForm.description)
async def update_task_description(message: Message, state: FSMContext):
    description = message.text
    description = message.text.strip()

    if not description:
        await message.answer("Description cannot be empty.")
        return

    if len(description) > 400:
        await message.answer("Description must be less than 400 characters.")
        return
    await state.update_data(description=description)
    await state.set_state(UpdateForm.deadline)
    await message.answer(
        "📅 Enter new deadline.\n\n"
        "Format:\n"
        "<code>YYYY-MM-DD HH:MM</code>\n\n"
        "Example:\n"
        "<code>2026-12-31 18:30</code>",
        parse_mode="HTML"
    )


@router.message(UpdateForm.deadline)
async def update_task_deadline(message: Message, state: FSMContext):
    try:
        deadline = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer(
            "❌ Invalid date format.\n\n"
            "Please use the format: YYYY-MM-DD HH:MM\n\n"
            "Example:\n"
            "<code>2026-09-16 22:00</code>",
            parse_mode="HTML")
        return

    await state.update_data(deadline=deadline)
    await state.set_state(UpdateForm.priority)
    await message.answer("Please enter the new task priority :", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟢Low", callback_data="low"),
                InlineKeyboardButton(text="🟡Medium", callback_data="medium"),
                InlineKeyboardButton(text="🔴High", callback_data="high"),
            ]
        ]
    ))


@router.callback_query(UpdateForm.priority)
async def update_task_priority(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    priority = callback.data

    await state.update_data(priority=priority)

    data = await state.get_data()

    db = TaskRepository()

    db.update_task(
        task_id=data["task_id"],
        user_id=callback.from_user.id,
        task=data["task"],
        description=data["description"],
        deadline=data["deadline"],
        priority=data["priority"]
    )
    await state.clear()
    await callback.message.answer(
        f"""
✅ Task updated successfully!

📌 {data['task']}
📝 {data['description']}
📅 {data['deadline']}
🔥 {data['priority']}
"""
    )


@router.message(Command("drop"))
@router.message(F.text == "🗑️ Drop All Tasks")
async def drop_tasks(message: Message):
    db = TaskRepository()
    tasks = db.show_tasks(message.from_user.id)

    if not tasks:
        await message.answer("List of your tasks is empty😪")
        return

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Yes, drop all tasks", callback_data="drop_yes"),
                InlineKeyboardButton(
                    text="No, cancel", callback_data="drop_no")
            ]
        ]
    )
    await message.answer("Are you sure you want to drop all your tasks? You can't return your tasks once dropped.", reply_markup=reply_markup)


@router.callback_query(lambda c: c.data.startswith("drop_yes"))
async def confirm_drop_tasks(callback: CallbackQuery):
    await callback.answer()
    db = TaskRepository()
    db.drop_tasks(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ All tasks have been dropped.")


@router.callback_query(lambda c: c.data.startswith("drop_no"))
async def cancel_drop_tasks(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("❌ Drop operation canceled.")


@router.message(Command("stats"))
@router.message(F.text == "📊 Statistics")
async def stats(message: Message):
    db = TaskRepository()
    tasks = db.show_tasks(message.from_user.id)
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task.status])
    pending_tasks = total_tasks - completed_tasks

    await message.answer(
        f"📊 Your Task Statistics:\n\n"
        f"Total Tasks: {total_tasks}\n"
        f"Completed Tasks: {completed_tasks}\n"
        f"Pending Tasks: {pending_tasks}"
    )


@router.message(F.photo)
@router.message(F.video)
@router.message(F.document)
@router.message(F.sticker)
@router.message(F.voice)
async def unsupported_content(message: Message):
    await message.answer(
        "❌ This content type is not supported.\n\n"
        "Use the menu below or type /help."
    )
