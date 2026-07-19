from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    task = Column(String(100))
    description = Column(String(400))
    deadline = Column(DateTime)
    priority = Column(String)
    status = Column(Boolean, default=False)
