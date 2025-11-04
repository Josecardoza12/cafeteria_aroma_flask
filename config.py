import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-super-secreta-123")

    # Obtener URL de la base de datos desde Render
    uri = os.environ.get("DATABASE_URL")

    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql+psycopg2://", 1)

    # Forzar sslmode=require si no existe
    if uri and "sslmode" not in uri:
        uri = uri + ("&sslmode=require" if "?" in uri else "?sslmode=require")

    SQLALCHEMY_DATABASE_URI = uri or f"sqlite:///{BASE_DIR / 'app.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
