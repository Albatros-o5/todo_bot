from sqlalchemy import select
from database.db import get_session
from database.models import Task


class TaskRepository:

    def __init__(self):
        self.session = get_session()

    def add_task(self, user_id, task, description, deadline, priority):
        new_task = Task(
            user_id=user_id,
            task=task,
            description=description,
            deadline=deadline,
            priority=priority,
            status=False
        )
        self.session.add(new_task)
        self.session.commit()
        return new_task

    def show_tasks(self, user_id):
        tasks = self.session.execute(select(Task).where(
            Task.user_id == user_id)).scalars().all()
        return tasks

    def get_task(self, task_id, user_id):
        task = self.session.execute(select(Task).where(
            Task.id == task_id, Task.user_id == user_id)).scalar()
        return task

    def delete_task(self, task_id, user_id):
        task = self.get_task(task_id, user_id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True

        return False

    def update_task(self, task_id, user_id, task, description, deadline, priority):
        task_to_update = self.get_task(task_id, user_id)
        if task_to_update:
            task_to_update.task = task
            task_to_update.description = description
            task_to_update.deadline = deadline
            task_to_update.priority = priority
            self.session.commit()

    def drop_tasks(self, user_id):
        tasks = self.session.execute(select(Task).where(
            Task.user_id == user_id)).scalars().all()
        for task in tasks:
            self.session.delete(task)
        self.session.commit()

    def done_task(self, task_id, user_id):
        task_to_mark_done = self.get_task(task_id, user_id)

        if task_to_mark_done:
            task_to_mark_done.status = True
            self.session.commit()
            return True

        return False

    def all_tasks(self, user_id):
        tasks = self.session.execute(select(Task).where(
            Task.user_id == user_id, Task.status == False)).scalars().all()
        return tasks
