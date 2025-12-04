"""
Database initialization and session management.
Handles database connection, table creation, and session lifecycle.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from config import Config
from models import Base

# Create database engine
engine = create_engine(Config.DATABASE_URL, echo=False)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    """
    Initialize the database by creating all tables.
    This function should be called when setting up the application for the first time.
    """
    Base.metadata.create_all(engine)
    print("Database initialized successfully!")


def drop_db():
    """
    Drop all tables from the database.
    WARNING: This will delete all data!
    """
    Base.metadata.drop_all(engine)
    print("Database tables dropped!")


@contextmanager
def get_session():
    """
    Context manager for database sessions.
    Ensures proper session handling with automatic commit/rollback.
    
    Usage:
        with get_session() as session:
            # perform database operations
            session.add(obj)
    
    Yields:
        Session: SQLAlchemy session object
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
