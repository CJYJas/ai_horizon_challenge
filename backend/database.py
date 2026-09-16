import os
from sqlmodel import SQLModel, create_engine, Session

# SQLite Database
DATABASE_URL = "sqlite:///./assessment_v2.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
