from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///todo.db", echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_session():
    return SessionLocal()
