from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL and make_url(DATABASE_URL).drivername == "postgresql":
    DATABASE_URL = make_url(DATABASE_URL).set(
        drivername="postgresql+psycopg2"
    ).render_as_string(hide_password=False)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()