from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from datetime import datetime

from database.repository import TaskRepository

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

db = TaskRepository()


# HOME


@app.get("/")
async def home(request: Request):

    user_id = request.cookies.get("user_id")

    if user_id:
        return RedirectResponse(
            url="/tasks",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


# LOGIN


@app.post("/login")
async def login(
    user_id: int = Form(...)
):

    response = RedirectResponse(
        url="/tasks",
        status_code=303
    )

    response.set_cookie(
        key="user_id",
        value=str(user_id),
        max_age=60 * 60 * 24 * 30
    )

    return response


# TASKS PAGE


@app.get("/tasks")
async def tasks_page(request: Request):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    tasks = db.show_tasks(int(user_id))

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
            "user_id": int(user_id)
        }
    )

# ==========================
# ADD TASK
# ==========================


@app.post("/add")
async def add_task(
    request: Request,
    task: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    priority: str = Form(...)
):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    # DEADLINE TEKSHIRISH

    try:

        deadline = datetime.strptime(
            deadline,
            "%Y-%m-%d %H:%M"
        )

    except ValueError:

        tasks = db.show_tasks(int(user_id))

        return templates.TemplateResponse(
            request=request,
            name="tasks.html",
            context={
                "tasks": tasks,
                "user_id": int(user_id),
                "error": "Please enter a valid date format. Example: 2026-07-18 15:30."}
        )

    if deadline < datetime.now():

        tasks = db.show_tasks(int(user_id))

        return templates.TemplateResponse(
            request=request,
            name="tasks.html",
            context={
                "tasks": tasks,
                "user_id": int(user_id),
                "error": "The deadline cannot be in the past. Please select a future date and time."
            }
        )

    # DATABASEGA SAQLASH

    db.add_task(
        user_id=int(user_id),
        task=task,
        description=description,
        deadline=deadline,
        priority=priority
    )

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )


# DELETE TASK


@app.post("/delete")
async def delete_task(
    request: Request,
    task_id: int = Form(...)
):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    db.delete_task(
        task_id=task_id,
        user_id=int(user_id)
    )

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )


# DONE TASK


@app.post("/done")
async def done_task(
    request: Request,
    task_id: int = Form(...)
):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    db.done_task(
        task_id=task_id,
        user_id=int(user_id)
    )

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )

# UNDONE TASK


@app.post("/undone")
async def undone_task(
    request: Request,
    task_id: int = Form(...)
):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    db.undone_task(
        task_id=task_id,
        user_id=int(user_id)
    )

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )


@app.post("/edit")
async def edit(
    request: Request,
    task_id: int = Form(...)
):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    task = db.get_task(
        task_id=task_id,
        user_id=int(user_id)
    )

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={
            "task": task,
            "user_id": int(user_id)
        }
    )

# UPDATE TASK


@app.post("/update")
async def update_task(
    request: Request,
    task_id: int = Form(...),
    task: str = Form(...),
    description: str = Form(...),
    deadline: str = Form(...),
    priority: str = Form(...)
):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/",
            status_code=303
        )

    task = task.strip()
    description = description.strip()

    current_task = db.get_task(
        task_id=task_id,
        user_id=int(user_id)
    )

    # TASK LENGTH

    if len(task) < 3:

        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": int(user_id),
                "error": "Task must contain at least 3 characters."
            }
        )

    # DESCRIPTION LENGTH

    if len(description) > 200:

        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": int(user_id),
                "error": "Description cannot exceed 200 characters."
            }
        )

    # PRIORITY

    if priority not in ["Low", "Medium", "High"]:

        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": int(user_id),
                "error": "Invalid priority selected."
            }
        )

    # DEADLINE FORMAT

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
                "user_id": int(user_id),
                "error": "Please enter a valid date format. Example: 2026-07-18 15:30."
            }
        )

    # DEADLINE CHECK

    if deadline < datetime.now():

        return templates.TemplateResponse(
            request=request,
            name="edit.html",
            context={
                "task": current_task,
                "user_id": int(user_id),
                "error": "The deadline cannot be in the past. Please select a future date and time."
            }
        )

    # UPDATE DATABASE

    db.update_task(
        task_id=task_id,
        user_id=int(user_id),
        task=task,
        description=description,
        deadline=deadline,
        priority=priority
    )

    return RedirectResponse(
        url="/tasks",
        status_code=303
    )


@app.get("/logout")
async def logout():

    response = RedirectResponse(
        url="/",
        status_code=303
    )

    response.delete_cookie("user_id")

    return response
