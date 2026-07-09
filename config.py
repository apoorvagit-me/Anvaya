import os


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "anvaya_secret_key")

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql://",
            1
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or "sqlite:///database.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False