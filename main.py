import os
import json
import time
import hmac
import hashlib

from urllib.parse import parse_qsl, unquote
from datetime import datetime

from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import JSONResponse, RedirectResponse
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
    raise RuntimeError("BOT_TOKEN topilmadi")


def verify_init_data(init_data: str):

    parsed = dict(
        parse_qsl(
            unquote(init_data),
            keep_blank_values=True
        )
    )

    received_hash = parsed.pop("hash", None)

    if not received_hash:
        raise ValueError("Hash topilmadi")

    data_check_string = "\n".join(
        f"{k}={v}"
        for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(
        calculated_hash,
        received_hash
    ):
        raise ValueError("initData noto'g'ri")

    auth_date = int(parsed["auth_date"])

    if time.time() - auth_date > 86400:
        raise ValueError("Session eskirgan")

    user = json.loads(parsed["user"])

    return user


def get_user_id(
    request: Request,
    init_data: str = None
):

    cookie = request.cookies.get("user_id")

    if cookie:
        return int(cookie)

    if init_data:

        user = verify_init_data(init_data)

        return int(user["id"])

    return None


@app.get("/")
async def home(request: Request):

    if request.cookies.get("user_id"):
        return RedirectResponse(
            "/tasks",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


@app.post("/auth")
async def auth(body: dict = Body(...)):

    init_data = body.get("init_data")

    if not init_data:

        return JSONResponse(
            {
                "ok": False,
                "detail": "initData mavjud emas"
            },
            status_code=400
        )

    try:

        user = verify_init_data(init_data)

    except Exception as e:

        return JSONResponse(
            {
                "ok": False,
                "detail": str(e)
            },
            status_code=401
        )

    response = JSONResponse(
        {
            "ok": True
        }
    )

    response.set_cookie(
        key="user_id",
        value=str(user["id"]),
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 30
    )

    return response


@app.get("/tasks")
async def tasks_page(
    request: Request,
    init_data: str = None
):

    user_id = get_user_id(
        request,
        init_data
    )

    if not user_id:

        return RedirectResponse(
            "/",
            status_code=303
        )

    tasks = db.show_tasks(user_id)

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
            "user_id": user_id
        }
    )


@app.post("/add")
async def add_task(
    request: Request,
    task: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(...),
    priority: str = Form(...),
    init_data: str = Form(None)
):

    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse("/", status_code=303)

    task = task.strip()
    description = description.strip()

    if len(task) < 3:

        tasks = db.show_tasks(user_id)

        return templates.TemplateResponse(
            request=request,
            name="tasks.html",
            context={
                "tasks": tasks,
                "user_id": user_id,
                "error": "Task must contain at least 3 characters."
            }
        )

    try:
        deadline = datetime.strptime(
            deadline,
            "%Y-%m-%d %H:%M"
        )

    except ValueError:

        tasks = db.show_tasks(user_id)

        return templates.TemplateResponse(
            request=request,
            name="tasks.html",
            context={
                "tasks": tasks,
                "user_id": user_id,
                "error": "Wrong date format."
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
                "error": "Deadline cannot be in the past."
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
        "/tasks",
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
        return RedirectResponse("/", status_code=303)

    db.delete_task(
        task_id,
        user_id
    )

    return RedirectResponse(
        "/tasks",
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
        return RedirectResponse("/", status_code=303)

    db.done_task(
        task_id,
        user_id
    )

    return RedirectResponse(
        "/tasks",
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
        return RedirectResponse("/", status_code=303)

    db.undone_task(
        task_id,
        user_id
    )

    return RedirectResponse(
        "/tasks",
        status_code=303
    )


@app.post("/edit")
async def edit_page(
    request: Request,
    task_id: int = Form(...),
    init_data: str = Form(None)
):

    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse("/", status_code=303)

    task = db.get_task(
        task_id,
        user_id
    )

    if not task:
        return RedirectResponse(
            "/tasks",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={
            "task": task,
            "user_id": user_id
        }
    )


@app.post("/update")
async def update_task(
    request: Request,
    task_id: int = Form(...),
    task: str = Form(...),
    description: str = Form(""),
    deadline: str = Form(...),
    priority: str = Form(...),
    init_data: str = Form(None)
):

    user_id = get_user_id(request, init_data)

    if not user_id:
        return RedirectResponse(
            "/",
            status_code=303
        )

    task = task.strip()
    description = description.strip()

    current_task = db.get_task(
        task_id=task_id,
        user_id=user_id
    )

    if not current_task:
        return RedirectResponse(
            "/tasks",
            status_code=303
        )

    if len(task) < 3:
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": user_id,
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
                "error": "Invalid priority selected."
            }
        )

    try:
        deadline = datetime.strptime(
            deadline,
            "%Y-%m-%d %H:%M"
        )

    except ValueError:
        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": user_id,
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
                "error": "The deadline cannot be in the past."
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
        "/tasks",
        status_code=303
    )
