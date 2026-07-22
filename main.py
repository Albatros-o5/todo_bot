import hmac
import hashlib
import json
import time
import os

from urllib.parse import unquote, parse_qsl
from datetime import datetime

from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database.repository import TaskRepository


app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

db = TaskRepository()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable o'rnatilmagan!")


def verify_init_data(init_data: str) -> dict:
    """
    Telegram WebApp initData ni HMAC-SHA256 bilan tekshiradi.
    To'g'ri bo'lsa user dict qaytaradi, xato bo'lsa ValueError.
    """
    parsed = dict(parse_qsl(unquote(init_data), keep_blank_values=True))

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise ValueError("Hash topilmadi")

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise ValueError("initData yaroqsiz yoki buzilgan")

    auth_date = int(parsed.get("auth_date", 0))
    if time.time() - auth_date > 86400:
        raise ValueError("initData muddati o'tgan")

    user_json = parsed.get("user")
    if not user_json:
        raise ValueError("User ma'lumoti topilmadi")

    return json.loads(user_json)


def get_user_id(request: Request, init_data: str = None) -> int | None:
    """
    Avval cookie dan oladi.
    Cookie bo'lmasa initData ni verify qilib user_id oladi.
    """
    cookie_user_id = request.cookies.get("user_id")
    if cookie_user_id:
        return int(cookie_user_id)

    if init_data:
        try:
            tg_user = verify_init_data(init_data)
            return int(tg_user["id"])
        except Exception:
            return None

    return None


# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@app.get("/")
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.get("/tasks")
async def tasks_page(request: Request, init_data: str = None):
    """
    Cookie yoki initData (query param) dan user_id oladi.
    """
    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    tasks = db.show_tasks(user_id)

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
            "user_id": user_id,
            "init_data": init_data or ""
        }
    )


@app.post("/add")
async def add_task(
    request: Request,
    task: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    priority: str = Form(...),
    init_data: str = Form(None)
):
    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    try:
        deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
    except ValueError:
        tasks = db.show_tasks(user_id)
        return templates.TemplateResponse(
            request=request,
            name="tasks.html",
            context={
                "tasks": tasks,
                "user_id": user_id,
                "init_data": init_data or "",
                "error": "Please enter a valid date format. Example: 2026-07-18 15:30."
            }
        )

    if deadline < datetime.now():
        tasks = db.show_tasks(user_id)
        return templates.TemplateResponse(
            request=request,
            name="tasks.html",
            context={
                "tasks": tasks,
                "user_id": user_id,
                "init_data": init_data or "",
                "error": "The deadline cannot be in the past. Please select a future date and time."
            }
        )

    db.add_task(
        user_id=user_id,
        task=task,
        description=description,
        deadline=deadline,
        priority=priority
    )

    return RedirectResponse(
        url=f"/tasks?init_data={init_data}" if init_data else "/tasks",
        status_code=303
    )


@app.post("/delete")
async def delete_task(
    request: Request,
    task_id: int = Form(...),
    init_data: str = Form(None)
):
    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    db.delete_task(task_id=task_id, user_id=user_id)

    return RedirectResponse(
        url=f"/tasks?init_data={init_data}" if init_data else "/tasks",
        status_code=303
    )


@app.post("/done")
async def done_task(
    request: Request,
    task_id: int = Form(...),
    init_data: str = Form(None)
):
    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    db.done_task(task_id=task_id, user_id=user_id)

    return RedirectResponse(
        url=f"/tasks?init_data={init_data}" if init_data else "/tasks",
        status_code=303
    )


@app.post("/undone")
async def undone_task(
    request: Request,
    task_id: int = Form(...),
    init_data: str = Form(None)
):
    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    db.undone_task(task_id=task_id, user_id=user_id)

    return RedirectResponse(
        url=f"/tasks?init_data={init_data}" if init_data else "/tasks",
        status_code=303
    )


@app.post("/edit")
async def edit(
    request: Request,
    task_id: int = Form(...),
    init_data: str = Form(None)
):
    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    task = db.get_task(task_id=task_id, user_id=user_id)

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={
            "task": task,
            "user_id": user_id,
            "init_data": init_data or ""
        }
    )


@app.post("/update")
async def update_task(
    request: Request,
    task_id: int = Form(...),
    task: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    priority: str = Form(...),
    init_data: str = Form(None)
):
    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    task = task.strip()
    description = description.strip()

    current_task = db.get_task(task_id=task_id, user_id=user_id)

    if len(task) < 3:
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": user_id,
                "init_data": init_data or "",
                "error": "Task must contain at least 3 characters."
            }
        )

    if len(description) > 200:
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": user_id,
                "init_data": init_data or "",
                "error": "Description cannot exceed 200 characters."
            }
        )

    if priority not in ["Low", "Medium", "High"]:
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": user_id,
                "init_data": init_data or "",
                "error": "Invalid priority selected."
            }
        )

    try:
        deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
    except ValueError:
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": user_id,
                "init_data": init_data or "",
                "error": "Please enter a valid date format. Example: 2026-07-18 15:30."
            }
        )

    if deadline < datetime.now():
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": user_id,
                "init_data": init_data or "",
                "error": "The deadline cannot be in the past. Please select a future date and time."
            }
        )

    db.update_task(
        task_id=task_id,
        user_id=user_id,
        task=task,
        description=description,
        deadline=deadline,
        priority=priority
    )

    return RedirectResponse(
        url=f"/tasks?init_data={init_data}" if init_data else "/tasks",
        status_code=303
    )
