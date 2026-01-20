"""
Database Connection and Session Management
SQLModel database setup for Neon PostgreSQL
"""

from sqlmodel import SQLModel, create_engine, Session
from config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """
    Dependency function to get database session
    """
    with Session(engine) as session:
        yield session


def init_db():
    """
    Initialize database tables
    """
    SQLModel.metadata.create_all(engine)
