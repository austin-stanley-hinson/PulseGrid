import os 

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine 

# Load environment variables before reading DATABASE_URL.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set. Add it to backend/.env")

# Shared SQLModel engine used across request sessions.
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    # Creates tables for all imported SQLModel models.
    SQLModel.metadata.create_all(engine)

def get_session():
    # Dependency that yields one DB session per request.
    with Session(engine) as session:
        yield session