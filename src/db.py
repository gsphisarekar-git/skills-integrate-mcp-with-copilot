from sqlmodel import create_engine, SQLModel

# SQLite for development; file stored next to the project
DATABASE_URL = "sqlite:///./activities.db"

# Required for SQLite to allow access from multiple threads used by uvicorn
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)


def get_engine():
    return engine
