import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Default to local SQLite if DATABASE_URL isn't found in .env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

# Senior Move: Handle engine arguments conditionally based on DB type
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL doesn't need or support check_same_thread
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

Base.metadata.create_all(bind=engine) # Create tables based on models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
