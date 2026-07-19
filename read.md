# 🦤 Todo List Bot

A Telegram Todo List Bot built with **Python**, **Aiogram 3**, **SQLAlchemy**, and **SQLite**.

This project allows users to manage their daily tasks efficiently by creating, updating, completing, and deleting tasks through a Telegram bot interface.

---

## ✨ Features

- ➕ Add new tasks
- 📋 View all tasks
- ✅ Mark tasks as completed
- ✏️ Update existing tasks
- ❌ Delete individual tasks
- 🗑️ Delete all tasks
- 📊 View task statistics
- ♻️ Cancel current operation
- 🔥 Set task priorities
- 📅 Set task deadlines

---

## 🛠️ Tech Stack

- Python 3
- Aiogram 3
- SQLAlchemy
- SQLite
- FSM (Finite State Machine)

---

## 📁 Project Structure

```
todo_list_bot/
│
├── database/
│   ├── db.py
│   ├── models.py
│   └── repository.py
│
├── handler/
│   ├── start.py
│   ├── help.py
│   ├── stats.py
│   └── task.py
│
├── keyboard/
│   └── reply_keyboard.py
│
├── app.py
├── requirements.txt
└── README.md
```


## 📚 Commands

| Command | Description |
|---------|-------------|
| /start | Start the bot |
| /add | Add a new task |
| /list | View all tasks |
| /done | Mark a task as completed |
| /update | Update a task |
| /delete | Delete a task |
| /drop | Delete all tasks |
| /stats | Show task statistics |
| /cancel | Cancel current operation |
| /help | Show help |
| /about | About the project |

---

## 📌 Technologies Used

- Repository Pattern
- Finite State Machine (FSM)
- Inline Keyboard
- Reply Keyboard
- Callback Queries
- SQLAlchemy ORM
- SQLite Database

---

## 👨‍💻 Author

Muhammadjon

GitHub:
https://github.com/Albatros-o5