import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leasehackr.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    import app.models  # noqa: F401 — ensures all models are registered
    Base.metadata.create_all(bind=engine)
    _migrate_add_column("lease_programs", "base_msrp", "REAL")
    _migrate_add_column("lease_programs", "costco_cash", "REAL")
    _migrate_add_column("lease_programs", "military_cash", "REAL")
    _migrate_add_column("lease_programs", "college_cash", "REAL")


def _migrate_add_column(table: str, column: str, col_type: str) -> None:
    """Non-destructive: adds a column if it doesn't already exist (SQLite safe)."""
    import sqlalchemy.exc
    with engine.connect() as conn:
        try:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
            conn.commit()
        except sqlalchemy.exc.OperationalError:
            pass  # column already present
