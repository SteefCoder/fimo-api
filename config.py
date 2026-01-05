import os

from dotenv import load_dotenv

load_dotenv()

KEY = os.environ.get("SECRET_KEY")
assert KEY is not None

class Config:
    SECRET_KEY = KEY
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
