import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Load environment variables from .env
load_dotenv()

# 2. Extract individual database components from your .env
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME")

# 3. Construct the PostgreSQL connection URL dynamically
if all([db_user, db_password, db_host, db_name]):
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
else:
    # Fallback to checking for a single flat URL if provided
    DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "Database configuration variables are missing from your .env file. "
        "Please check your DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME configurations."
    )

# 4. Create the SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# 5. Create a Session Local class for transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 6. Create the declarative Base class for database models
Base = declarative_base()

# 7. FastAPI Dependency injection for database sessions
def get_db():
    """
    Yields a database session instance per API request and safely closes it when finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("[SYSTEM] PostgreSQL Database config initialized successfully via environment variables.")